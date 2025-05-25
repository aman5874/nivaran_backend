"""
AI Service for generating responses using OpenAI's API.
Handles conversation management, memory, and doctor information retrieval.
"""

import logging
import os
import json
import uuid
import asyncio
import datetime
import aiohttp
from typing import Dict, Any, List, Optional
from openai import AsyncOpenAI
from openai import APIError, RateLimitError, APIConnectionError, AuthenticationError

from app.config.settings import settings
from app.config.prompts import DEFAULT_SYSTEM_PROMPT
from app.models.response_models import StructuredResponse, TextResponse, TextContent
from app.services.memory_service import MemoryService
from app.services.gemini_service import gemini_service

# Configure logging
logger = logging.getLogger(__name__)

# Initialize memory service
memory_service = MemoryService()

# Constants for message roles
ROLE_SYSTEM = "system"
ROLE_USER = "user"
ROLE_ASSISTANT = "assistant"
ROLE_TOOL = "tool"

# Constants for content types
TYPE_TEXT = "text"
TYPE_BUTTON = "button"
TYPE_LIST = "list"
TYPE_CALL_TO_ACTION = "call_to_action"
TYPE_FUNCTION = "function"

# Constants for function names
FUNCTION_GET_SERVICE_INFO = "get_service_info"
FUNCTION_GET_CONFIRMATION = "get_confirmation"

class AIService:
    def __init__(self):
        self.openai_api_key = os.environ.get("OPENAI_API_KEY", settings.OPENAI_API_KEY)
        if not self.openai_api_key:
            logger.error("OPENAI_API_KEY not found. AIService may not function correctly.")
            self.client = None
        else:
            try:
                self.client = AsyncOpenAI(api_key=self.openai_api_key)
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                self.client = None
        
        # Define tools for function calling
        self.tools = [
            {
                "type": TYPE_FUNCTION,
                "function": {
                    "name": FUNCTION_GET_SERVICE_INFO,
                    "description": "Get information about doctors including their availability, specialties, diagnostic tests, pricing, and timings.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "User's query about doctors, specialties, hospitals, or medical services"
                            },
                            "location": {
                                "type": "string",
                                "description": "Location or city where the user is looking for doctors"
                            },
                            "specialty": {
                                "type": "string",
                                "description": "Medical specialty the user is looking for (e.g., cardiologist, dermatologist)"
                            },
                            "symptoms": {
                                "type": "string",
                                "description": "Symptoms the user is experiencing"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": TYPE_FUNCTION,
                "function": {
                    "name": FUNCTION_GET_CONFIRMATION,
                    "description": "Send appointment confirmation to the backend server.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "user_id": {
                                "type": "string",
                                "description": "The ID of the user making the appointment"
                            },
                            "conversation_id": {
                                "type": "string",
                                "description": "The ID of the current conversation"
                            },
                            "patient_details": {
                                "type": "object",
                                "description": "Details of the patient",
                                "properties": {
                                    "name": {
                                        "type": "string",
                                        "description": "Patient's full name"
                                    },
                                    "age": {
                                        "type": "integer",
                                        "description": "Patient's age"
                                    },
                                    "gender": {
                                        "type": "string",
                                        "description": "Patient's gender"
                                    },
                                    "phone": {
                                        "type": "string",
                                        "description": "Patient's contact number"
                                    }
                                },
                                "required": ["name", "age", "gender", "phone"]
                            },
                            "appointment_details": {
                                "type": "object",
                                "description": "Details of the appointment",
                                "properties": {
                                    "doctor_id": {
                                        "type": "string",
                                        "description": "ID of the selected doctor"
                                    },
                                    "doctor_name": {
                                        "type": "string",
                                        "description": "Name of the selected doctor"
                                    },
                                    "hospital_name": {
                                        "type": "string",
                                        "description": "Name of the hospital"
                                    },
                                    "appointment_date": {
                                        "type": "string",
                                        "description": "Date of the appointment (YYYY-MM-DD)"
                                    },
                                    "appointment_time": {
                                        "type": "string",
                                        "description": "Time of the appointment (HH:MM)"
                                    },
                                    "symptoms": {
                                        "type": "string",
                                        "description": "Patient's symptoms"
                                    }
                                },
                                "required": ["doctor_id", "doctor_name", "hospital_name", "appointment_date", "appointment_time", "symptoms"]
                            }
                        },
                        "required": ["user_id", "conversation_id", "patient_details", "appointment_details"]
                    }
                }
            }
        ]
            
    async def _process_individual_tool_call(
        self, 
        tool_call_obj,
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Helper to process a single tool call and return its result along with identifiers.
        Designed for use with asyncio.gather for concurrent execution.
        
        Args:
            tool_call_obj: A tool call object from the OpenAI API response
            user_id: Optional user ID from the generate API
            conversation_id: Optional conversation ID from the generate API
            
        Returns:
            Dictionary containing id, function_name, and result for the tool call
        """
        # Initialize result_json_str with a default error message
        result_json_str = json.dumps({"error": "Tool processing failed before execution."})

        if tool_call_obj.type != TYPE_FUNCTION:
            logger.warning(f"Skipping non-function tool call of type: {tool_call_obj.type}")
            result_json_str = json.dumps({"error": "Unsupported tool call type"})
            function_name = "unknown"
        else:
            function_call = tool_call_obj.function
            function_name = function_call.name
            try:
                result_json_str = await self._handle_tool_call(
                    function_call,
                    user_id=user_id,
                    conversation_id=conversation_id
                )
            except Exception as e:
                logger.error(f"Error processing tool_call ID {tool_call_obj.id} for function {function_name}: {e}", exc_info=True)
                # Assign the specific error JSON string to result_json_str
                result_json_str = json.dumps({
                    "error": f"Failed to execute tool {function_name}",
                    "details": str(e)
                })

        return {
            "id": tool_call_obj.id,
            "function_name": function_name,
            "result": result_json_str
        }
            
    async def generate_response(
        self,
        prompt: str,
        conversation_id: Optional[str] = None,
        user_id: Optional[str] = None,
        previous_response_id: Optional[str] = None,
    ) -> StructuredResponse:
        """
        Generate a response using OpenAI's API.
        
        Args:
            prompt: The user's input text
            conversation_id: Optional ID for continuing conversations
            user_id: Optional user identifier
            previous_response_id: Optional ID of the previous response
            
        Returns:
            A structured response object
        """
        # Generate a response_id once at the beginning and reuse it throughout
        response_id = str(uuid.uuid4())

        if self.client is None:
            logger.error("OpenAI client is not initialized. Cannot generate response.")
            # Ensure conversation_id is generated if None, for the error response
            effective_conversation_id = conversation_id or memory_service.generate_conversation_id(user_id)
            return TextResponse(
                response_id=response_id,
                conversation_id=effective_conversation_id,
                previous_response_id=previous_response_id,
                content=TextContent(text="Service configuration error. Please contact support.")
            )
        
        try:
            # Handle conversation ID and user association
            if conversation_id is None:
                # No conversation ID provided, create a new one
                conversation_id = memory_service.generate_conversation_id(user_id)
                logger.info(f"Created new conversation with ID: {conversation_id}")
            elif user_id is not None:
                # Both conversation_id and user_id provided - check if this is a new conversation for this user
                is_new_conversation = await memory_service.associate_conversation_with_user(conversation_id, user_id)
                if is_new_conversation:
                    # This is a new conversation for this user
                    await memory_service.add_message(
                        conversation_id,
                        {"role": ROLE_SYSTEM, "content": "New conversation started"},
                        user_id
                    )
                    logger.info(f"Associated existing conversation {conversation_id} with user {user_id}")
            
            # Add user message to memory
            await memory_service.add_message(
                conversation_id,
                {"role": ROLE_USER, "content": prompt},
                user_id
            )
            
            # Retrieve conversation history
            conversation_history = await memory_service.get_messages(conversation_id)
            
            # Format messages for the OpenAI API
            messages = self._prepare_messages(conversation_history)
            
            # Generate response from OpenAI with function calling
            try:
                response = await self.client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=messages,
                    temperature=settings.TEMPERATURE,
                    response_format={"type": "json_object"},
                    tools=self.tools,
                    tool_choice="auto"
                )
                
                # Log response structure only in development mode
                if settings.DEVELOPMENT_MODE:
                    logger.info(f"API Response type: {type(response)}")
                    if hasattr(response, 'model'):
                        logger.info(f"API Response model: {response.model}")
                    
                    if hasattr(response, 'choices') and response.choices:
                        msg_for_log = response.choices[0].message
                        logger.info(f"Message role: {msg_for_log.role}")
                        if msg_for_log.content:
                            logger.info(f"Message content (preview): {msg_for_log.content[:100]}")
                        if msg_for_log.tool_calls:
                            logger.info(f"Message tool_calls: {[(tc.type, tc.function.name if tc.function else 'N/A') for tc in msg_for_log.tool_calls]}")
                
                # Get the message from the response
                message = response.choices[0].message if hasattr(response, 'choices') and response.choices else None
                model = response.model if hasattr(response, 'model') else settings.OPENAI_MODEL
                
                # Check if the model wants to call a function
                if (message and hasattr(message, 'tool_calls') and message.tool_calls):
                    if settings.DEVELOPMENT_MODE:
                        logger.info(f"Message contains {len(message.tool_calls)} tool call(s). Processing concurrently.")
                    
                    # Create a list of coroutines for concurrent execution
                    tool_processing_coroutines = []
                    for tool_call in message.tool_calls:
                        if tool_call.type == TYPE_FUNCTION:
                            tool_processing_coroutines.append(
                                self._process_individual_tool_call(tool_call, user_id, conversation_id)
                            )
                    
                    # Execute all tool calls concurrently
                    processed_tool_outputs = await asyncio.gather(*tool_processing_coroutines)
                    
                    # Reconstruct tool_call_results for sending back to memory and API
                    tool_call_results = []
                    for output in processed_tool_outputs:
                        tool_call_results.append({
                            "id": output["id"],
                            "function": output["function_name"],
                            "result": output["result"]
                        })
                    
                    # Add assistant's tool call to the conversation history
                    tool_calls = [
                        {
                            "id": tc.id,
                            "type": tc.type,
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in message.tool_calls if tc.type == TYPE_FUNCTION
                    ]
                    await memory_service.add_message(
                        conversation_id,
                        {
                            "role": ROLE_ASSISTANT,
                            "content": None,
                            "tool_calls": tool_calls
                        }
                    )
                    
                    # Add tool results to the conversation history
                    for result in tool_call_results:
                        await memory_service.add_message(
                            conversation_id,
                            {
                                "role": ROLE_TOOL,
                                "content": result["result"],
                                "tool_call_id": result["id"]
                            },
                            user_id
                        )
                    
                    # Get updated conversation history with tool results
                    updated_messages = self._prepare_messages(await memory_service.get_messages(conversation_id))
                    
                    # Log the updated messages for debugging
                    if settings.DEVELOPMENT_MODE:
                        logger.info(f"Updated messages for second API call: {json.dumps(updated_messages)[:500]}...")
                    
                    # Generate a second response that includes the function results
                    try:
                        # Add a reminder about JSON schema for the second response
                        reminder_message = {
                            "role": ROLE_SYSTEM,
                            "content": "IMPORTANT: Your response MUST be a valid JSON object following one of the schema formats defined earlier. The response should be a single JSON object with the correct structure - no additional text. Use the appropriate structure based on the content type (text, button, list, or call_to_action)."
                        }
                        updated_messages.append(reminder_message)
                        
                        second_response = await self.client.chat.completions.create(
                            model=settings.OPENAI_MODEL,
                            messages=updated_messages,
                            temperature=settings.TEMPERATURE,
                            response_format={"type": "json_object"}
                        )
                        
                        # Extract the content from the second response
                        content = self._extract_json_content_from_response(second_response)
                    except Exception as second_call_error:
                        logger.error(f"Error in second API call after tool response: {str(second_call_error)}", exc_info=True)
                        # Fallback response when the tool call flow breaks
                        content = json.dumps({
                            "type": TYPE_TEXT,
                            "content": {
                                "text": "I'm sorry, I encountered an error processing your request. Please try again."
                            }
                        })
                    
                    # Add final assistant response to memory
                    await memory_service.add_message(
                        conversation_id,
                        {"role": ROLE_ASSISTANT, "content": content},
                        user_id
                    )
                else:
                    # No tool calls, just a regular response
                    if settings.DEVELOPMENT_MODE:
                        logger.info("Response contains no tool calls, processing as regular response")
                    
                    # Now extract the text content from the direct response
                    content = self._extract_json_content_from_response(response)
                    
                    # Add regular assistant message to memory
                    await memory_service.add_message(
                        conversation_id,
                        {"role": ROLE_ASSISTANT, "content": content},
                        user_id
                    )
                
                # Parse JSON content
                try:
                    # Ensure content is a non-empty string before parsing
                    if not content or not isinstance(content, str):
                        if settings.DEVELOPMENT_MODE:
                            logger.warning(f"Invalid content format for JSON parsing: {type(content)}")
                        content = json.dumps({
                            "type": TYPE_TEXT,
                            "content": {
                                "text": "I'm sorry, I encountered an error processing your request. Please try again."
                            }
                        })
                        
                    parsed_content = json.loads(content)
                except (json.JSONDecodeError, TypeError) as json_error:
                    logger.error(f"Failed to parse JSON response: {str(json_error)}, Content: {content[:200] if content else 'None'}")
                    # Fall back to default text response
                    parsed_content = {
                        "type": TYPE_TEXT,
                        "content": {
                            "text": "I'm sorry, I encountered an error processing your request. Please try again."
                        }
                    }
                
                # Handle different response types (text, button, list, etc.)
                structured_response = self._create_structured_response(
                    parsed_content, conversation_id, response_id, previous_response_id
                )
                
                # Return the structured response
                return structured_response
                
            except (APIError, RateLimitError, APIConnectionError, AuthenticationError) as api_error:
                # Handle different types of OpenAI errors with appropriate messages
                error_message = "I'm sorry, I encountered an error processing your request."
                
                if isinstance(api_error, RateLimitError):
                    logger.error(f"OpenAI Rate limit exceeded: {str(api_error)}", exc_info=True)
                    error_message = "I'm experiencing high demand right now. Please try again in a few moments."
                elif isinstance(api_error, AuthenticationError):
                    logger.error(f"OpenAI Authentication error: {str(api_error)}", exc_info=True)
                    error_message = "There's a configuration issue with the service. Please contact support."
                elif isinstance(api_error, APIConnectionError):
                    logger.error(f"OpenAI API Connection error: {str(api_error)}", exc_info=True)
                    error_message = "I'm having trouble connecting to my services. Please check your internet connection and try again."
                else:
                    logger.error(f"OpenAI API error: {str(api_error)}", exc_info=True)
                
                # Create a fallback text response with the appropriate error message
                return TextResponse(
                    response_id=response_id,
                    conversation_id=conversation_id,
                    previous_response_id=previous_response_id,
                    content=TextContent(text=error_message)
                )
                
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}", exc_info=True)
            # Create a fallback text response
            return TextResponse(
                response_id=response_id,
                conversation_id=conversation_id or memory_service.generate_conversation_id(user_id),
                previous_response_id=previous_response_id,
                content=TextContent(
                    text="I'm sorry, I encountered an error processing your request. Please try again."
                )
            )
    
    async def _handle_tool_call(self, function_call, user_id: Optional[str] = None, conversation_id: Optional[str] = None) -> str:
        """
        Handle a single function call from the OpenAI response.
        
        Args:
            function_call: A function call from the OpenAI completions API
            user_id: Optional user ID from the generate API
            conversation_id: Optional conversation ID from the generate API
            
        Returns:
            Result from the function call as a JSON string
        """
        result = {}
        
        try:
            if function_call.name == FUNCTION_GET_SERVICE_INFO:
                arguments_str_or_dict = function_call.arguments
                args = None

                if isinstance(arguments_str_or_dict, dict):
                    args = arguments_str_or_dict
                elif isinstance(arguments_str_or_dict, str):
                    try:
                        args = json.loads(arguments_str_or_dict)
                    except json.JSONDecodeError as json_error:
                        logger.error(f"JSON decode error parsing arguments string for {function_call.name}: {str(json_error)} - Content: '{arguments_str_or_dict[:200]}'")
                        return json.dumps({"error": f"Invalid arguments format for {function_call.name}: Malformed JSON string."})
                else:
                    logger.error(f"Unexpected type for arguments in {function_call.name}: {type(arguments_str_or_dict)}")
                    return json.dumps({"error": f"Invalid arguments type for {function_call.name}. Expected string or dict."})

                if args is None:
                    logger.error(f"Argument parsing failed for {function_call.name} without specific error.")
                    return json.dumps({"error": f"Argument parsing failed for {function_call.name}."})
                        
                query = args.get("query", "").strip()
                location = args.get("location", "").strip()
                specialty = args.get("specialty", "").strip()
                symptoms = args.get("symptoms", "").strip()
                
                # Ensure we have a valid query
                if not query:
                    query = "information about doctors"
                
                # Build a comprehensive prompt for Gemini using joined parts for cleaner construction
                gemini_prompt_parts = ["I need information about"]
                
                if specialty:
                    gemini_prompt_parts.append(f"{specialty} doctors")
                else:
                    gemini_prompt_parts.append("doctors")
                
                if location:
                    gemini_prompt_parts.append(f"in {location}")
                
                if symptoms:
                    gemini_prompt_parts.append(f"for treating {symptoms}")
                
                # Add the main query at the end
                gemini_prompt_parts.append(f". {query}")
                
                # Join all parts with spaces
                gemini_prompt = " ".join(gemini_prompt_parts)
                
                # Log the constructed prompt
                logger.info(f"Constructed Gemini prompt: {gemini_prompt[:500]}...")
                
                # Get service info from Gemini
                try:
                    gemini_response = await gemini_service.get_service_info(gemini_prompt)
                    
                    # Handle structured response from Gemini service
                    if gemini_response["success"]:
                        service_info = gemini_response["data"]
                        
                        # Ensure service_info is a string
                        if not isinstance(service_info, str):
                            logger.warning(f"Gemini service_info is not a string: {type(service_info)}. Attempting to convert to string.")
                            service_info = str(service_info)
                    else:
                        # Use the error message from the structured response
                        logger.warning(f"Received error from Gemini service: {gemini_response['error']}")
                        service_info = gemini_response["message"]
                except Exception as gemini_error:
                    logger.error(f"Gemini service error for {function_call.name}: {str(gemini_error)}", exc_info=True)
                    service_info = "I'm sorry, I encountered a technical issue retrieving healthcare information. Please try again."
                
                # Store result
                result = {
                    "service_info": service_info,
                    "location": location,
                    "specialty": specialty,
                    "symptoms": symptoms,
                    "query": query
                }
            elif function_call.name == FUNCTION_GET_CONFIRMATION:
                # Parse arguments
                try:
                    if isinstance(function_call.arguments, str):
                        args = json.loads(function_call.arguments)
                    else:
                        args = function_call.arguments
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse confirmation arguments: {str(e)}")
                    return json.dumps({
                        "success": False,
                        "error": "invalid_arguments",
                        "message": "Failed to parse appointment confirmation details."
                    })

                # Use the user_id and conversation_id from the generate API
                api_user_id = user_id
                api_conversation_id = conversation_id

                # Extract other required data
                patient_details = args.get("patient_details", {})
                appointment_details = args.get("appointment_details", {})

                # Validate required fields
                if not all([api_user_id, api_conversation_id, patient_details, appointment_details]):
                    logger.error("Missing required fields in confirmation request")
                    return json.dumps({
                        "success": False,
                        "error": "missing_fields",
                        "message": "Missing required fields in appointment confirmation request."
                    })

                try:
                    # Prepare the request payload
                    payload = {
                        "user_id": api_user_id,
                        "conversation_id": api_conversation_id,
                        "patient_details": patient_details,
                        "appointment_details": appointment_details
                    }

                    # Log the payload for debugging
                    if settings.DEVELOPMENT_MODE:
                        logger.info(f"Sending confirmation payload: {json.dumps(payload)}")

                    # Make the POST request to the confirmation endpoint
                    async with aiohttp.ClientSession() as session:
                        async with session.post(
                            "https://admin.n8n.healthnivaran.in/webhook/appointment/confirmation",
                            json=payload,
                            headers={"Content-Type": "application/json"}
                        ) as response:
                            response_text = await response.text()
                            
                            # Try to parse as JSON first
                            try:
                                response_data = json.loads(response_text)
                            except json.JSONDecodeError:
                                # If not JSON, use the text response
                                response_data = {"message": response_text}

                            if response.status == 200:
                                return json.dumps({
                                    "success": True,
                                    "message": "Appointment confirmed successfully",
                                    "data": response_data
                                })
                            else:
                                logger.error(f"Confirmation API error: Status {response.status}, Response: {response_text}")
                                return json.dumps({
                                    "success": False,
                                    "error": "api_error",
                                    "message": f"Failed to confirm appointment. Status: {response.status}"
                                })

                except aiohttp.ClientError as e:
                    logger.error(f"Network error during confirmation request: {str(e)}")
                    return json.dumps({
                        "success": False,
                        "error": "network_error",
                        "message": "Failed to connect to confirmation service. Please try again."
                    })
                except Exception as e:
                    logger.error(f"Unexpected error during confirmation: {str(e)}")
                    return json.dumps({
                        "success": False,
                        "error": "unexpected_error",
                        "message": "An unexpected error occurred during appointment confirmation."
                    })

            else:
                # Handle unknown function calls
                logger.warning(f"Unknown function call encountered: {function_call.name}")
                result = {"error": f"Function {function_call.name} is not implemented."}
        except Exception as e:
            logger.error(f"Error processing function call {function_call.name if hasattr(function_call, 'name') else 'unknown'}: {str(e)}")
            result = {
                "error": f"Failed to process request: {str(e)}"
            }
    
        return json.dumps(result)
    
    def _needs_doctor_info(self, prompt: str, conversation_history: List[Dict[str, Any]]) -> bool:
        """
        Determine if doctor information is needed based on the prompt and conversation history.
        Note: This method is currently not used in the main flow but is kept for potential future use.
        
        Args:
            prompt: The user's input text
            conversation_history: The conversation history
            
        Returns:
            True if doctor information is needed, False otherwise
        """
        # Check if the prompt contains keywords related to doctors
        doctor_keywords = ["doctor", "specialist", "physician", "hospital", "clinic", 
                         "medical", "appointment", "consult", "diagnosis", "treatment"]
                         
        if any(keyword in prompt.lower() for keyword in doctor_keywords):
            return True
            
        # Check conversation state for doctor-related content, but only if history is not empty
        if conversation_history and len(conversation_history) > 0:
            conv_id = conversation_history[0].get("conversation_id", "")
            state = memory_service.get_conversation_state(conv_id)
            if state and state.get("mentioned_doctor_search", False):
                return True
            
        return False
        
    def _prepare_messages(self, conversation_history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Prepare messages for the OpenAI API.
        
        Args:
            conversation_history: The conversation history
            
        Returns:
            List of messages for the OpenAI API
        """
        
        # Get current date and time information
        now = datetime.datetime.now()
        current_date = now.strftime("%d-%m-%Y")
        current_time = now.strftime("%H:%M")
        current_day = now.strftime("%A")
        
        # Replace placeholders in the system prompt
        system_prompt = DEFAULT_SYSTEM_PROMPT.replace("{current_date}", current_date)
        system_prompt = system_prompt.replace("{current_time}", current_time)
        system_prompt = system_prompt.replace("{current_day}", current_day)
        
        messages = [{"role": ROLE_SYSTEM, "content": system_prompt}]
        
        # Log initial history for debugging
        if settings.DEVELOPMENT_MODE:
            logger.debug(f"Raw conversation history: {json.dumps(conversation_history)[:500]}...")
        
        # Add conversation history
        for message in conversation_history:
            role = message.get("role")
            
            if role == ROLE_SYSTEM:
                # Handle system messages
                if message.get("content") == DEFAULT_SYSTEM_PROMPT:
                    # Skip duplicate system messages with exact same content as default prompt
                    continue
                else:
                    # Include other system messages
                    messages.append({
                        "role": ROLE_SYSTEM,
                        "content": message.get("content", "")
                    })
                
            elif role == ROLE_TOOL:
                # Format tool messages correctly for OpenAI API
                if "tool_call_id" not in message:
                    logger.warning("Missing tool_call_id in tool message") if settings.DEVELOPMENT_MODE else None
                    continue
                    
                messages.append({
                    "role": ROLE_TOOL,
                    "content": message.get("content", ""),
                    "tool_call_id": message.get("tool_call_id")
                })
            elif role == ROLE_ASSISTANT and message.get("tool_calls"):
                # Handle assistant messages with tool_calls
                assistant_message = {"role": ROLE_ASSISTANT}
                
                # Add content if it exists
                if message.get("content"):
                    assistant_message["content"] = message.get("content")
                else:
                    assistant_message["content"] = None
                
                # Add tool calls if they exist
                if message.get("tool_calls"):
                    tool_calls = []
                    for tool_call in message.get("tool_calls", []):
                        if tool_call.get("type") == TYPE_FUNCTION:
                            tool_calls.append({
                                "id": tool_call.get("id", ""),
                                "type": tool_call.get("type", ""),
                                "function": {
                                    "name": tool_call.get("function", {}).get("name", ""),
                                    "arguments": tool_call.get("function", {}).get("arguments", "")
                                }
                            })
                    
                    if tool_calls:
                        assistant_message["tool_calls"] = tool_calls
                        
                messages.append(assistant_message)
            elif role in [ROLE_USER, ROLE_ASSISTANT]:
                # Regular user or assistant message
                messages.append({
                    "role": role,
                    "content": message.get("content", "")
                })
            else:
                # Log unhandled message roles
                logger.warning(f"Skipping message with unhandled role: {role}")
        
        return messages
        
    def _create_structured_response(
        self, content: Dict[str, Any], conversation_id: str, response_id: str, 
        previous_response_id: Optional[str] = None
    ) -> StructuredResponse:
        """
        Create a structured response based on the content type.
        
        Args:
            content: The parsed JSON content
            conversation_id: The conversation ID
            response_id: The response ID
            previous_response_id: Optional ID of the previous response for continuity
            
        Returns:
            A structured response object
        """
        # Import response models here to avoid circular imports
        from app.models.response_models import (
            TextResponse, TextContent,
            ButtonResponse, ButtonContent, ButtonBody, ButtonAction, Button, ButtonReply,
            ListResponse, ListContent, ListBody, ListAction, ListSection, ListRow,
            CallToActionResponse, CallToActionContent, CallToActionParameters
        )
        
        # Determine response type
        response_type = content.get("type", TYPE_TEXT)
        
        if response_type == TYPE_TEXT:
            text = content.get("content", {}).get("text", "I'm sorry, I couldn't generate a proper response.")
            return TextResponse(
                response_id=response_id,
                conversation_id=conversation_id,
                previous_response_id=previous_response_id,
                content=TextContent(text=text)
            )
            
        elif response_type == TYPE_BUTTON:
            body_text = content.get("content", {}).get("body", {}).get("text", "Please select an option:")
            
            # Extract buttons
            buttons_data = content.get("content", {}).get("action", {}).get("buttons", [])
            buttons = []
            
            for button_data in buttons_data:
                reply_data = button_data.get("reply", {})
                buttons.append(
                    Button(
                        reply=ButtonReply(
                            id=reply_data.get("id", f"button_{len(buttons)}"),
                            title=reply_data.get("title", "Option")
                        )
                    )
                )
            
            # Log warning if buttons list is empty
            if not buttons:
                logger.warning(f"Button response for conv {conversation_id} has no buttons. Parsed content: {content}")
                
            return ButtonResponse(
                response_id=response_id,
                conversation_id=conversation_id,
                previous_response_id=previous_response_id,
                content=ButtonContent(
                    body=ButtonBody(text=body_text),
                    action=ButtonAction(buttons=buttons)
                )
            )
            
        elif response_type == TYPE_LIST:
            body_text = content.get("content", {}).get("body", {}).get("text", "Here are the available options:")
            button_text = content.get("content", {}).get("action", {}).get("button", "View List")
            
            # Extract sections
            sections_data = content.get("content", {}).get("action", {}).get("sections", [])
            sections = []
            
            for section_data in sections_data:
                section_title = section_data.get("title", "Options")
                rows = []
                
                for row_data in section_data.get("rows", []):
                    rows.append(
                        ListRow(
                            id=row_data.get("id", f"row_{len(rows)}"),
                            title=row_data.get("title", "Item"),
                            description=row_data.get("description", "")
                        )
                    )
                
                # Log warning if rows list is empty for a section
                if not rows:
                    logger.warning(f"List section '{section_title}' for conv {conversation_id} has no rows")
                    
                sections.append(
                    ListSection(
                        title=section_title,
                        rows=rows
                    )
                )
                
            # Log warning if sections list is empty
            if not sections:
                logger.warning(f"List response for conv {conversation_id} has no sections. Parsed content: {content}")
                
            return ListResponse(
                response_id=response_id,
                conversation_id=conversation_id,
                previous_response_id=previous_response_id,
                content=ListContent(
                    body=ListBody(text=body_text),
                    action=ListAction(
                        button=button_text,
                        sections=sections
                    )
                )
            )
            
        elif response_type == TYPE_CALL_TO_ACTION:
            display_text = content.get("content", {}).get("parameters", {}).get("display_text", "Click here")
            url = content.get("content", {}).get("parameters", {}).get("url", "")
            
            # Validate URL is not empty
            if not url:
                logger.error(f"CallToAction response for conv {conversation_id} is missing a URL. Parsed content: {content}")
                return TextResponse(
                    response_id=response_id,
                    conversation_id=conversation_id,
                    previous_response_id=previous_response_id,
                    content=TextContent(text="I tried to provide a link, but the URL is missing. Please try again.")
                )
            
            return CallToActionResponse(
                response_id=response_id,
                conversation_id=conversation_id,
                previous_response_id=previous_response_id,
                content=CallToActionContent(
                    name="cta_url",
                    parameters=CallToActionParameters(
                        display_text=display_text,
                        url=url
                    )
                )
            )
            
        else:
            # Default to text response if type is not recognized
            logger.warning(f"Unknown response type '{response_type}' for conv {conversation_id}")
            return TextResponse(
                response_id=response_id,
                conversation_id=conversation_id,
                previous_response_id=previous_response_id,
                content=TextContent(
                    text="I'm sorry, I don't understand the response type."
                )
            )
            
    def clear_conversation_history(self, conversation_id: str) -> bool:
        """
        Clear the conversation history for a given conversation ID.
        
        Args:
            conversation_id: The conversation ID to clear
            
        Returns:
            True if successful, False otherwise
        """
        return memory_service.clear_conversation(conversation_id)

    def _extract_json_content_from_response(self, response) -> str:
        """
        Extracts the message.content (expected to be a JSON string) from an OpenAI response object.
        Returns a fallback JSON string if content is not found or an error occurs.
        
        Args:
            response: The OpenAI API response object
            
        Returns:
            JSON content as string or fallback JSON if extraction fails
        """
        default_error_json = json.dumps({
            "type": TYPE_TEXT,
            "content": {
                "text": "I'm sorry, I couldn't generate a proper response. Please try again."
            }
        })

        try:
            if not response:
                logger.warning("Response object is None.")
                return default_error_json

            if hasattr(response, 'choices') and response.choices:
                choice = response.choices[0]
                if hasattr(choice, 'message'):
                    message = choice.message
                    if hasattr(message, 'content') and message.content and isinstance(message.content, str):
                        # Attempt to parse to ensure it's valid JSON, though we return the string
                        try:
                            json.loads(message.content)
                            if settings.DEVELOPMENT_MODE:
                                logger.info(f"Extracted message content: {message.content[:100]}...")
                            return message.content
                        except json.JSONDecodeError:
                            logger.warning(f"message.content is not a valid JSON string: {message.content[:200]}")
                            return default_error_json
                    else:
                        # message.content is None, empty, or not a string
                        logger.warning(f"message.content is missing, empty, or not a string. Type: {type(message.content)}")
                        if hasattr(message, 'tool_calls') and message.tool_calls:
                            logger.warning("Found tool_calls in response when direct content was expected, but content was empty.")
                        return default_error_json
                else:
                    logger.warning("No 'message' attribute in response choice.")
                    return default_error_json
            else:
                logger.warning("No 'choices' attribute in response or 'choices' is empty.")
                return default_error_json
        except AttributeError as e:
            logger.error(f"Attribute error while extracting content from response: {str(e)}", exc_info=True)
            return default_error_json
        except Exception as e:
            logger.error(f"Unexpected error extracting json content from response: {str(e)}", exc_info=True)
            return default_error_json

# Create singleton instance
ai_service = AIService()
