"""
Domain entity for pagination.
This represents a page of results with metadata.
"""

from dataclasses import dataclass
from typing import List, TypeVar, Generic
import math

T = TypeVar("T")


@dataclass
class Pagination:
    """Pagination metadata"""

    page: int
    size: int
    total_elements: int

    @property
    def total_pages(self) -> int:
        """Calculate total number of pages"""
        if self.size <= 0:
            return 0
        return math.ceil(self.total_elements / self.size)

    @property
    def is_first(self) -> bool:
        """Check if this is the first page"""
        return self.page == 0

    @property
    def is_last(self) -> bool:
        """Check if this is the last page"""
        return self.page >= self.total_pages - 1


@dataclass
class Page(Generic[T]):
    """Generic page entity for paginated results"""

    content: List[T]
    pagination: Pagination

    @property
    def number_of_elements(self) -> int:
        """Get number of elements in current page"""
        return len(self.content)

    # Backward compatibility properties
    @property
    def total_elements(self) -> int:
        """Get total elements (backward compatibility)"""
        return self.pagination.total_elements

    @property
    def page_number(self) -> int:
        """Get page number (backward compatibility)"""
        return self.pagination.page

    @property
    def page_size(self) -> int:
        """Get page size (backward compatibility)"""
        return self.pagination.size

    @property
    def total_pages(self) -> int:
        """Get total pages (backward compatibility)"""
        return self.pagination.total_pages

    @property
    def is_first(self) -> bool:
        """Check if this is the first page (backward compatibility)"""
        return self.pagination.is_first

    @property
    def is_last(self) -> bool:
        """Check if this is the last page (backward compatibility)"""
        return self.pagination.is_last
