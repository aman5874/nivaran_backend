# AI Response Generator API

A FastAPI application that serves as an AI response generator using OpenAI's API with Gemini integration for doctor information.

## Features

- Process user input and generate AI responses using OpenAI's API
- Integration with Google's Gemini API for retrieving doctor information
- Support for both streaming and non-streaming responses
- Customizable system prompts to control AI behavior
- Conversation state management with memory service
- Structured input/output validation using Pydantic
- Error handling with appropriate HTTP status codes
- Rate limiting for API calls
- API key authentication

## Requirements

- Python 3.10+
- OpenAI API key
- Google Gemini API key (optional, for doctor information features)

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv
   ```
3. Activate the virtual environment:
   - Windows:
     ```
     venv\Scripts\activate
     ```
   - Unix/MacOS:
     ```
     source venv/bin/activate
     ```
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Create a `.env` file in the root directory with the following variables:

   ```
   # Required - Your OpenAI API key
   OPENAI_API_KEY=your_openai_api_key_here

   # Optional - Your Google Gemini API key for doctor information
   GEMINI_API_KEY=your_gemini_api_key_here

   # Optional settings with defaults
   OPENAI_MODEL=gpt-4.1-mini
   MAX_TOKENS=750
   TEMPERATURE=0.7
   TOP_P=1.0
   FREQUENCY_PENALTY=0.0
   PRESENCE_PENALTY=0.0
   LOG_LEVEL=INFO
   RATE_LIMIT_PER_MINUTE=60

   # Optional API key for securing your API
   API_KEY=your_api_access_key_here
   ```

   > Note: At minimum, you must set the `OPENAI_API_KEY` variable.

## Running the Application

To run the application in development mode:

```
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

### Running Tests

To test the AI service functionality:

```
python tests/test_ai_service.py
```

### Troubleshooting

If you encounter any issues when starting the application:

1. **Missing environment variables**: Make sure you've created a `.env` file with at least the `OPENAI_API_KEY` variable.

2. **Package installation issues**: Ensure you're using a compatible Python version (3.10+) and have installed all dependencies:

   ```
   pip install -r requirements.txt
   ```

3. **Import errors**: Verify that all packages are properly installed and compatible with each other.

## AI Service Components

### OpenAI Integration

The application uses OpenAI's API to generate structured responses based on user queries. It formats all responses in JSON format to ensure consistent handling by frontend applications.

### Gemini Integration with Function Calling

When a user asks about doctor information, the system uses OpenAI's function calling capability to trigger the Gemini LLM and retrieve relevant details about doctors, their availability, specialties, diagnostic tests, and pricing.

The Gemini integration is implemented as a separate service (GeminiService) to maintain modularity and separation of concerns. OpenAI's model automatically detects when doctor information is needed and calls the appropriate function with extracted parameters (location, specialty, etc.). The Gemini model then processes this specialized query and returns detailed information, which is incorporated into the final response.

### Memory Service

The application includes a memory service that maintains conversation state between interactions, allowing for contextual responses and reference to previous messages.

## API Endpoints

### POST /api/generate

Generate AI responses from user input.

**Request Body:**

```json
{
  "user_id": "user123",
  "text": "Tell me about artificial intelligence",
  "conversation_id": "conv456",
  "previous_response_id": null
}
```

The `conversation_id` field is optional for continuing existing conversations. The `previous_response_id` field can be used to explicitly reference the previous response in a conversation chain.

**Response Format:**

The API returns structured JSON responses in one of the following formats:

1. **Text Response:**

```json
{
  "type": "text",
  "content": {
    "text": "Artificial intelligence (AI) refers to..."
  },
  "response_id": "resp789",
  "conversation_id": "conv456"
}
```

2. **Button Response:**

```json
{
  "type": "button",
  "content": {
    "body": {
      "text": "Would you like to learn more about AI applications?"
    },
    "action": {
      "buttons": [
        {
          "reply": {
            "id": "yes-button",
            "title": "Yes"
          }
        },
        {
          "reply": {
            "id": "no-button",
            "title": "No"
          }
        }
      ]
    }
  },
  "response_id": "resp789",
  "conversation_id": "conv456"
}
```

3. **List Response:**

```json
{
  "type": "list",
  "content": {
    "body": {
      "text": "Choose an AI topic to explore:"
    },
    "action": {
      "button": "AI Topics",
      "sections": [
        {
          "title": "Popular Topics",
          "rows": [
            {
              "id": "machine_learning",
              "title": "Machine Learning",
              "description": "Statistical techniques to learn from data"
            },
            {
              "id": "deep_learning",
              "title": "Deep Learning",
              "description": "Neural networks with multiple layers"
            }
          ]
        }
      ]
    }
  },
  "response_id": "resp789",
  "conversation_id": "conv456"
}
```

4. **Call to Action Response:**

```json
{
  "type": "call_to_action",
  "content": {
    "name": "cta_url",
    "parameters": {
      "display_text": "Learn More",
      "url": "https://example.com/ai-resources"
    }
  },
  "response_id": "resp789",
  "conversation_id": "conv456"
}
```

### DELETE /api/conversations/{conversation_id}

Clear the conversation history for a specific conversation ID.

**Parameters:**

- `conversation_id` (path parameter): The ID of the conversation to clear

**Response:**

```json
{
  "success": true,
  "message": "Conversation conv456 cleared successfully"
}
```

If the conversation is not found:

```json
{
  "success": false,
  "message": "Conversation conv456 not found"
}
```

### GET /api/health

Health check endpoint.

**Response:**

```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

## Documentation

API documentation is available at http://localhost:8000/docs when the server is running.

## API Usage Examples

### Using curl

You can use the following curl command to test the API:

```bash
curl -X POST "http://localhost:8000/api/generate" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_access_key_here" \
  -d '{
    "user_id": "user123",
    "text": "Tell me about artificial intelligence",
    "conversation_id": "conv456",
    "previous_response_id": null
  }'
```

For Windows PowerShell:

```powershell
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/generate" `
  -Headers @{
    "Content-Type" = "application/json"
    "X-API-Key" = "your_api_access_key_here"
  } `
  -Body '{
    "user_id": "user123",
    "text": "Tell me about artificial intelligence",
    "conversation_id": "conv456",
    "previous_response_id": null
  }'
```

## Multi-turn Conversations

The API supports multi-turn conversations through two mechanisms:

1. **Using conversation_id**: When you provide the same `conversation_id` across multiple requests, the API maintains the conversation history automatically. This is the simplest approach for most applications.

2. **Using previous_response_id**: For more explicit control over conversation flow, you can provide the `previous_response_id` parameter with the ID of the previous response. This can be useful for branching conversations or resuming from specific points.

Example of a multi-turn conversation:

1. First request:

```json
{
  "user_id": "user123",
  "text": "Tell me a joke",
  "conversation_id": "conv789"
}
```

2. Follow-up request:

```json
{
  "user_id": "user123",
  "text": "Explain why that's funny",
  "conversation_id": "conv789",
  "previous_response_id": "resp456"
}
```

The conversation history is maintained automatically on the server, with a maximum history length to prevent excessive token usage.
