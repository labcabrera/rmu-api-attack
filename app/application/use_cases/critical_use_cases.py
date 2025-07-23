"""
Critical use cases for the application layer.
"""

from typing import Optional, List, Dict, Any
from app.domain.entities.critical import Critical
from app.domain.ports.critical_ports import CriticalRepository, CriticalNotificationPort


class CreateCriticalUseCase:
    """Use case for creating a new critical"""
    
    def __init__(self, repository: CriticalRepository, 
                 notification_port: Optional[CriticalNotificationPort] = None):
        self.repository = repository
        self.notification_port = notification_port

    async def execute(self, critical_id: str, critical_type: str, roll: int, 
                     result: str, status: str = "pending") -> Critical:
        """Execute the create critical use case"""
        critical = Critical(
            id=critical_id,
            type=critical_type,
            roll=roll,
            result=result,
            status=status
        )

        created_critical = await self.repository.save(critical)

        if self.notification_port:
            await self.notification_port.notify_critical_created(created_critical)

        return created_critical


class GetCriticalUseCase:
    """Use case for retrieving a critical by ID"""
    
    def __init__(self, repository: CriticalRepository):
        self.repository = repository

    async def execute(self, critical_id: str) -> Optional[Critical]:
        """Execute the get critical use case"""
        return await self.repository.find_by_id(critical_id)


class UpdateCriticalUseCase:
    """Use case for updating a critical (PATCH)"""
    
    def __init__(self, repository: CriticalRepository,
                 notification_port: Optional[CriticalNotificationPort] = None):
        self.repository = repository
        self.notification_port = notification_port

    async def execute(self, critical_id: str, update_data: Dict[str, Any]) -> Optional[Critical]:
        """Execute the update critical use case"""
        existing_critical = await self.repository.find_by_id(critical_id)
        if not existing_critical:
            return None

        # Apply partial updates
        if "type" in update_data:
            existing_critical.type = update_data["type"]
        if "roll" in update_data:
            existing_critical.roll = update_data["roll"]
        if "result" in update_data:
            existing_critical.result = update_data["result"]
        if "status" in update_data:
            existing_critical.status = update_data["status"]

        updated_critical = await self.repository.update(existing_critical)

        if self.notification_port and updated_critical:
            await self.notification_port.notify_critical_updated(updated_critical)

        return updated_critical


class ListCriticalsUseCase:
    """Use case for listing criticals with filters"""
    
    def __init__(self, repository: CriticalRepository):
        self.repository = repository

    async def execute(self, status: Optional[str] = None, 
                     critical_type: Optional[str] = None,
                     limit: int = 100, skip: int = 0) -> List[Critical]:
        """Execute the list criticals use case"""
        return await self.repository.find_all(
            status=status,
            type=critical_type,
            limit=limit,
            skip=skip
        )


class ApplyCriticalUseCase:
    """Use case for applying a critical"""
    
    def __init__(self, repository: CriticalRepository,
                 notification_port: Optional[CriticalNotificationPort] = None):
        self.repository = repository
        self.notification_port = notification_port

    async def execute(self, critical_id: str) -> Optional[Critical]:
        """Execute the apply critical use case"""
        critical = await self.repository.find_by_id(critical_id)
        if not critical:
            return None

        critical.apply()
        updated_critical = await self.repository.update(critical)

        if self.notification_port and updated_critical:
            await self.notification_port.notify_critical_applied(updated_critical)

        return updated_critical
