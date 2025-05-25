from typing import Optional, Any, Dict, List, Union, Literal
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
from datetime import datetime
import uuid

# Basic button reply model
class ButtonReply(BaseModel):
    id: str
    title: str

# Button for interactive responses
class Button(BaseModel):
    reply: ButtonReply

# Button message components
class ButtonBody(BaseModel):
    text: str

class ButtonAction(BaseModel):
    buttons: List[Button]

# Alternative button message format (for compatibility)
class ButtonAlternativeFormat(BaseModel):
    message: str
    buttons: List[Dict[str, Any]]
    
    @model_validator(mode='after')
    def validate_buttons(self) -> 'ButtonAlternativeFormat':
        for button in self.buttons:
            if 'reply' not in button:
                raise ValueError("Each button must contain a 'reply' field")
            reply = button['reply']
            if not isinstance(reply, dict) or 'id' not in reply or 'title' not in reply:
                raise ValueError("Each reply must contain 'id' and 'title' fields")
        return self

# List message components
class ListRow(BaseModel):
    id: str
    title: str
    description: str

# Doctor-specific list row
class DoctorRow(ListRow):
    """Specific model for doctor search results"""
    id: str  # Format: "<doctor_id>-<specialty>-<condition>"
    title: str  # Doctor name
    description: str  # Doctor information including hospital, location, contact, etc.

class ListSection(BaseModel):
    title: str
    rows: List[ListRow]

# Hospital section containing doctors
class HospitalSection(ListSection):
    """Section representing a hospital with its doctors"""
    title: str  # Hospital name
    rows: List[DoctorRow]

class ListBody(BaseModel):
    text: str

class ListAction(BaseModel):
    button: str
    sections: List[ListSection]

# Call to action parameters
class CallToActionParameters(BaseModel):
    display_text: str
    url: str

# Content models for each response type
class TextContent(BaseModel):
    text: str

class ButtonContent(BaseModel):
    body: ButtonBody
    action: ButtonAction
    
    # Support alternative format where we have "message" and "buttons" directly
    @classmethod
    def from_alternative_format(cls, alt_format: ButtonAlternativeFormat) -> 'ButtonContent':
        return cls(
            body=ButtonBody(text=alt_format.message),
            action=ButtonAction(
                buttons=[
                    Button(
                        reply=ButtonReply(
                            id=btn['reply']['id'],
                            title=btn['reply']['title']
                        )
                    )
                    for btn in alt_format.buttons
                ]
            )
        )

class ListContent(BaseModel):
    body: ListBody
    action: ListAction

class CallToActionContent(BaseModel):
    name: str = "cta_url"
    parameters: CallToActionParameters

# Base response model with common fields and methods
class BaseResponse(BaseModel):
    response_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique ID for this response")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for continuation")
    
    def model_dump(self, **kwargs):
        """Include response_id and conversation_id in the output"""
        data = super().model_dump(**kwargs)
        # Make sure conversation_id is included only if it has a value
        if not data.get('conversation_id'):
            data.pop('conversation_id', None)
        return data

# Main structured response models
class TextResponse(BaseResponse):
    type: Literal["text"] = "text"
    content: TextContent

class ButtonResponse(BaseResponse):
    type: Literal["button"] = "button"
    content: Union[ButtonContent, Dict[str, Any]]
    
    @model_validator(mode='after')
    def validate_content(self) -> 'ButtonResponse':
        if isinstance(self.content, dict) and 'message' in self.content and 'buttons' in self.content:
            # Convert from alternative format to standard format
            alt_format = ButtonAlternativeFormat(**self.content)
            self.content = ButtonContent.from_alternative_format(alt_format)
        return self

class ListResponse(BaseResponse):
    type: Literal["list"] = "list"
    content: ListContent

class CallToActionResponse(BaseResponse):
    type: Literal["call_to_action"] = "call_to_action"
    content: CallToActionContent

# Doctor search specific action
class DoctorSearchAction(BaseModel):
    """Action for doctor search results"""
    button: str = "View Doctors"
    sections: List[HospitalSection]

# Doctor search content model
class DoctorSearchContent(BaseModel):
    """Content model for doctor search results"""
    body: ListBody
    action: DoctorSearchAction

    # Override model_dump to match the required format exactly
    def model_dump(self, **kwargs):
        """Customize the JSON output to match the exact required format"""
        return {
            "body": {
                "text": self.body.text
            },
            "action": {
                "button": self.action.button,
                "sections": [
                    {
                        "title": section.title,
                        "rows": [
                            {
                                "id": row.id,
                                "title": row.title,
                                "description": row.description
                            }
                            for row in section.rows
                        ]
                    }
                    for section in self.action.sections
                ]
            }
        }

# Doctor search response
class DoctorSearchResponse(BaseResponse):
    """Response model for doctor search results"""
    type: Literal["list"] = "list"
    content: DoctorSearchContent

    # Override model_dump to match the required format exactly
    def model_dump(self, **kwargs):
        """Customize the JSON output to match the exact required format"""
        base_dump = {
            "type": "list",
            "content": self.content.model_dump(),
            "response_id": self.response_id
        }
        if self.conversation_id:
            base_dump["conversation_id"] = self.conversation_id
        return base_dump

# Diagnostic lab specific models
class DiagnosticTestRow(ListRow):
    """Specific model for diagnostic test results"""
    id: str  # Format: "<test_id>"
    title: str  # Test name
    description: str  # Test information including price, lab name, etc.

class DiagnosticLabSection(ListSection):
    """Section representing a diagnostic lab with its tests"""
    title: str  # Diagnostic lab name
    rows: List[DiagnosticTestRow]

class DiagnosticSearchAction(BaseModel):
    """Action for diagnostic search results"""
    button: str = "View Tests"
    sections: List[DiagnosticLabSection]

class DiagnosticSearchContent(BaseModel):
    """Content model for diagnostic search results"""
    body: ListBody
    action: DiagnosticSearchAction

    # Override model_dump to match the required format exactly
    def model_dump(self, **kwargs):
        """Customize the JSON output to match the exact required format"""
        return {
            "body": {
                "text": self.body.text
            },
            "action": {
                "button": self.action.button,
                "sections": [
                    {
                        "title": section.title,
                        "rows": [
                            {
                                "id": row.id,
                                "title": row.title,
                                "description": row.description
                            }
                            for row in section.rows
                        ]
                    }
                    for section in self.action.sections
                ]
            }
        }

# Diagnostic search response
class DiagnosticSearchResponse(BaseResponse):
    """Response model for diagnostic search results"""
    type: Literal["list"] = "list"
    content: DiagnosticSearchContent

    # Override model_dump to match the required format exactly
    def model_dump(self, **kwargs):
        """Customize the JSON output to match the exact required format"""
        base_dump = {
            "type": "list",
            "content": self.content.model_dump(),
            "response_id": self.response_id
        }
        if self.conversation_id:
            base_dump["conversation_id"] = self.conversation_id
        return base_dump

# Union type for all response types
StructuredResponse = Union[TextResponse, ButtonResponse, ListResponse, CallToActionResponse, DoctorSearchResponse, DiagnosticSearchResponse]

# Legacy models kept for compatibility
class GenerateResponse(BaseModel):
    """Model for complete AI response"""
    text: str = Field(..., description="Complete AI response text")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for continuation")
    previous_response_id: Optional[str] = Field(None, description="Previous response ID for context")
    response_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique ID for this response")
    model: str = Field(..., description="AI model used for generation")
    created_at: datetime = Field(default_factory=datetime.now, description="Timestamp of response creation")
    token_usage: Dict[str, int] = Field(..., description="Token usage statistics")
    finish_reason: Optional[str] = Field(None, description="Reason for finishing the response")

class ErrorResponse(BaseModel):
    """Model for error responses"""
    error: bool = Field(True, description="Error flag")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error": True,
                "message": "Invalid request parameters",
                "details": {
                    "text": "Field is required"
                }
            }
        }
    ) 