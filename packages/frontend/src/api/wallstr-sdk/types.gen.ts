// This file is auto-generated by @hey-api/openapi-ts

export type AccessToken = {
  token: string;
  token_type?: string;
};

export type Chat = {
  id: string;
  slug: string;
  title: string | null;
  messages: PaginatedChatMessage;
};

export type ChatMessage = {
  id: string;
  role: ChatMessageRole;
  content: string;
  documents: Array<Document>;
};

export type ChatMessageRole = "user" | "assistant";

export type CreateChatResponse = {
  chat: Chat;
  pending_documents: Array<PendingDocument>;
};

export type Document = {
  id: string;
  filename: string;
  status: DocumentStatus;
};

export type DocumentPayload = {
  filename: string;
  doc_type: DocumentType;
};

export type DocumentStatus = "uploading" | "uploaded";

export type DocumentType = "pdf" | "doc" | "docx" | "xls" | "xlsx";

export type HttpUnauthorizedError = {
  detail: string;
};

export type HttpValidationError = {
  detail?: Array<ValidationError>;
};

export type MessageRequest = {
  message: string | null;
  documents: Array<DocumentPayload>;
};

export type PaginatedChatMessage = {
  items: Array<ChatMessage>;
  cursor: number | null;
};

export type PaginatedChat = {
  items: Array<Chat>;
  cursor: number | null;
};

export type PendingDocument = {
  id: string;
  filename: string;
  presigned_url: string;
};

export type SignInRequest = {
  email: string;
  password: string;
};

export type SignUpRequest = {
  email: string;
  password: string;
  username: string | null;
  fullname: string | null;
};

export type User = {
  id: string;
  email: string;
  username: string;
  fullname: string;
};

export type ValidationError = {
  loc: Array<string | number>;
  msg: string;
  type: string;
};

export type SignupData = {
  body: SignUpRequest;
  path?: never;
  query?: never;
  url: "/auth/signup";
};

export type SignupErrors = {
  /**
   * Validation Error
   */
  422: HttpValidationError;
};

export type SignupError = SignupErrors[keyof SignupErrors];

export type SignupResponses = {
  /**
   * Successful Response
   */
  201: User;
};

export type SignupResponse = SignupResponses[keyof SignupResponses];

export type SigninData = {
  body: SignInRequest;
  path?: never;
  query?: never;
  url: "/auth/signin";
};

export type SigninErrors = {
  /**
   * Unauthorized
   */
  401: HttpUnauthorizedError;
  /**
   * Validation Error
   */
  422: HttpValidationError;
};

export type SigninError = SigninErrors[keyof SigninErrors];

export type SigninResponses = {
  /**
   * Successful Response
   */
  200: AccessToken;
};

export type SigninResponse = SigninResponses[keyof SigninResponses];

export type RefreshTokenData = {
  body?: never;
  path?: never;
  query?: never;
  url: "/auth/refresh-token";
};

export type RefreshTokenResponses = {
  /**
   * Successful Response
   */
  200: AccessToken;
};

export type RefreshTokenResponse = RefreshTokenResponses[keyof RefreshTokenResponses];

export type SignoutData = {
  body?: never;
  path?: never;
  query?: never;
  url: "/auth/signout";
};

export type SignoutResponses = {
  /**
   * Successful Response
   */
  204: void;
};

export type SignoutResponse = SignoutResponses[keyof SignoutResponses];

export type GetCurrentUserData = {
  body?: never;
  path?: never;
  query?: never;
  url: "/auth/me";
};

export type GetCurrentUserResponses = {
  /**
   * Successful Response
   */
  200: User;
};

export type GetCurrentUserResponse = GetCurrentUserResponses[keyof GetCurrentUserResponses];

export type ListChatsData = {
  body?: never;
  path?: never;
  query?: {
    cursor?: number;
  };
  url: "/chats";
};

export type ListChatsErrors = {
  /**
   * Unauthorized
   */
  401: HttpUnauthorizedError;
  /**
   * Validation Error
   */
  422: HttpValidationError;
};

export type ListChatsError = ListChatsErrors[keyof ListChatsErrors];

export type ListChatsResponses = {
  /**
   * Successful Response
   */
  200: PaginatedChat;
};

export type ListChatsResponse = ListChatsResponses[keyof ListChatsResponses];

export type CreateChatData = {
  body: MessageRequest;
  path?: never;
  query?: never;
  url: "/chats";
};

export type CreateChatErrors = {
  /**
   * Unauthorized
   */
  401: HttpUnauthorizedError;
  /**
   * Validation Error
   */
  422: HttpValidationError;
};

export type CreateChatError = CreateChatErrors[keyof CreateChatErrors];

export type CreateChatResponses = {
  /**
   * Successful Response
   */
  201: CreateChatResponse;
};

export type CreateChatResponse2 = CreateChatResponses[keyof CreateChatResponses];

export type GetChatData = {
  body?: never;
  path: {
    slug: string;
  };
  query?: never;
  url: "/chats/{slug}";
};

export type GetChatErrors = {
  /**
   * Unauthorized
   */
  401: HttpUnauthorizedError;
  /**
   * Validation Error
   */
  422: HttpValidationError;
};

export type GetChatError = GetChatErrors[keyof GetChatErrors];

export type GetChatResponses = {
  /**
   * Successful Response
   */
  200: Chat;
};

export type GetChatResponse = GetChatResponses[keyof GetChatResponses];

export type GetChatMessagesData = {
  body?: never;
  path: {
    slug: string;
  };
  query?: {
    cursor?: number;
  };
  url: "/chats/{slug}/messages";
};

export type GetChatMessagesErrors = {
  /**
   * Unauthorized
   */
  401: HttpUnauthorizedError;
  /**
   * Validation Error
   */
  422: HttpValidationError;
};

export type GetChatMessagesError = GetChatMessagesErrors[keyof GetChatMessagesErrors];

export type GetChatMessagesResponses = {
  /**
   * Successful Response
   */
  200: PaginatedChatMessage;
};

export type GetChatMessagesResponse = GetChatMessagesResponses[keyof GetChatMessagesResponses];

export type GetChatMessagesStreamData = {
  body?: never;
  path: {
    slug: string;
  };
  query?: never;
  url: "/chats/{slug}/messages/stream";
};

export type GetChatMessagesStreamErrors = {
  /**
   * Unauthorized
   */
  401: HttpUnauthorizedError;
  /**
   * Validation Error
   */
  422: HttpValidationError;
};

export type GetChatMessagesStreamError = GetChatMessagesStreamErrors[keyof GetChatMessagesStreamErrors];

export type GetChatMessagesStreamResponses = {
  /**
   * Successful Response
   */
  200: unknown;
};

export type MarkDocumentUploadedData = {
  body?: never;
  path: {
    id: string;
  };
  query?: never;
  url: "/documents/{id}/mark-uploaded";
};

export type MarkDocumentUploadedErrors = {
  /**
   * Unauthorized
   */
  401: HttpUnauthorizedError;
  /**
   * Validation Error
   */
  422: HttpValidationError;
};

export type MarkDocumentUploadedError = MarkDocumentUploadedErrors[keyof MarkDocumentUploadedErrors];

export type MarkDocumentUploadedResponses = {
  /**
   * Successful Response
   */
  204: void;
};

export type MarkDocumentUploadedResponse = MarkDocumentUploadedResponses[keyof MarkDocumentUploadedResponses];

export type RootData = {
  body?: never;
  path?: never;
  query?: never;
  url: "/";
};

export type RootResponses = {
  /**
   * Successful Response
   */
  200: {
    [key: string]: string;
  };
};

export type RootResponse = RootResponses[keyof RootResponses];
