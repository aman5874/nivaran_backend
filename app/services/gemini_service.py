"""
Gemini Service for retrieving doctor information using Google's Generative AI API.
"""

import logging
import os
import datetime
import json
from typing import Optional, Dict, Any

from google import genai
from google.genai import types

from app.config.gemini_prompts import DOCTOR_SERVICE_PROMPT
from app.config.settings import settings

# Configure logging
logger = logging.getLogger(__name__)

class GeminiService:
    """Service for retrieving doctor information using Google's Generative AI API."""
    
    def __init__(self):
        """Initialize Gemini service with API key and client."""
        # Get API key from environment variables
        self.api_key = os.environ.get("GEMINI_API_KEY")
        
        if not self.api_key:
            logger.error("GEMINI_API_KEY not found in environment variables. Gemini service will not function properly.")
            self.client = None # Ensure client is set to None
            return
            
        # Configure Gemini client with the API key
        try:
            self.client = genai.Client(api_key=self.api_key)
            logger.info("Gemini API client configured successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {str(e)}", exc_info=True)
            self.client = None
    
    def _clean_response_text(self, response_text: str) -> str:
        """
        Clean up response text to ensure it's properly formatted.
        
        Args:
            response_text: Raw response text from Gemini
            
        Returns:
            Cleaned response text
        """
        # Handle common JSON issues
        if response_text.startswith("```json") and response_text.endswith("```"):
            # Extract JSON from markdown code block
            response_text = response_text[7:-3].strip()
        elif response_text.startswith("```") and response_text.endswith("```"):
            # Extract content from any markdown code block
            response_text = response_text[3:-3].strip()
            
        # Remove any invalid trailing commas in JSON objects
        response_text = response_text.replace(",\n}", "\n}")
        response_text = response_text.replace(",\n]", "\n]")
        
        # Validate if it's JSON or not
        try:
            # Try to parse as JSON to see if it's valid
            json.loads(response_text)
            # If it's valid JSON, return as is
            return response_text
        except (json.JSONDecodeError, ValueError):
            # If not valid JSON, just return as plain text
            return response_text
    
    async def get_service_info(self, prompt: str) -> Dict[str, Any]:
        """
        Get healthcare service information using the Gemini API.
        
        Args:
            prompt: The user's input containing healthcare service query
            
        Returns:
            A dictionary with either service data or error information
        """
        # Check if client is properly initialized
        if not hasattr(self, 'client') or self.client is None:
            logger.error("Gemini client not initialized - cannot process request")
            return {
                "success": False,
                "error": "configuration_error",
                "message": "Unable to retrieve healthcare information due to a configuration issue."
            }
            
        try:
            # Log the input prompt for debugging
            logger.info(f"Sending prompt to Gemini: {prompt[:100]}...")
            
            # Get current date and time information
            now = datetime.datetime.now()
            current_date = now.strftime("%d-%m-%Y")
            current_time = now.strftime("%H:%M")
            current_day = now.strftime("%A")
            
            # Instead of using string formatting with placeholders, construct the prompt directly
            # This avoids issues with curly braces in the template string
            system_prompt = DOCTOR_SERVICE_PROMPT.replace("{current_date}", current_date)
            system_prompt = system_prompt.replace("{current_time}", current_time)
            system_prompt = system_prompt.replace("{current_day}", current_day)
            
            # Set up system instruction
            system_instruction = system_prompt
            
            # Set up content with user prompt
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=prompt),
                    ],
                ),
            ]
            
            # Configure safety settings
            safety_settings = [
                types.SafetySetting(
                    category="HARM_CATEGORY_HARASSMENT",
                    threshold="BLOCK_MEDIUM_AND_ABOVE",
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_HATE_SPEECH",
                    threshold="BLOCK_MEDIUM_AND_ABOVE",
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    threshold="BLOCK_MEDIUM_AND_ABOVE",
                ),
                types.SafetySetting(
                    category="HARM_CATEGORY_DANGEROUS_CONTENT",
                    threshold="BLOCK_MEDIUM_AND_ABOVE",
                ),
            ]
            
            # Configure generation settings
            generate_content_config = types.GenerateContentConfig(
                safety_settings=safety_settings,
                temperature=0.7,
                top_p=0.95,
                top_k=40,
                max_output_tokens=2048,
                system_instruction=system_instruction,
            )
            
            # Select model
            model_name = settings.GEMINI_API_MODEL_NAME
            
            # Make the API call
            try:
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config=generate_content_config,
                )
                
                # Log the response for debugging
                logger.info(f"Gemini raw response: {str(response)[:200]}...")
                
                # Extract text from response
                if not hasattr(response, 'text'):
                    logger.error("Gemini returned an invalid response structure")
                    return {
                        "success": False,
                        "error": "invalid_response",
                        "message": "No information available at this time."
                    }
                    
                # Clean up the response text
                cleaned_response_text = self._clean_response_text(response.text)
                
                # Log the response but don't modify the actual return value
                logger.info(f"Received service info from Gemini: {cleaned_response_text[:100]}...")
                
                # Return a structured response
                return {
                    "success": True,
                    "data": cleaned_response_text,
                    "query": prompt
                }
                
            except Exception as api_e:
                logger.error(f"API call error: {str(api_e)}", exc_info=True)
                return {
                    "success": False,
                    "error": "api_error",
                    "message": "Unable to retrieve healthcare information due to an API error."
                }
                
        except Exception as e:
            logger.error(f"Error getting service info from Gemini: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": "technical_error",
                "message": "Unable to retrieve healthcare information due to a technical issue."
            }
            
    # Keep the old method for backward compatibility but update return value
    async def get_doctor_info(self, prompt: str) -> Dict[str, Any]:
        """DEPRECATED: This method is an alias for get_service_info. Consider using get_service_info directly."""
        logger.warning("The get_doctor_info method is deprecated. Use get_service_info instead.")
        return await self.get_service_info(prompt)

    # Add a legacy method to maintain backward compatibility
    async def get_service_info_text(self, prompt: str) -> Optional[str]:
        """DEPRECATED: This method returns plain text and may be removed in future versions. Prefer get_service_info for structured output."""
        logger.warning("The get_service_info_text method is deprecated and may be removed in the future. Prefer get_service_info.")
        result = await self.get_service_info(prompt)
        if result["success"]:
            return result["data"]
        else:
            return result["message"]

# Create singleton instance
gemini_service = GeminiService()