# Memory Service Implementation

## Overview

The Memory Service is responsible for managing conversation histories in the chatbot application. It provides thread-scoped memory that persists for the duration of a conversation and can be recalled from within that specific conversation thread.

## Key Features

- **Thread-scoped Memory**: Each conversation has its own isolated memory space
- **Thread Safety**: Concurrent access is handled properly with locks
- **Automatic Cleanup**: Expired conversations are automatically removed to prevent memory leaks
- **Simple API**: Easy-to-use methods for adding, retrieving, and clearing conversation history

## Implementation Details

The Memory Service uses a thread-safe dictionary to store conversation history, with the following structure:

```python
{
    "conversation_id": {
        "messages": [
            {"role": "user", "content": "..."},
            {"role": "assistant", "content": "..."},
            # More messages
        ],
        "created_at": datetime,
        "updated_at": datetime
    }
}
```

### Memory Management

The service includes automatic memory management features:

- **Expiry**: Conversations that haven't been accessed for a configurable period (default: 24 hours) are automatically removed
- **Size Limits**: The number of active conversations is capped (default: 1000)
- **Cleanup Thread**: A background thread periodically checks for and removes expired conversations

### API Methods

#### `add_message(conversation_id, message)`

Adds a message to the specified conversation thread. The message should be a dictionary with at least `role` and `content` keys.

#### `get_messages(conversation_id)`

Retrieves all messages for a conversation thread. Returns a list of message dictionaries.

#### `clear_conversation(conversation_id)`

Clears the conversation history for a thread, keeping the thread itself but removing all messages.

#### `generate_conversation_id()`

Generates a new unique conversation ID.

## Integration with AI Service

The AI Service uses the Memory Service to maintain conversation context across multiple user interactions. This allows the chatbot to:

1. Remember information from previous messages
2. Understand contextual references
3. Provide more coherent responses in multi-turn conversations

## Usage Example

```python
# Import the service
from app.services.memory_service import memory_service

# Generate a new conversation ID
conversation_id = memory_service.generate_conversation_id()

# Add messages
memory_service.add_message(
    conversation_id,
    {"role": "user", "content": "Hello, my name is John."}
)

# Get messages
messages = memory_service.get_messages(conversation_id)

# Clear conversation
memory_service.clear_conversation(conversation_id)
```
