from dependency_injector import containers, providers
from app.infrastructure.persistence import MongoAttackRepository
from app.infrastructure.api_client.attack_table_rest_adapter import (
    AttackTableRestAdapter,
    AttackTableRestAdapterWithRetry,
)
from app.infrastructure.config.attack_table_config import AttackTableApiConfig
from app.domain.services.attack_calculator import AttackCalculator
from app.domain.services.attack_domain_service import AttackDomainService
from app.domain.services.attack_resolution_service import AttackResolutionService
from app.application.use_cases import ApplyAttackUseCase
from app.application.use_cases import CreateAttackUseCase
from app.application.use_cases import DeleteAttackUseCase
from app.application.use_cases import SearchAttackByIdUseCase
from app.application.use_cases import SearchAttacksByRsqlUseCase
from app.application.use_cases import UpdateAttackModifiersUseCase
from app.application.use_cases import UpdateAttackRollUseCase
from app.application.use_cases import UpdateCriticalRollUseCase
from app.application.use_cases import UpdateAttackParryUseCase
from app.application.use_cases import UpdateFumbleRollUseCase
from app.infrastructure.config.config import settings
from motor.motor_asyncio import AsyncIOMotorClient


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(packages=["app"])

    mongo_client = providers.Singleton(AsyncIOMotorClient, settings.MONGODB_URL)
    mongo_database = providers.Singleton(
        lambda client: client.get_default_database(), mongo_client
    )
    attack_repository = providers.Singleton(MongoAttackRepository, mongo_database)
    attack_table_config = providers.Singleton(AttackTableApiConfig.from_env)
    attack_table_service = providers.Singleton(
        lambda config: (
            AttackTableRestAdapterWithRetry(
                base_url=config.base_url,
                timeout=config.timeout,
                api_key=config.api_key,
                max_retries=config.max_retries,
                retry_delay=config.retry_delay,
            )
            if config.enable_retry
            else AttackTableRestAdapter(
                base_url=config.base_url,
                timeout=config.timeout,
                api_key=config.api_key,
            )
        ),
        attack_table_config,
    )
    attack_calculator = providers.Singleton(
        AttackCalculator, attack_table_client=attack_table_service
    )
    attack_domain_service = providers.Singleton(
        AttackDomainService,
        attack_calculator=attack_calculator,
        attack_repository=attack_repository,
    )
    attack_resolution_service = providers.Singleton(
        AttackResolutionService,
        attack_calculator=attack_calculator,
        attack_repository=attack_repository,
        attack_table_client=attack_table_service,
    )
    apply_attack_results_use_case = providers.Singleton(
        ApplyAttackUseCase, attack_domain_service
    )
    create_attack_use_case = providers.Singleton(
        CreateAttackUseCase, attack_domain_service
    )
    delete_attack_use_case = providers.Singleton(DeleteAttackUseCase, attack_repository)
    search_attack_by_id_use_case = providers.Singleton(
        SearchAttackByIdUseCase, attack_repository
    )
    search_attack_by_rsql_use_case = providers.Singleton(
        SearchAttacksByRsqlUseCase, attack_repository
    )
    update_attack_modifiers_use_case = providers.Singleton(
        UpdateAttackModifiersUseCase,
        attack_repository=attack_repository,
        attack_calculator=attack_calculator,
    )
    update_attack_roll_use_case = providers.Singleton(
        UpdateAttackRollUseCase, attack_resolution_service
    )
    update_critical_roll_use_case = providers.Singleton(
        UpdateCriticalRollUseCase, attack_resolution_service
    )
    update_fumble_roll_use_case = providers.Singleton(
        UpdateFumbleRollUseCase, attack_resolution_service
    )
    update_attack_parry_use_case = providers.Singleton(
        UpdateAttackParryUseCase,
        attack_repository=attack_repository,
        attack_calculator=attack_calculator,
    )
