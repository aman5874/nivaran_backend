import logging
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, Optional

# Vector store functionality has been removed
# from app.utils.vector_store import vector_store
from app.routers.generate import verify_api_key

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/doctor",
    tags=["doctor"],
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"}
    }
)

@router.get("/availability/{provider_id}", response_model=Dict[str, Any])
async def get_doctor_availability(
    provider_id: str,
    day_of_week: Optional[str] = None,
    authenticated: bool = Depends(verify_api_key)
) -> Dict[str, Any]:
    """
    Get doctor availability information by provider_id.
    
    Args:
        provider_id: The provider ID of the doctor
        day_of_week: Optional specific day to query (e.g., "Monday", "Tuesday")
        
    Returns:
        Doctor information with availability details
    """
    try:
        logger.info(f"Doctor availability endpoint called for provider_id: {provider_id}, day: {day_of_week or 'all days'}")
        logger.warning("Vector store functionality has been removed. Doctor availability data is no longer available.")
        
        # Return a message indicating functionality is no longer available
        return {
            "status": "info",
            "message": "Doctor availability functionality has been removed. Please contact healthcare providers directly for availability information."
        }
            
    except Exception as e:
        # Log error
        logger.error(f"Error in doctor availability endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while retrieving doctor availability: {str(e)}"
        ) 