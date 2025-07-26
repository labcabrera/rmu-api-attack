"""
Dependency injection container for hexagonal architecture.
This assembles all the components and their dependencies.
"""

from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient

from app.domain.services.attack_calculator import AttackCalculator
from app.domain.services.attack_domain_service import AttackDomainService
from app.domain.ports.attack_ports import AttackRepository
from app.domain.ports.critical_ports import CriticalRepository
from app.domain.ports.attack_table_port import AttackTableClient


from app.application.use_cases import (
    ApplyAttackUseCase,
    CreateAttackUseCase,
    DeleteAttackUseCase,
    SearchAttackByIdUseCase,
    SearchAttacksByRsqlUseCase,
    UpdateAttackModifiersUseCase,
    UpdateAttackRollUseCase,
)
from app.application.use_cases.critical_use_cases import (
    CreateCriticalUseCase,
    GetCriticalUseCase,
    UpdateCriticalUseCase,
    ListCriticalsUseCase,
    ApplyCriticalUseCase,
)

from app.infrastructure.config.config import settings
from app.infrastructure.adapters.persistence.mongo_attack_repository import (
    MongoAttackRepository,
)
from app.infrastructure.adapters.persistence.mongo_critical_repository import (
    MongoCriticalRepository,
)
from app.infrastructure.adapters.external.attack_table_rest_adapter import (
    AttackTableRestAdapter,
    AttackTableRestAdapterWithRetry,
)
from app.infrastructure.config.attack_table_config import AttackTableApiConfig


class DependencyContainer:
    """Container for dependency injection"""

    def __init__(self):
        self._client = None
        self._database = None

        # Repositories
        self._attack_repository: Optional[AttackRepository] = None
        self._critical_repository: Optional[CriticalRepository] = None

        # External services
        self._attack_table_service: Optional[AttackTableClient] = None

        # Domain services
        self._attack_domain_service: Optional[AttackDomainService] = None
        self._attack_calculator: Optional[AttackCalculator] = None

        # Attack Use Cases
        self._apply_attack_use_case: Optional[ApplyAttackUseCase] = None
        self._create_attack_use_case: Optional[CreateAttackUseCase] = None
        self._delete_attack_use_case: Optional[DeleteAttackUseCase] = None
        self._search_attack_by_id_use_case: Optional[SearchAttackByIdUseCase] = None
        self._search_attack_by_rsql_use_case: Optional[SearchAttacksByRsqlUseCase] = (
            None
        )
        self._update_attack_modifiers_use_case: Optional[
            UpdateAttackModifiersUseCase
        ] = None
        self._update_attack_roll_use_case: Optional[UpdateAttackRollUseCase] = None

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

        # Initialize external services
        attack_table_config = AttackTableApiConfig.from_env()
        if attack_table_config.enable_retry:
            self._attack_table_service = AttackTableRestAdapterWithRetry(
                base_url=attack_table_config.base_url,
                timeout=attack_table_config.timeout,
                api_key=attack_table_config.api_key,
                max_retries=attack_table_config.max_retries,
                retry_delay=attack_table_config.retry_delay,
            )
        else:
            self._attack_table_service = AttackTableRestAdapter(
                base_url=attack_table_config.base_url,
                timeout=attack_table_config.timeout,
                api_key=attack_table_config.api_key,
            )

        # Initialize indexes
        await self._critical_repository.initialize()

        # Initialize domain services
        self._attack_calculator = AttackCalculator(
            attack_table_client=self._attack_table_service,
        )
        self._attack_domain_service = AttackDomainService(
            attack_calculator=self._attack_calculator,
            attack_repository=self._attack_repository,
        )

        # Initialize Attack use cases
        self._apply_attack_results_use_case = ApplyAttackUseCase(
            self._attack_domain_service
        )
        self._create_attack_use_case = CreateAttackUseCase(self._attack_domain_service)
        self._delete_attack_use_case = DeleteAttackUseCase(self._attack_repository)
        self._search_attack_by_id_use_case = SearchAttackByIdUseCase(
            self._attack_repository
        )
        self._search_attack_by_rsql_use_case = SearchAttacksByRsqlUseCase(
            self._attack_repository
        )
        self._update_attack_modifiers_use_case = UpdateAttackModifiersUseCase(
            attack_repository=self._attack_repository,
            attack_calculator=self._attack_calculator,
        )
        self._update_attack_roll_use_case = UpdateAttackRollUseCase(
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

    def get_apply_attack_use_case(self) -> ApplyAttackUseCase:
        """Get apply attack use case instance"""
        return self._apply_attack_use_case

    def get_create_attack_use_case(self) -> CreateAttackUseCase:
        """Get create attack use case instance"""
        return self._create_attack_use_case

    def get_delete_attack_use_case(self) -> DeleteAttackUseCase:
        """Get delete attack use case instance"""
        return self._delete_attack_use_case

    def get_search_attack_by_id_use_case(self) -> SearchAttackByIdUseCase:
        """Get search attack by ID use case instance"""
        return self._search_attack_by_id_use_case

    def get_search_attack_by_rsql_use_case(self) -> SearchAttacksByRsqlUseCase:
        """Get search attack by RSQL use case instance"""
        return self._search_attack_by_rsql_use_case

    def get_update_attack_modifiers_use_case(self) -> UpdateAttackModifiersUseCase:
        """Get update attack modifiers use case instance"""
        return self._update_attack_modifiers_use_case

    def get_update_attack_roll_use_case(self) -> UpdateAttackRollUseCase:
        """Get update attack roll use case instance"""
        return self._update_attack_roll_use_case

    # External services
    def get_attack_table_service(self) -> AttackTableClient:
        """Get attack table service instance"""
        return self._attack_table_service

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
