import asyncio
from collections.abc import AsyncGenerator
from functools import cache
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException, Request, status
from redis.asyncio import Redis
from sse_starlette.sse import EventSourceResponse
from structlog.contextvars import bind_contextvars, clear_contextvars

from wallstr.auth.dependencies import Auth
from wallstr.auth.schemas import HTTPUnauthorizedError
from wallstr.auth.services import UserService
from wallstr.core.schemas import Paginated
from wallstr.core.utils import uvicorn_should_exit
from wallstr.documents.models import DocumentModel
from wallstr.documents.schemas import PendingDocument
from wallstr.documents.services import DocumentService
from wallstr.openapi import generate_unique_id_function

from .schemas import (
    Chat,
    ChatMessage,
    MessageRequest,
)
from .services import ChatService
from .tasks import process_chat_message

logger = structlog.get_logger()
router = APIRouter(
    prefix="/chats",
    tags=["chat"],
    generate_unique_id_function=generate_unique_id_function(2),
    responses={401: {"model": HTTPUnauthorizedError}},
)


@router.get("/{slug}")
async def get_chat(
    auth: Auth,
    chat_svc: Annotated[ChatService, Depends(ChatService.inject_svc)],
    slug: str,
) -> Chat:
    chat = await chat_svc.get_chat_by_slug(slug, auth.user_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    messages, new_cursor = await chat_svc.get_chat_messages(chat_id=chat.id)
    return Chat(
        id=chat.id,
        title=chat.title,
        slug=chat.slug,
        messages=Paginated(
            items=[ChatMessage.model_validate(message) for message in messages],
            cursor=new_cursor,
        ),
    )


@router.get("/{slug}/messages")
async def get_chat_messages(
    auth: Auth,
    chat_svc: Annotated[ChatService, Depends(ChatService.inject_svc)],
    slug: str,
    cursor: int = 0,
) -> Paginated[ChatMessage]:
    chat = await chat_svc.get_chat_by_slug(slug, auth.user_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    messages, new_cursor = await chat_svc.get_chat_messages(
        chat_id=chat.id, offset=cursor
    )
    return Paginated(
        items=[ChatMessage.model_validate(message) for message in messages],
        cursor=new_cursor,
    )


@router.post(
    "",
    response_model=Chat,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"description": "Invalid request"}},
)
async def create_chat(
    data: MessageRequest,
    auth: Auth,
    chat_svc: Annotated[ChatService, Depends(ChatService.inject_svc)],
    document_svc: Annotated[DocumentService, Depends(DocumentService.inject_svc)],
) -> Chat:
    if data.message is None and len(data.documents) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot send empty message",
        )
    chat, message = await chat_svc.create_chat(
        user_id=auth.user_id,
        message=data.message,
        documents=data.documents,
    )

    async def get_pending_document(document: DocumentModel) -> PendingDocument:
        return PendingDocument(
            id=document.id,
            filename=document.filename,
            presigned_url=document_svc.generate_upload_url(auth.user_id, document),
        )

    pending_documents = await asyncio.gather(
        *[get_pending_document(document) for document in message.documents]
    )

    return Chat(
        id=chat.id,
        title=chat.title,
        slug=chat.slug,
        messages=Paginated(
            items=[
                ChatMessage.model_validate(message).model_copy(
                    update={"pending_documents": pending_documents}
                )
            ],
            cursor=None,
        ),
    )


@router.post(
    "/{slug}/messages",
    response_model=ChatMessage,
    responses={
        400: {"description": "Invalid request"},
        404: {"description": "Chat not found"},
    },
)
async def send_chat_message(
    auth: Auth,
    data: MessageRequest,
    chat_svc: Annotated[ChatService, Depends(ChatService.inject_svc)],
    document_svc: Annotated[DocumentService, Depends(DocumentService.inject_svc)],
    slug: str,
) -> ChatMessage:
    if data.message is None and len(data.documents) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot send empty message",
        )

    chat = await chat_svc.get_chat_by_slug(slug, auth.user_id)
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found"
        )

    try:
        message = await chat_svc.create_chat_message(
            chat_id=chat.id,
            message=data.message,
            documents=data.documents,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found"
        ) from e

    async def get_pending_document(document: DocumentModel) -> PendingDocument:
        return PendingDocument(
            id=document.id,
            filename=document.filename,
            presigned_url=document_svc.generate_upload_url(auth.user_id, document),
        )

    pending_documents = await asyncio.gather(
        *[get_pending_document(document) for document in message.documents]
    )
    process_chat_message.send(message_id=str(message.id))
    return ChatMessage.model_validate(message).model_copy(
        update={"pending_documents": pending_documents}
    )


@cache
@router.get("/{slug}/messages/stream")
async def get_chat_messages_stream(
    request: Request,
    slug: str,
    chat_svc: Annotated[ChatService, Depends(ChatService.inject_svc)],
    user_svc: Annotated[UserService, Depends(UserService.inject_svc)],
) -> EventSourceResponse:
    redis: Redis = request.state.redis

    # TODO: refresh_token is used for authentincation, needs to introduce additional cookie based auth
    # for sse only
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )
    auth_session = await user_svc.get_session_by_token(refresh_token)
    if not auth_session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )

    chat = await chat_svc.get_chat_by_slug(slug, auth_session.user_id)
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found"
        )

    clear_contextvars()
    bind_contextvars(user_id=auth_session.user_id, chat_id=chat.id)

    async def generator() -> AsyncGenerator[str, None]:
        async with redis.pubsub() as pubsub:
            await pubsub.psubscribe(f"{auth_session.user_id}:{chat.id}:*")

            while not uvicorn_should_exit():
                if await request.is_disconnected():
                    await pubsub.close()
                    break

                try:
                    message = await pubsub.get_message(
                        ignore_subscribe_messages=True,
                        timeout=5.0,
                    )

                    if message is not None:
                        yield message["data"].decode("utf-8")
                except asyncio.CancelledError as e:
                    await pubsub.close()
                    raise e
                except ConnectionError as e:
                    await pubsub.close()
                    raise e

    return EventSourceResponse(generator())


@router.get("")
async def list_chats(
    auth: Auth,
    chat_svc: Annotated[ChatService, Depends(ChatService.inject_svc)],
    cursor: int = 0,
) -> Paginated[Chat]:
    chats, new_cursor = await chat_svc.get_user_chats(
        user_id=auth.user_id,
        offset=cursor,
    )
    return Paginated(
        items=[
            Chat(
                id=chat.id,
                title=chat.title,
                slug=chat.slug,
                messages=Paginated(items=[], cursor=None),
            )
            for chat in chats
        ],
        cursor=new_cursor,
    )
