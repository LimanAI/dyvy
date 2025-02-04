import enum
from uuid import UUID

from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, mapped_column

from wallstr.models.base import RecordModel, string_column


class DocumentType(str, enum.Enum):
    PDF = "pdf"
    DOC = "doc"
    DOCX = "docx"
    XLS = "xls"
    XLSX = "xlsx"


class DocumentStatus(str, enum.Enum):
    UPLOADING = "uploading"
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class DocumentModel(RecordModel):
    __tablename__ = "documents"

    user_id: Mapped[UUID] = mapped_column(nullable=False, index=True)
    status: Mapped[DocumentStatus] = mapped_column(Enum(DocumentStatus), nullable=False)

    filename: Mapped[str] = string_column(length=255, nullable=False)
    file_size: Mapped[int] = mapped_column(nullable=True)
    doc_type: Mapped[DocumentType] = mapped_column(Enum(DocumentType), nullable=False)
    storage_path: Mapped[str] = string_column(length=1024, nullable=False)
    page_count: Mapped[int] = mapped_column(nullable=True)
