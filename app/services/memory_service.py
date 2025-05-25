"""
Memory management service for chatbot conversations.
Provides efficient Redis-backed memory for conversations.
"""

import logging
import uuid
import json
import time
import redis.asyncio as redis
import atexit
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timedelta

from app.config.settings import settings

# Configure logging
logger = logging.getLogger(__name__)

class MemoryService:
    """Service for managing conversation memory using Redis as a backend."""
    
    def __init__(self, 
                max_conversations=None, 
                expiry_hours=None, 
                cleanup_interval=3600):
        # Configuration for memory management
        self.max_conversations = max_conversations or settings.REDIS_MAX_CONVERSATIONS
        self.expiry_hours = expiry_hours or settings.REDIS_CONVERSATIONS_TTL_HOURS
        self.cleanup_interval = cleanup_interval  # Seconds between cleanup runs
        self.expiry_seconds = self.expiry_hours * 3600  # Convert hours to seconds for Redis TTL
        
        # Initialize Redis connection
        self.redis = None
        # Don't immediately connect - connection will happen on first use
        # This is better for async applications
        
        # Redis key prefixes for different data types
        self.CONV_META_PREFIX = "conv:meta:"      # Metadata about conversations (Hash)
        self.CONV_MSGS_PREFIX = "conv:msgs:"      # Messages in conversations (List)
        self.CONV_STATE_PREFIX = "conv:state:"    # Conversation state (Hash)
        self.USER_CONV_PREFIX = "user:conv:"      # User to conversation mapping (String)
        self.CONV_INDEX_KEY = "conv:index"        # Sorted set of conversations by update time (ZSet)
    
    async def _setup_redis_connection(self):
        """Set up the Redis connection with fallback options if SSL fails."""
        if self.redis is not None:
            # Already connected
            return self.redis
            
        # First, try with the configured settings
        try:
            connection_params = {
                "host": settings.REDIS_HOST,
                "port": settings.REDIS_PORT,
                "decode_responses": settings.REDIS_DECODE_RESPONSES,
                "username": settings.REDIS_USERNAME if settings.REDIS_USERNAME else None,
                "password": settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
                "ssl": settings.REDIS_SSL,
            }
            
            # Log connection attempt
            ssl_status = "with SSL" if settings.REDIS_SSL else "without SSL"
            logger.info(f"Connecting to Redis at {settings.REDIS_HOST}:{settings.REDIS_PORT} {ssl_status}")
            
            # Try to establish connection
            self.redis = redis.Redis(**connection_params)
            await self.redis.ping()
            logger.info(f"Successfully connected to Redis at {settings.REDIS_HOST}:{settings.REDIS_PORT}")
            
            # Register cleanup on application exit
            atexit.register(self._close_redis_connection)
            return self.redis
            
        except redis.ConnectionError as e:
            # If SSL is enabled and we get a connection error, try without SSL
            if settings.REDIS_SSL:
                logger.warning(f"SSL connection to Redis failed: {str(e)}. Trying without SSL.")
                try:
                    # Try again without SSL
                    connection_params["ssl"] = False
                    self.redis = redis.Redis(**connection_params)
                    await self.redis.ping()
                    logger.info(f"Successfully connected to Redis at {settings.REDIS_HOST}:{settings.REDIS_PORT} without SSL")
                    
                    # Register cleanup on application exit
                    atexit.register(self._close_redis_connection)
                    return self.redis
                except Exception as e2:
                    logger.error(f"Non-SSL Redis connection also failed: {str(e2)}")
            
            # If we're here, both connection attempts failed or SSL was not enabled
            logger.error(f"Failed to connect to Redis: {str(e)}")
            raise
    
    def _close_redis_connection(self):
        """Close the Redis connection when the application exits."""
        async def close_async():
            try:
                if hasattr(self, 'redis') and self.redis:
                    await self.redis.close()
                    logger.info("Redis connection closed")
            except Exception as e:
                logger.error(f"Error closing Redis connection: {e}")
        
        # We need to run the async close in a new event loop
        # This is generally not ideal, but for cleanup on app exit it's acceptable
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(close_async())
            else:
                asyncio.run(close_async())
        except Exception as e:
            logger.error(f"Error in Redis cleanup: {e}")
    
    def _get_conv_meta_key(self, conversation_id: str) -> str:
        """Get the Redis key for conversation metadata."""
        return f"{self.CONV_META_PREFIX}{conversation_id}"
    
    def _get_conv_msgs_key(self, conversation_id: str) -> str:
        """Get the Redis key for conversation messages."""
        return f"{self.CONV_MSGS_PREFIX}{conversation_id}"
    
    def _get_conv_state_key(self, conversation_id: str) -> str:
        """Get the Redis key for conversation state."""
        return f"{self.CONV_STATE_PREFIX}{conversation_id}"
    
    def _get_user_conv_key(self, user_id: str) -> str:
        """Get the Redis key for user to conversation mapping."""
        return f"{self.USER_CONV_PREFIX}{user_id}"
    
    def _serialize(self, data: Any) -> str:
        """
        Serialize data structures to JSON string.
        Ensures all data is JSON-serializable by design.
        
        Args:
            data: The data to serialize
            
        Returns:
            JSON string representation
            
        Raises:
            TypeError: If data cannot be JSON serialized
        """
        if isinstance(data, datetime):
            return data.isoformat()
        elif isinstance(data, set):
            return json.dumps(list(data))
        else:
            try:
                return json.dumps(data)
            except (TypeError, OverflowError) as e:
                # Instead of falling back to pickle, log the error and raise a more helpful exception
                logger.error(f"Non-serializable data encountered: {type(data)}. Error: {str(e)}")
                # Convert the problematic data to a string representation as a last resort
                fallback_data = {"error": "Non-serializable data", "string_repr": str(data)}
                return json.dumps(fallback_data)
    
    def _deserialize(self, data: str, data_type: str = None) -> Any:
        """
        Deserialize JSON string to appropriate data structure.
        
        Args:
            data: The string to deserialize
            data_type: Optional hint about the expected data type
            
        Returns:
            Deserialized data structure
        """
        if not data:
            return None
            
        if data_type == "datetime":
            return datetime.fromisoformat(data)
        elif data_type == "set":
            return set(json.loads(data))
        else:
            try:
                return json.loads(data)
            except json.JSONDecodeError as e:
                # Log the error and return a structured error object instead of trying pickle
                logger.error(f"Failed to deserialize data: {str(e)}")
                return {"error": "Deserialization failed", "raw_data": data[:100] + "..." if len(data) > 100 else data}
    
    def _serialize_message(self, message: Dict[str, Any]) -> str:
        """Serialize a message dictionary to JSON string."""
        return json.dumps(message)
    
    def _deserialize_message(self, message_str: str) -> Dict[str, Any]:
        """Deserialize a JSON string to a message dictionary."""
        return json.loads(message_str)
    
    async def _enforce_max_conversations(self):
        """
        Enforce the maximum number of conversations by removing oldest ones.
        Uses Redis pipeline for bulk operations to improve efficiency.
        """
        # Ensure Redis connection
        if not self.redis:
            await self._setup_redis_connection()
            
        # Get the total number of conversations
        conv_count = await self.redis.zcard(self.CONV_INDEX_KEY)
        
        if conv_count > self.max_conversations:
            # Calculate how many to remove
            remove_count = conv_count - self.max_conversations
            
            # Get the oldest conversation IDs
            oldest_convs = await self.redis.zrange(self.CONV_INDEX_KEY, 0, remove_count - 1)
            
            if oldest_convs:
                logger.info(f"Enforcing max conversations limit, removing {len(oldest_convs)} oldest conversations")
                
                # Create a pipeline for bulk operations
                pipeline = self.redis.pipeline()
                
                # Collect all keys to delete in batch
                conv_meta_keys = []
                conv_msgs_keys = []
                conv_state_keys = []
                
                # First pass: collect keys and user IDs
                user_ids = []
                for conv_id in oldest_convs:
                    # Get user ID associated with this conversation
                    user_id = await self.redis.hget(self._get_conv_meta_key(conv_id), "user_id")
                    if user_id:
                        user_ids.append(user_id)
                    
                    # Add keys to lists for batch deletion
                    conv_meta_keys.append(self._get_conv_meta_key(conv_id))
                    conv_msgs_keys.append(self._get_conv_msgs_key(conv_id))
                    conv_state_keys.append(self._get_conv_state_key(conv_id))
                
                # Second pass: bulk operations in pipeline
                # Delete user to conversation mappings
                for user_id in user_ids:
                    pipeline.delete(self._get_user_conv_key(user_id))
                
                # Delete all conversation keys in batches
                if conv_meta_keys:
                    pipeline.delete(*conv_meta_keys)
                if conv_msgs_keys:
                    pipeline.delete(*conv_msgs_keys)
                if conv_state_keys:
                    pipeline.delete(*conv_state_keys)
                
                # Remove from the conversation index
                pipeline.zrem(self.CONV_INDEX_KEY, *oldest_convs)
                
                # Execute all deletions in a single atomic operation
                await pipeline.execute()
                
                logger.debug(f"Bulk deleted {len(oldest_convs)} conversations")
    
    async def _delete_conversation(self, conversation_id: str):
        """
        Delete a conversation and all associated data from Redis.
        Uses a pipeline for atomic operations.
        """
        # Ensure Redis connection
        if not self.redis:
            await self._setup_redis_connection()
            
        # Create a pipeline for atomic operations
        pipeline = self.redis.pipeline()
        
        # Get user ID associated with this conversation
        user_id = await self.redis.hget(self._get_conv_meta_key(conversation_id), "user_id")
        
        # Delete user to conversation mapping if it exists
        if user_id:
            pipeline.delete(self._get_user_conv_key(user_id))
        
        # Delete conversation keys
        pipeline.delete(
            self._get_conv_meta_key(conversation_id),
            self._get_conv_msgs_key(conversation_id),
            self._get_conv_state_key(conversation_id)
        )
        
        # Remove from the conversation index
        pipeline.zrem(self.CONV_INDEX_KEY, conversation_id)
        
        # Execute all operations
        await pipeline.execute()
        
        logger.debug(f"Deleted conversation {conversation_id}")
    
    async def add_message(self, conversation_id: str, message: Dict[str, Any], user_id: Optional[str] = None) -> bool:
        """
        Add a message to the conversation history in Redis.
        
        Args:
            conversation_id: Unique identifier for the conversation
            message: Message to add (dict with 'role' and 'content' keys)
            user_id: Optional user identifier to associate with this conversation
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure Redis connection
            if not self.redis:
                await self._setup_redis_connection()
                
            # Serialize the message
            message_str = self._serialize_message(message)
            
            # Current timestamp for updates
            now = datetime.now()
            now_str = self._serialize(now)
            
            # Multi operations for atomicity
            pipeline = self.redis.pipeline()
            
            # If user_id is provided, associate this conversation with the user
            if user_id:
                pipeline.set(self._get_user_conv_key(user_id), conversation_id)
            
            # Check if conversation exists
            conv_meta_key = self._get_conv_meta_key(conversation_id)
            pipeline.exists(conv_meta_key)
                
            # Initialize conversation if it doesn't exist
            pipeline.hsetnx(conv_meta_key, "created_at", now_str)
            pipeline.hset(conv_meta_key, "updated_at", now_str)
            
            if user_id:
                pipeline.hsetnx(conv_meta_key, "user_id", user_id)
            
            # Add message to conversation list
            pipeline.rpush(self._get_conv_msgs_key(conversation_id), message_str)
            
            # Update conversation in the sorted index with current timestamp as score
            pipeline.zadd(self.CONV_INDEX_KEY, {conversation_id: now.timestamp()})
            
            # Set expiry on conversation keys
            pipeline.expire(conv_meta_key, self.expiry_seconds)
            pipeline.expire(self._get_conv_msgs_key(conversation_id), self.expiry_seconds)
            pipeline.expire(self._get_conv_state_key(conversation_id), self.expiry_seconds)
            
            # Execute all commands
            await pipeline.execute()
            
            # Update conversation state based on message content and role
            await self._update_conversation_state(conversation_id, message)
            
            # Enforce max conversation limit periodically
            if now.second % 10 == 0:  # Only check occasionally to reduce overhead
                await self._enforce_max_conversations()
                
                logger.debug(f"Added message to conversation {conversation_id}")
                return True
            
        except Exception as e:
            logger.error(f"Failed to add message to conversation {conversation_id}: {str(e)}")
            return False
    
    async def _update_conversation_state(self, conversation_id: str, message: Dict[str, Any]):
        """
        Update the state tracking for this conversation based on the message.
        
        Args:
            conversation_id: The conversation to update
            message: The message that was added
        """
        # Ensure Redis connection
        if not self.redis:
            await self._setup_redis_connection()
            
        conv_state_key = self._get_conv_state_key(conversation_id)
        
        # Initialize state tracking if needed - use a pipeline for multiple operations
        pipeline = self.redis.pipeline()
        
        # Track message type
        pipeline.hset(conv_state_key, "last_message_type", message.get("role", ""))
        
        # Check if conversation state exists
        pipeline.exists(conv_state_key)
        result = await pipeline.execute()
        exists = result[1]
        
        # Initialize state fields if they don't exist
        if not exists:
            pipeline = self.redis.pipeline()
            pipeline.hset(conv_state_key, "mentioned_doctor_search", "false")
            pipeline.hset(conv_state_key, "mentioned_symptoms", self._serialize([]))
            pipeline.hset(conv_state_key, "topics_discussed", self._serialize(set()))
            pipeline.hset(conv_state_key, "doctor_search_results", self._serialize({}))
            pipeline.hset(conv_state_key, "search_count", "0")
            await pipeline.execute()
        
        # Process based on message type
        role = message.get("role")
        
        # If this is a user message, analyze content
        if role == "user" and message.get("content"):
            content = message.get("content", "").lower()
            
            # Track doctor search mentions
            doctor_keywords = ["doctor", "specialist", "physician", "hospital", "medical"]
            if any(keyword in content for keyword in doctor_keywords):
                await self.redis.hset(conv_state_key, "mentioned_doctor_search", "true")
            
            # Track symptom mentions
            symptom_keywords = ["symptom", "pain", "ache", "fever", "cough", "sick", "ill"]
            if any(keyword in content for keyword in symptom_keywords):
                # Extract the sentence containing the symptom
                sentences = content.split(".")
                mentioned_symptoms = []
                
                # Get existing symptoms
                existing_symptoms_str = await self.redis.hget(conv_state_key, "mentioned_symptoms")
                if existing_symptoms_str:
                    mentioned_symptoms = self._deserialize(existing_symptoms_str)
                
                # Add new symptoms from this message
                for sentence in sentences:
                    if any(keyword in sentence for keyword in symptom_keywords):
                        mentioned_symptoms.append(sentence.strip())
                
                # Store updated symptoms list
                await self.redis.hset(conv_state_key, "mentioned_symptoms", self._serialize(mentioned_symptoms))
                        
            # Track topics from this message
            topics = self._extract_topics(content)
            if topics:
                # Get existing topics
                existing_topics_str = await self.redis.hget(conv_state_key, "topics_discussed")
                topics_discussed = set()
                
                if existing_topics_str:
                    topics_discussed = self._deserialize(existing_topics_str, "set")
                
                # Update with new topics
                topics_discussed.update(topics)
                await self.redis.hset(conv_state_key, "topics_discussed", self._serialize(topics_discussed))
        
        # If this is a tool response message, save doctor search results
        elif role == "tool" and message.get("content"):
            try:
                content = message.get("content")
                if isinstance(content, str) and "doctor" in content.lower():
                    result = json.loads(content)
                    
                    # If this is a doctor search result, cache it
                    if "type" in result and result["type"] == "list":
                        # Check for last_doctor_search_params
                        search_params_str = await self.redis.hget(conv_state_key, "last_doctor_search_params")
                        
                        if search_params_str:
                            search_params = self._deserialize(search_params_str)
                            
                            # Cache the doctor search result with its parameters
                            cache_key = self._get_cache_key(search_params)
                            
                            # Get existing doctor search results
                            results_str = await self.redis.hget(conv_state_key, "doctor_search_results")
                            doctor_search_results = {}
                            
                            if results_str:
                                doctor_search_results = self._deserialize(results_str)
                            
                            # Add this result to the cache
                            doctor_search_results[cache_key] = content
                            
                            # Update doctor_search_results in Redis
                            await self.redis.hset(conv_state_key, "doctor_search_results", 
                                           self._serialize(doctor_search_results))
                            
                            # Increment search count
                            await self.redis.hincrby(conv_state_key, "search_count", 1)
            except Exception as e:
                logger.debug(f"Error processing tool message: {e}")
                pass  # If parsing fails, just continue
        
        # If this is an assistant message with tool calls
        elif role == "assistant" and message.get("tool_calls"):
            # Check if it's a doctor search
            tool_calls = message.get("tool_calls", [])
            for tool in tool_calls:
                if tool.get("function", {}).get("name") == "search_doctors":
                    await self.redis.hset(conv_state_key, "mentioned_doctor_search", "true")
                    await self.redis.hset(conv_state_key, "last_doctor_search_time", 
                                  self._serialize(datetime.now()))
                    
                    # Save the search parameters for caching
                    try:
                        args = json.loads(tool.get("function", {}).get("arguments", "{}"))
                        await self.redis.hset(conv_state_key, "last_doctor_search_params", 
                                      self._serialize(args))
                    except Exception as e:
                        logger.debug(f"Error processing search parameters: {e}")
                        pass
        
        # Set expiry on conversation state key
        await self.redis.expire(conv_state_key, self.expiry_seconds)
    
    def _extract_topics(self, text: str) -> set:
        """Extract potential topics from text content"""
        # A simple approach - extract key nouns and phrases
        topics = set()
        
        # List of common health topics to detect
        health_topics = [
            "headache", "migraine", "pain", "fever", "cough", "cold", "flu", 
            "allergy", "diabetes", "heart", "blood pressure", "skin", "rash",
            "stomach", "digestion", "mental health", "anxiety", "depression",
            "pregnancy", "eye", "vision", "ear", "hearing", "vaccination",
            "nutrition", "diet", "exercise", "sleep", "stress", "cancer",
            "smoking", "alcohol", "medication", "prescription", "surgery",
            "injury", "infection", "disease", "condition", "treatment"
        ]
        
        # Check if any health topics are mentioned
        for topic in health_topics:
            if topic in text:
                topics.add(topic)
        
        return topics
    
    async def get_conversation_state(self, conversation_id: str) -> Dict[str, Any]:
        """
        Get the tracked state for a conversation.
        
        Args:
            conversation_id: Unique identifier for the conversation
            
        Returns:
            Dictionary of state information for this conversation
        """
        # Ensure Redis connection
        if not self.redis:
            await self._setup_redis_connection()
            
        conv_state_key = self._get_conv_state_key(conversation_id)
        
        # Check if the conversation state exists
        if not await self.redis.exists(conv_state_key):
            return {}
        
        # Get all fields from the conversation state hash
        state_hash = await self.redis.hgetall(conv_state_key)
        
        # Deserialize complex fields
        state = {}
        for key, value in state_hash.items():
            if key == "mentioned_doctor_search":
                state[key] = value == "true"
            elif key == "last_doctor_search_time":
                state[key] = self._deserialize(value, "datetime") if value else None
            elif key == "mentioned_symptoms":
                state[key] = self._deserialize(value) if value else []
            elif key == "topics_discussed":
                state[key] = self._deserialize(value, "set") if value else set()
            elif key == "doctor_search_results":
                state[key] = self._deserialize(value) if value else {}
            elif key == "last_doctor_search_params":
                state[key] = self._deserialize(value) if value else None
            elif key == "search_count":
                state[key] = int(value) if value else 0
            else:
                state[key] = value
                
        return state
    
    async def get_messages(self, conversation_id: str) -> List[Dict[str, Any]]:
        """
        Get all messages for a conversation thread.
        
        Args:
            conversation_id: Unique identifier for the conversation
            
        Returns:
            List of message dictionaries
        """
        # Ensure Redis connection
        if not self.redis:
            await self._setup_redis_connection()
            
        # Get the message list key
        msgs_key = self._get_conv_msgs_key(conversation_id)
        
        # Check if the conversation exists
        if not await self.redis.exists(msgs_key):
            return []
        
        # Update the last accessed time
        now = datetime.now()
        await self.redis.hset(self._get_conv_meta_key(conversation_id), "updated_at", self._serialize(now))
        await self.redis.zadd(self.CONV_INDEX_KEY, {conversation_id: now.timestamp()})
        
        # Refresh expiry
        await self.redis.expire(self._get_conv_meta_key(conversation_id), self.expiry_seconds)
        await self.redis.expire(msgs_key, self.expiry_seconds)
        await self.redis.expire(self._get_conv_state_key(conversation_id), self.expiry_seconds)
        
        # Get all messages
        message_strings = await self.redis.lrange(msgs_key, 0, -1)
        
        # Deserialize each message
        return [self._deserialize_message(msg_str) for msg_str in message_strings]
    
    async def clear_conversation(self, conversation_id: str) -> bool:
        """
        Clear the conversation history for a thread.
        
        Args:
            conversation_id: Unique identifier for the conversation
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure Redis connection
            if not self.redis:
                await self._setup_redis_connection()
                
            # Check if the conversation exists
            meta_key = self._get_conv_meta_key(conversation_id)
            msgs_key = self._get_conv_msgs_key(conversation_id)
            state_key = self._get_conv_state_key(conversation_id)
            
            if not await self.redis.exists(meta_key):
                return True  # Nothing to clear
            
            # Update timestamp
            now = datetime.now()
            
            # Create a pipeline for atomic operations
            pipeline = self.redis.pipeline()
            
            # Clear messages (delete and recreate the list)
            pipeline.delete(msgs_key)
            
            # Update timestamp in metadata
            pipeline.hset(meta_key, "updated_at", self._serialize(now))
            
            # Update in the sorted index
            pipeline.zadd(self.CONV_INDEX_KEY, {conversation_id: now.timestamp()})
            
            # Reset conversation state
            pipeline.delete(state_key)
            pipeline.hset(state_key, "mentioned_doctor_search", "false")
            pipeline.hset(state_key, "mentioned_symptoms", self._serialize([]))
            pipeline.hset(state_key, "topics_discussed", self._serialize(set()))
            pipeline.hset(state_key, "doctor_search_results", self._serialize({}))
            pipeline.hset(state_key, "search_count", "0")
            
            # Set expiry on all keys
            pipeline.expire(meta_key, self.expiry_seconds)
            pipeline.expire(msgs_key, self.expiry_seconds)
            pipeline.expire(state_key, self.expiry_seconds)
            
            # Execute all commands
            await pipeline.execute()
                    
            logger.debug(f"Cleared conversation {conversation_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to clear conversation {conversation_id}: {str(e)}")
            return False
    
    async def get_user_conversation_id(self, user_id: str) -> Optional[str]:
        """
        Get the conversation ID associated with a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Conversation ID if found, None otherwise
        """
        # Ensure Redis connection
        if not self.redis:
            await self._setup_redis_connection()
            
        return await self.redis.get(self._get_user_conv_key(user_id))
    
    async def generate_conversation_id(self, user_id: Optional[str] = None) -> str:
        """
        Generate a unique conversation ID.
        If user_id is provided and user already has a conversation, return that.
        
        Args:
            user_id: Optional user identifier
            
        Returns:
            Unique ID string
        """
        # Ensure Redis connection
        if not self.redis:
            await self._setup_redis_connection()
            
        # If user_id is provided, check if they already have a conversation
        if user_id:
            existing_id = await self.get_user_conversation_id(user_id)
            if existing_id:
                return existing_id
                
            # Otherwise, generate a new ID and associate it with the user
            new_id = str(uuid.uuid4())
            await self.redis.set(self._get_user_conv_key(user_id), new_id)
            return new_id
        
        # If no user_id, just generate a new conversation ID
        return str(uuid.uuid4())

    def _get_cache_key(self, search_params: Dict) -> str:
        """Generate a cache key from search parameters"""
        location = search_params.get("location", "")
        specialty = search_params.get("specialty", "")
        doctor_name = search_params.get("doctor_name", "")
        return f"{location}:{specialty}:{doctor_name}".lower()
        
    async def get_cached_doctor_results(self, conversation_id: str, 
                                location: str, specialty: str = "", 
                                doctor_name: str = "") -> Optional[str]:
        """
        Get cached doctor search results if available.
        
        Args:
            conversation_id: The conversation ID
            location: Location parameter
            specialty: Specialty parameter
            doctor_name: Doctor name parameter
            
        Returns:
            Cached result if found, None otherwise
        """
        # Ensure Redis connection
        if not self.redis:
            await self._setup_redis_connection()
            
            # Generate the cache key
            cache_key = f"{location}:{specialty}:{doctor_name}".lower()
        
        # Get the doctor search results from the conversation state
        state_key = self._get_conv_state_key(conversation_id)
        
        if not await self.redis.exists(state_key):
            return None
            
        results_str = await self.redis.hget(state_key, "doctor_search_results")
        if not results_str:
            return None
            
        doctor_search_results = self._deserialize(results_str)
            
            # Check if we have cached results
        return doctor_search_results.get(cache_key)

    async def associate_conversation_with_user(self, conversation_id: str, user_id: str) -> bool:
        """
        Associate a conversation with a user and determine if this is a new conversation for this user.
        
        Args:
            conversation_id: The conversation ID to associate
            user_id: The user ID to associate with the conversation
            
        Returns:
            True if this is a new conversation for this user, False if they were already associated
        """
        # Ensure Redis connection
        if not self.redis:
            await self._setup_redis_connection()
            
        # Check if user already has a conversation
        existing_conv_id = await self.get_user_conversation_id(user_id)
        
        # If user doesn't have a conversation or has a different one
        if not existing_conv_id or existing_conv_id != conversation_id:
            # Associate this conversation with the user
            await self.redis.set(self._get_user_conv_key(user_id), conversation_id)
            
            # Initialize the conversation if it doesn't exist
            meta_key = self._get_conv_meta_key(conversation_id)
            if not await self.redis.exists(meta_key):
                now = datetime.now()
                pipeline = self.redis.pipeline()
                
                pipeline.hset(meta_key, "created_at", self._serialize(now))
                pipeline.hset(meta_key, "updated_at", self._serialize(now))
                pipeline.hset(meta_key, "user_id", user_id)
                
                # Add to the index
                pipeline.zadd(self.CONV_INDEX_KEY, {conversation_id: now.timestamp()})
                
                # Set expiry
                pipeline.expire(meta_key, self.expiry_seconds)
                
                await pipeline.execute()
            
            # This is a new conversation for this user
            return True
            
        # User is already associated with this conversation
        return False


# Create a singleton instance
memory_service = MemoryService() 