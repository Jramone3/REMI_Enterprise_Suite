from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class UserProfileBSUID(BaseModel):
    user_id: str = Field(..., description="ID Primario: BSUID (whatsapp:XX...) o Número E.164")
    phone_number: Optional[str] = None
    bsuid: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_active: datetime = Field(default_factory=datetime.utcnow)
    conversation_history: List[dict] = []

    def update_identity(self, raw_from: str, external_user_id: Optional[str] = None):
        if external_user_id:
            self.bsuid = external_user_id
        if raw_from.startswith("whatsapp:+"):
            self.phone_number = raw_from
