from pydantic import BaseModel, ConfigDict, Field

from app.domain.entities import Page, Pagination
from app.infrastructure.adapters.web.dto import AttackDTO


class PaginationDTO(BaseModel):
    """DTO for pagination metadata"""

    model_config = ConfigDict(use_enum_values=True)

    page: int = Field(..., description="Current page number (0-based)")
    size: int = Field(..., description="Page size")
    totalElements: int = Field(..., description="Total number of elements")
    totalPages: int = Field(..., description="Total number of pages")

    @classmethod
    def from_entity(cls, entity: Pagination) -> "PaginationDTO":
        return cls(
            page=entity.page,
            size=entity.size,
            totalElements=entity.total_elements,
            totalPages=entity.total_pages,
        )


class PagedAttacksDTO(BaseModel):
    """DTO for paginated attack results"""

    model_config = ConfigDict(use_enum_values=True)

    content: list[AttackDTO] = Field(..., description="List of attacks")
    pagination: PaginationDTO = Field(..., description="Pagination metadata")

    @classmethod
    def from_entity(cls, entity: Page) -> "PagedAttacksDTO":
        return cls(
            content=[AttackDTO.from_entity(attack) for attack in entity.content],
            pagination=PaginationDTO.from_entity(entity.pagination),
        )
