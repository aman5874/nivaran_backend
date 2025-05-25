import logging
from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.config.settings import settings
from app.models.request_models import GenerateRequest
from app.models.response_models import StructuredResponse
from app.services.ai_service import ai_service
from app.utils.error_handlers import APIError

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api", tags=["AI Generation"])

# Optional API key authentication dependency
async def verify_api_key(request: Request):
    """Verify API key if configured"""
    api_key = settings.API_KEY
    
    if not api_key:
        # API key auth is not configured, so allow all requests
        return True
    
    # Get API key from header
    request_api_key = request.headers.get(settings.API_KEY_HEADER)
    if not request_api_key:
        raise APIError(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message="API key is required"
        )
    
    if request_api_key != api_key:
        raise APIError(
            status_code=status.HTTP_403_FORBIDDEN,
            message="Invalid API key"
        )
    
    return True

@router.post("/generate", response_model=None)
async def generate(
    request_data: GenerateRequest,
    authenticated: bool = Depends(verify_api_key)
) -> StructuredResponse:
    """Generate AI responses from user input
    
    Processes the user input and returns a structured response in one of the following formats:
    - Text: Simple text message
    - Button: Interactive message with buttons
    - List: Interactive message with list options
    - Call to Action: Message with a clickable link
    
    The AI will automatically detect when a user is looking for a doctor and use function
    calling to search for appropriate doctors based on the specialty, symptoms, and location
    extracted from the conversation.
    """
    try:
        logger.info(f"Generate endpoint called for user {request_data.user_id}")
        
        # Call the AI service to generate a structured response
        structured_response = await ai_service.generate_response(
            prompt=request_data.text,
            conversation_id=request_data.conversation_id,
            user_id=request_data.user_id,
            previous_response_id=request_data.previous_response_id
        )
        
        # Return the structured response directly
        return structured_response
            
    except Exception as e:
        # Log error
        logger.error(f"Error in generate endpoint: {str(e)}")
        raise

@router.delete("/conversations/{conversation_id}", response_model=Dict[str, Any])
async def clear_conversation(
    conversation_id: str,
    authenticated: bool = Depends(verify_api_key)
) -> Dict[str, Any]:
    """Clear the conversation history for a given conversation ID
    
    Args:
        conversation_id: The conversation ID to clear
        
    Returns:
        Success status message
    """
    try:
        logger.info(f"Clear conversation endpoint called for conversation_id {conversation_id}")
        
        # Clear conversation history
        success = ai_service.clear_conversation_history(conversation_id)
        
        if success:
            return {"success": True, "message": f"Conversation {conversation_id} cleared successfully"}
        else:
            return {"success": False, "message": f"Conversation {conversation_id} not found"}
            
    except Exception as e:
        # Log error
        logger.error(f"Error in clear_conversation endpoint: {str(e)}")
        raise 