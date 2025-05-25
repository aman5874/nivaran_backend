from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class GenerateRequest(BaseModel):
    """Request model for the generate endpoint"""
    user_id: str = Field(..., description="Unique identifier for the user")
    text: str = Field(..., description="User input/prompt", min_length=1)
    conversation_id: Optional[str] = Field(None, description="ID for continuing existing conversations")
    previous_response_id: Optional[str] = Field(None, description="ID of the previous response for continuing conversations")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_id": "user123",
                "text": "Tell me about artificial intelligence",
                "conversation_id": "conv456",
                "previous_response_id": None
            }
        }
    ) 