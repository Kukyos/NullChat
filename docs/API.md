# API Documentation for Admin Panel Integration

## Base URL
```
Development: http://localhost:8000
Production: https://your-api-domain.com
```

## Authentication

### POST /admin/login
```json
Request:
{
  "username": "admin",
  "password": "password123"
}

Response:
{
  "success": true,
  "data": {
    "token": "jwt-token-here",
    "expires_in": 86400,
    "user": {
      "id": 1,
      "username": "admin",
      "role": "admin"
    }
  }
}
```

### GET /admin/conversations
```json
Query Parameters:
- page: int = 1
- limit: int = 50
- language: str = null
- date_from: str = null (YYYY-MM-DD)
- date_to: str = null
- feedback: int = null (-1, 0, 1)

Response:
{
  "success": true,
  "data": [
    {
      "id": 1,
      "session_id": "uuid-here",
      "user_message": "When is the fee deadline?",
      "bot_response": "Fee deadline is March 15th, 2024.",
      "language_detected": "en",
      "confidence_score": 0.95,
      "feedback": 1,
      "timestamp": "2024-01-15T10:30:00Z",
      "forwarded_to_admin": false
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 50,
    "total": 150,
    "pages": 3
  }
}
```

### POST /admin/documents
```json
Content-Type: multipart/form-data

Form Fields:
- file: PDF file
- title: string (optional)

Response:
{
  "success": true,
  "data": {
    "id": 1,
    "filename": "fee_structure_2024.pdf",
    "title": "Fee Structure 2024",
    "file_size": 1024000,
    "upload_date": "2024-01-15T10:30:00Z",
    "processing_status": "pending"
  }
}
```

### GET /admin/overrides
```json
Response:
{
  "success": true,
  "data": [
    {
      "id": 1,
      "question_pattern": "fee.*deadline|last.*date.*fee",
      "override_response": "Fee deadline is March 15th, 2024. Please pay online or at the accounts office.",
      "language_code": "en",
      "audio_file_path": "/audio/fee_deadline_en.mp3",
      "created_date": "2024-01-10T09:00:00Z",
      "is_active": true
    }
  ]
}
```

### POST /admin/overrides
```json
Request:
{
  "question_pattern": "admission.*process|how.*to.*apply",
  "override_response": "Visit our admissions page or contact the office at +91-1234567890",
  "language_code": "en"
}

Response:
{
  "success": true,
  "data": {
    "id": 2,
    "question_pattern": "admission.*process|how.*to.*apply",
    "override_response": "Visit our admissions page or contact the office at +91-1234567890",
    "language_code": "en",
    "created_date": "2024-01-15T11:00:00Z",
    "is_active": true
  }
}
```

### GET /admin/analytics/daily
```json
Query Parameters:
- days: int = 7 (last N days)

Response:
{
  "success": true,
  "data": {
    "daily_stats": [
      {
        "date": "2024-01-15",
        "total_conversations": 45,
        "positive_feedback": 38,
        "negative_feedback": 3,
        "forwarded_to_admin": 2,
        "languages": {
          "en": 25,
          "hi": 15,
          "ta": 5
        }
      }
    ],
    "summary": {
      "total_conversations": 315,
      "avg_daily": 45,
      "satisfaction_rate": 0.89
    }
  }
}
```

### WebSocket: /admin/ws
```json
Real-time messages:
{
  "type": "new_conversation",
  "data": {
    "id": 123,
    "user_message": "What is the hostel fee?",
    "language": "en",
    "timestamp": "2024-01-15T14:30:00Z"
  }
}

{
  "type": "feedback_received",
  "data": {
    "conversation_id": 123,
    "feedback": 1,
    "timestamp": "2024-01-15T14:32:00Z"
  }
}

{
  "type": "forwarded_to_admin",
  "data": {
    "conversation_id": 124,
    "user_message": "My scholarship status is unclear",
    "language": "hi",
    "timestamp": "2024-01-15T14:35:00Z"
  }
}
```

## Error Responses
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid file format. Only PDF files are allowed.",
    "details": {
      "field": "file",
      "provided": "image/jpeg",
      "expected": "application/pdf"
    }
  }
}
```

## File Upload Constraints
- PDF files: Max 10MB
- Audio files: Max 5MB, formats: MP3, WAV, M4A
- Rate limiting: 100 requests per minute per IP

## Status Codes
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 413: File too large
- 429: Rate limit exceeded
- 500: Internal Server Error