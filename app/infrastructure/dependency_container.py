"""
Dependency injection container for hexagonal architecture.
This assembles all the components and their dependencies.
"""

from typing import Optional
from app.domain.services import AttackDomainService
from app.domain.ports import AttackRepository, AttackNotificationPort
from app.application.use_cases import (
    CreateAttackUseCase,
    GetAttackUseCase,
    ListAttacksUseCase,
    UpdateAttackUseCase,
    DeleteAttackUseCase,
    ExecuteAttackRollUseCase,
    ApplyAttackResultsUseCase
)
from app.infrastructure.adapters.persistence import MongoAttackRepository
from app.infrastructure.adapters.web import AttackController


class DependencyContainer:
    """Container for dependency injection"""
    
    def __init__(self):
        self._attack_repository: Optional[AttackRepository] = None
        self._attack_domain_service: Optional[AttackDomainService] = None
        self._attack_controller: Optional[AttackController] = None
        
        # Use cases
        self._create_attack_use_case: Optional[CreateAttackUseCase] = None
        self._get_attack_use_case: Optional[GetAttackUseCase] = None
        self._list_attacks_use_case: Optional[ListAttacksUseCase] = None
        self._update_attack_use_case: Optional[UpdateAttackUseCase] = None
        self._delete_attack_use_case: Optional[DeleteAttackUseCase] = None
        self._execute_attack_roll_use_case: Optional[ExecuteAttackRollUseCase] = None
        self._apply_attack_results_use_case: Optional[ApplyAttackResultsUseCase] = None
    
    def get_attack_repository(self) -> AttackRepository:
        """Get attack repository instance"""
        if self._attack_repository is None:
            self._attack_repository = MongoAttackRepository()
        return self._attack_repository
    
    def get_attack_domain_service(self) -> AttackDomainService:
        """Get attack domain service instance"""
        if self._attack_domain_service is None:
            self._attack_domain_service = AttackDomainService(
                attack_repository=self.get_attack_repository(),
                notification_port=None  # TODO: Implement notification adapter if needed
            )
        return self._attack_domain_service
    
    def get_create_attack_use_case(self) -> CreateAttackUseCase:
        """Get create attack use case instance"""
        if self._create_attack_use_case is None:
            self._create_attack_use_case = CreateAttackUseCase(
                domain_service=self.get_attack_domain_service()
            )
        return self._create_attack_use_case
    
    def get_get_attack_use_case(self) -> GetAttackUseCase:
        """Get get attack use case instance"""
        if self._get_attack_use_case is None:
            self._get_attack_use_case = GetAttackUseCase(
                attack_repository=self.get_attack_repository()
            )
        return self._get_attack_use_case
    
    def get_list_attacks_use_case(self) -> ListAttacksUseCase:
        """Get list attacks use case instance"""
        if self._list_attacks_use_case is None:
            self._list_attacks_use_case = ListAttacksUseCase(
                attack_repository=self.get_attack_repository()
            )
        return self._list_attacks_use_case
    
    def get_update_attack_use_case(self) -> UpdateAttackUseCase:
        """Get update attack use case instance"""
        if self._update_attack_use_case is None:
            self._update_attack_use_case = UpdateAttackUseCase(
                attack_repository=self.get_attack_repository(),
                notification_port=None  # TODO: Implement notification adapter if needed
            )
        return self._update_attack_use_case
    
    def get_delete_attack_use_case(self) -> DeleteAttackUseCase:
        """Get delete attack use case instance"""
        if self._delete_attack_use_case is None:
            self._delete_attack_use_case = DeleteAttackUseCase(
                attack_repository=self.get_attack_repository()
            )
        return self._delete_attack_use_case
    
    def get_execute_attack_roll_use_case(self) -> ExecuteAttackRollUseCase:
        """Get execute attack roll use case instance"""
        if self._execute_attack_roll_use_case is None:
            self._execute_attack_roll_use_case = ExecuteAttackRollUseCase(
                domain_service=self.get_attack_domain_service()
            )
        return self._execute_attack_roll_use_case
    
    def get_apply_attack_results_use_case(self) -> ApplyAttackResultsUseCase:
        """Get apply attack results use case instance"""
        if self._apply_attack_results_use_case is None:
            self._apply_attack_results_use_case = ApplyAttackResultsUseCase(
                domain_service=self.get_attack_domain_service()
            )
        return self._apply_attack_results_use_case
    
    def get_attack_controller(self) -> AttackController:
        """Get attack controller instance"""
        if self._attack_controller is None:
            self._attack_controller = AttackController(
                create_attack_use_case=self.get_create_attack_use_case(),
                get_attack_use_case=self.get_get_attack_use_case(),
                list_attacks_use_case=self.get_list_attacks_use_case(),
                update_attack_use_case=self.get_update_attack_use_case(),
                delete_attack_use_case=self.get_delete_attack_use_case()
            )
        return self._attack_controller
    
    async def initialize(self):
        """Initialize dependencies that require async setup"""
        # Initialize MongoDB connection
        repository = self.get_attack_repository()
        if hasattr(repository, 'connect'):
            await repository.connect()
    
    async def cleanup(self):
        """Clean up dependencies"""
        # Close MongoDB connection
        repository = self.get_attack_repository()
        if hasattr(repository, 'disconnect'):
            await repository.disconnect()


# Global container instance
container = DependencyContainer()
