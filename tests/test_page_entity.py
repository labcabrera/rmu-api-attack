"""
Tests for Page and Pagination entities
"""

import pytest
from app.domain.entities.page import Page, Pagination


class TestPagination:
    """Test cases for Pagination entity"""

    def test_pagination_basic_properties(self):
        """Test basic pagination properties"""
        pagination = Pagination(
            page=0,
            size=10,
            total_elements=25
        )
        
        assert pagination.page == 0
        assert pagination.size == 10
        assert pagination.total_elements == 25
        assert pagination.total_pages == 3  # ceil(25/10) = 3

    def test_pagination_total_pages_calculation(self):
        """Test total pages calculation with different scenarios"""
        # Exact division
        pagination1 = Pagination(page=0, size=10, total_elements=20)
        assert pagination1.total_pages == 2
        
        # With remainder
        pagination2 = Pagination(page=0, size=10, total_elements=25)
        assert pagination2.total_pages == 3
        
        # Single page
        pagination3 = Pagination(page=0, size=10, total_elements=5)
        assert pagination3.total_pages == 1
        
        # No elements
        pagination4 = Pagination(page=0, size=10, total_elements=0)
        assert pagination4.total_pages == 0

    def test_pagination_edge_cases(self):
        """Test edge cases for pagination"""
        # Zero size
        pagination_zero_size = Pagination(page=0, size=0, total_elements=10)
        assert pagination_zero_size.total_pages == 0
        
        # Single element per page
        pagination_single = Pagination(page=0, size=1, total_elements=100)
        assert pagination_single.total_pages == 100

    def test_pagination_is_first_page(self):
        """Test is_first property"""
        pagination_first = Pagination(page=0, size=10, total_elements=25)
        assert pagination_first.is_first is True
        
        pagination_not_first = Pagination(page=1, size=10, total_elements=25)
        assert pagination_not_first.is_first is False

    def test_pagination_is_last_page(self):
        """Test is_last property"""
        # Total pages = 3 (0, 1, 2), so page 2 is last
        pagination_last = Pagination(page=2, size=10, total_elements=25)
        assert pagination_last.is_last is True
        
        pagination_not_last = Pagination(page=1, size=10, total_elements=25)
        assert pagination_not_last.is_last is False
        
        # Single page scenario
        pagination_single_page = Pagination(page=0, size=10, total_elements=5)
        assert pagination_single_page.is_last is True


class TestPage:
    """Test cases for Page entity"""

    @pytest.fixture
    def sample_content(self):
        """Sample content for testing"""
        return ["item1", "item2", "item3", "item4", "item5"]

    @pytest.fixture
    def sample_pagination(self):
        """Sample pagination for testing"""
        return Pagination(page=1, size=5, total_elements=25)

    def test_page_basic_properties(self, sample_content, sample_pagination):
        """Test basic page properties"""
        page = Page(content=sample_content, pagination=sample_pagination)
        
        assert page.content == sample_content
        assert page.pagination == sample_pagination
        assert page.number_of_elements == 5

    def test_page_backward_compatibility_properties(self, sample_content, sample_pagination):
        """Test backward compatibility properties"""
        page = Page(content=sample_content, pagination=sample_pagination)
        
        # Test backward compatibility properties
        assert page.total_elements == 25
        assert page.page_number == 1
        assert page.page_size == 5
        assert page.total_pages == 5  # ceil(25/5) = 5
        assert page.is_first is False
        assert page.is_last is False

    def test_page_empty_content(self):
        """Test page with empty content"""
        pagination = Pagination(page=0, size=10, total_elements=0)
        page = Page(content=[], pagination=pagination)
        
        assert page.number_of_elements == 0
        assert page.total_elements == 0
        assert page.total_pages == 0
        assert page.is_first is True
        assert page.is_last is True

    def test_page_first_page(self):
        """Test first page properties"""
        content = ["item1", "item2"]
        pagination = Pagination(page=0, size=5, total_elements=12)
        page = Page(content=content, pagination=pagination)
        
        assert page.is_first is True
        assert page.is_last is False
        assert page.total_pages == 3  # ceil(12/5) = 3

    def test_page_last_page(self):
        """Test last page properties"""
        content = ["item11", "item12"]  # Only 2 items on last page
        pagination = Pagination(page=2, size=5, total_elements=12)
        page = Page(content=content, pagination=pagination)
        
        assert page.is_first is False
        assert page.is_last is True
        assert page.number_of_elements == 2
        assert page.total_pages == 3

    def test_page_middle_page(self):
        """Test middle page properties"""
        content = ["item6", "item7", "item8", "item9", "item10"]
        pagination = Pagination(page=1, size=5, total_elements=12)
        page = Page(content=content, pagination=pagination)
        
        assert page.is_first is False
        assert page.is_last is False
        assert page.number_of_elements == 5

    def test_page_generic_typing(self):
        """Test that Page works with different types"""
        # Page of strings
        string_content = ["a", "b", "c"]
        string_pagination = Pagination(page=0, size=3, total_elements=3)
        string_page = Page[str](content=string_content, pagination=string_pagination)
        assert len(string_page.content) == 3
        assert isinstance(string_page.content[0], str)
        
        # Page of integers
        int_content = [1, 2, 3]
        int_pagination = Pagination(page=0, size=3, total_elements=3)
        int_page = Page[int](content=int_content, pagination=int_pagination)
        assert len(int_page.content) == 3
        assert isinstance(int_page.content[0], int)


class TestPaginationScenarios:
    """Test realistic pagination scenarios"""

    def test_pagination_scenario_large_dataset(self):
        """Test pagination with large dataset"""
        # 1000 elements, 50 per page = 20 pages
        pagination = Pagination(page=10, size=50, total_elements=1000)
        
        assert pagination.total_pages == 20
        assert pagination.is_first is False
        assert pagination.is_last is False

    def test_pagination_scenario_incomplete_last_page(self):
        """Test pagination where last page is not full"""
        # 47 elements, 10 per page = 5 pages (last page has 7 elements)
        pagination_last = Pagination(page=4, size=10, total_elements=47)
        
        assert pagination_last.total_pages == 5
        assert pagination_last.is_last is True

    def test_pagination_scenario_single_page_dataset(self):
        """Test pagination with dataset that fits in one page"""
        pagination = Pagination(page=0, size=100, total_elements=50)
        
        assert pagination.total_pages == 1
        assert pagination.is_first is True
        assert pagination.is_last is True
