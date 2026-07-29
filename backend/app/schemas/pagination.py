from __future__ import annotations

from typing import TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class PageMeta(BaseModel):
    """Pagination metadata returned alongside a list of items."""

    model_config = ConfigDict(from_attributes=True)

    page: int
    page_size: int
    total: int
    total_pages: int


class PaginatedResponse[T](BaseModel):
    """Generic paginated list envelope."""

    items: list[T]
    meta: PageMeta
