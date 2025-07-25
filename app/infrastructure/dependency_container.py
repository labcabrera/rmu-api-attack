"""
Dependency injection container for hexagonal architecture.
This assembles all the components and their dependencies.
"""

from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings

from app.domain.services.attack_domain_service import AttackDomainService
from app.domain.ports.attack_ports import AttackRepository
from app.domain.ports.critical_ports import CriticalRepository

from app.application.use_cases.attack.create_attack_use_case import CreateAttackUseCase
from app.application.use_cases.attack.search_attacks_use_case import (
    SearchAttacksUseCase,
)
from app.application.use_cases.attack_use_cases import (
    GetAttackUseCase,
    UpdateAttackUseCase,
    DeleteAttackUseCase,
    ExecuteAttackRollUseCase,
    ApplyAttackResultsUseCase,
)

from app.application.use_cases.critical_use_cases import (
    CreateCriticalUseCase,
    GetCriticalUseCase,
    UpdateCriticalUseCase,
    ListCriticalsUseCase,
    ApplyCriticalUseCase,
)

from app.infrastructure.adapters.persistence.mongo_attack_repository import (
    MongoAttackRepository,
)
from app.infrastructure.adapters.persistence.mongo_critical_repository import (
    MongoCriticalRepository,
)


class DependencyContainer:
    """Container for dependency injection"""

    def __init__(self):
        self._client = None
        self._database = None

        # Repositories
        self._attack_repository: Optional[AttackRepository] = None
        self._critical_repository: Optional[CriticalRepository] = None

        # Domain services
        self._attack_domain_service: Optional[AttackDomainService] = None

        # Attack Use Cases
        self._create_attack_use_case: Optional[CreateAttackUseCase] = None
        self._get_attack_use_case: Optional[GetAttackUseCase] = None
        self._update_attack_use_case: Optional[UpdateAttackUseCase] = None
        self._list_attacks_use_case: Optional[SearchAttacksUseCase] = None
        self._delete_attack_use_case: Optional[DeleteAttackUseCase] = None
        self._execute_attack_roll_use_case: Optional[ExecuteAttackRollUseCase] = None
        self._apply_attack_results_use_case: Optional[ApplyAttackResultsUseCase] = None

        # Critical Use Cases
        self._create_critical_use_case: Optional[CreateCriticalUseCase] = None
        self._get_critical_use_case: Optional[GetCriticalUseCase] = None
        self._update_critical_use_case: Optional[UpdateCriticalUseCase] = None
        self._list_criticals_use_case: Optional[ListCriticalsUseCase] = None
        self._apply_critical_use_case: Optional[ApplyCriticalUseCase] = None

    async def initialize(self):
        """Initialize all dependencies"""
        # Database connection
        self._client = AsyncIOMotorClient(settings.MONGODB_URL)
        self._database = self._client[settings.MONGODB_DATABASE]

        # Test connection
        await self._database.command("ping")

        # Initialize repositories
        self._attack_repository = MongoAttackRepository(self._database)
        self._critical_repository = MongoCriticalRepository(self._database)

        # Initialize indexes
        await self._critical_repository.initialize()

        # Initialize domain services
        self._attack_domain_service = AttackDomainService(self._attack_repository)

        # Initialize Attack use cases
        self._create_attack_use_case = CreateAttackUseCase(self._attack_domain_service)
        self._get_attack_use_case = GetAttackUseCase(self._attack_repository)
        self._update_attack_use_case = UpdateAttackUseCase(self._attack_repository)
        self._list_attacks_use_case = SearchAttacksUseCase(self._attack_repository)
        self._delete_attack_use_case = DeleteAttackUseCase(self._attack_repository)
        self._execute_attack_roll_use_case = ExecuteAttackRollUseCase(
            self._attack_domain_service
        )
        self._apply_attack_results_use_case = ApplyAttackResultsUseCase(
            self._attack_domain_service
        )

        # Initialize Critical use cases
        self._create_critical_use_case = CreateCriticalUseCase(
            self._critical_repository
        )
        self._get_critical_use_case = GetCriticalUseCase(self._critical_repository)
        self._update_critical_use_case = UpdateCriticalUseCase(
            self._critical_repository
        )
        self._list_criticals_use_case = ListCriticalsUseCase(self._critical_repository)
        self._apply_critical_use_case = ApplyCriticalUseCase(self._critical_repository)

    async def cleanup(self):
        """Clean up dependencies"""
        if self._client:
            self._client.close()
            self._client = None
            self._database = None

    # Attack repository and use cases
    def get_attack_repository(self) -> AttackRepository:
        """Get attack repository instance"""
        return self._attack_repository

    def get_create_attack_use_case(self) -> CreateAttackUseCase:
        """Get create attack use case instance"""
        return self._create_attack_use_case

    def get_get_attack_use_case(self) -> GetAttackUseCase:
        """Get get attack use case instance"""
        return self._get_attack_use_case

    def get_update_attack_use_case(self) -> UpdateAttackUseCase:
        """Get update attack use case instance"""
        return self._update_attack_use_case

    def get_list_attacks_use_case(self) -> SearchAttacksUseCase:
        """Get list attacks use case instance"""
        return self._list_attacks_use_case

    def get_delete_attack_use_case(self) -> DeleteAttackUseCase:
        """Get delete attack use case instance"""
        return self._delete_attack_use_case

    def get_execute_attack_roll_use_case(self) -> ExecuteAttackRollUseCase:
        """Get execute attack roll use case instance"""
        return self._execute_attack_roll_use_case

    def get_apply_attack_results_use_case(self) -> ApplyAttackResultsUseCase:
        """Get apply attack results use case instance"""
        return self._apply_attack_results_use_case

    # Critical repository and use cases
    def get_critical_repository(self) -> CriticalRepository:
        """Get critical repository instance"""
        return self._critical_repository

    def get_create_critical_use_case(self) -> CreateCriticalUseCase:
        """Get create critical use case instance"""
        return self._create_critical_use_case

    def get_get_critical_use_case(self) -> GetCriticalUseCase:
        """Get get critical use case instance"""
        return self._get_critical_use_case

    def get_update_critical_use_case(self) -> UpdateCriticalUseCase:
        """Get update critical use case instance"""
        return self._update_critical_use_case

    def get_list_criticals_use_case(self) -> ListCriticalsUseCase:
        """Get list criticals use case instance"""
        return self._list_criticals_use_case

    def get_apply_critical_use_case(self) -> ApplyCriticalUseCase:
        """Get apply critical use case instance"""
        return self._apply_critical_use_case


# Global container instance
container = DependencyContainer()
