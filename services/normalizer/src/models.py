"""
Modelos Pydantic para validacion de eventos normalizados
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator


class NormalizedEvent(BaseModel):
    """Modelo de evento normalizado"""
    type: str = Field(..., description="Tipo de evento: sismo, lluvia, corte")
    occurred_at: datetime = Field(..., description="Fecha y hora del evento")
    zone: Optional[str] = Field(None, description="Zona geografica del evento")
    severity: Optional[str] = Field(None, description="Severidad: Baja, Media, Alta")
    title: str = Field(..., min_length=1, max_length=500, description="Titulo del evento")
    description: Optional[str] = Field(None, description="Descripcion detallada")
    evidence_url: str = Field(..., description="URL de evidencia")
    source_id: str = Field(..., description="ID de la fuente")
    dedup_hash: str = Field(..., description="Hash para deduplicacion")
    
    @validator('type')
    def validate_type(cls, v):
        """Validar que el tipo sea valido"""
        valid_types = ['sismo', 'lluvia', 'corte']
        if v not in valid_types:
            raise ValueError(f'Tipo debe ser uno de: {valid_types}')
        return v
    
    @validator('severity')
    def validate_severity(cls, v):
        """Validar que la severidad sea valida"""
        if v is None:
            return v
        valid_severities = ['Baja', 'Media', 'Alta']
        if v not in valid_severities:
            raise ValueError(f'Severidad debe ser uno de: {valid_severities}')
        return v
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
