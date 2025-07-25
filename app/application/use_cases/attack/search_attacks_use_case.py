from typing import Optional

from app.domain.entities.attack import Attack
from app.domain.entities.page import Page, Pagination
from app.domain.ports.attack_ports import AttackRepository


class SearchAttacksUseCase:
    """Use case for listing attacks with support for both RSQL queries and individual filters"""

    def __init__(self, attack_repository: AttackRepository):
        self._attack_repository = attack_repository

    async def execute(
        self,
        rsql_query: Optional[str] = None,
        page: int = 0,
        size: int = 100,
    ) -> Page[Attack]:

        skip = page * size
        limit = size

        if rsql_query:
            attacks = await self._attack_repository.find_by_rsql(
                rsql_query=rsql_query,
                limit=limit,
                skip=skip,
            )
            total_elements = await self._attack_repository.count_by_rsql(
                rsql_query=rsql_query,
            )
        else:
            attacks = await self._attack_repository.find_all(
                limit=limit,
                skip=skip,
            )
            total_elements = await self._attack_repository.count_all()

        pagination = Pagination(
            page=page,
            size=size,
            total_elements=total_elements,
        )

        return Page(
            content=attacks,
            pagination=pagination,
        )
