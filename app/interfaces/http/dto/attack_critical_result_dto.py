from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from app.domain.entities import AttackCriticalResult
from app.domain.entities.enums import CriticalStatus

from .critical_table_entry_dto import CriticalTableEntryDTO


class AttackCriticalResultDTO(BaseModel):
    """DTO for critical hit"""

    key: str = Field(..., description="Critical key")
    status: str = Field(..., description="Critical status")
    criticalType: Optional[str] = Field(..., description="Type of critical hit")
    criticalSeverity: Optional[str] = Field(..., description="Severity of critical hit")
    adjustedRoll: Optional[int] = Field(None, description="Adjusted roll value")
    result: Optional[CriticalTableEntryDTO] = Field(
        None, description="Critical result data"
    )

    model_config = ConfigDict(
        json_schema_extra={"example": {"key": "critical_001", "status": "success"}}
    )

    def to_entity(self):
        return AttackCriticalResult(
            key=self.key,
            status=CriticalStatus.from_value(self.status),
            critical_type=self.criticalType,
            critical_severity=self.criticalSeverity,
            adjusted_roll=self.adjustedRoll,
            result=self.result.to_entity() if self.result else None,
        )

    @classmethod
    def from_entity(cls, entity: AttackCriticalResult) -> "AttackCriticalResultDTO":
        return cls(
            key=entity.key,
            status=entity.status.value,
            criticalType=entity.critical_type,
            criticalSeverity=entity.critical_severity,
            adjustedRoll=entity.adjusted_roll,
            result=(
                CriticalTableEntryDTO.from_entity(entity.result)
                if entity.result
                else None
            ),
        )
