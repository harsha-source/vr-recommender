Stage 38: Friendly Rate Limit Error Messages

 Date: 2025-12-12
 Focus: Display user-friendly rate limit error messages in chatbot instead of generic "Sorry, I encountered
 an error".

 1. Problem Description

 When users exceed rate limits, they see:
 "Sorry, I encountered an error. Please make sure the backend server is running and try again."

 This is unhelpful. Users should see:
 "You've exceeded the limit of 10 requests per minute. Please wait a moment and try again."

 2. Current Behavior

 Backend (flask_api.py)

 - Flask-Limiter returns HTTP 429 with default HTML body
 - No custom JSON response for rate limit errors

 Frontend (vr-chatbot-embed.html:310-325)

 if (!response.ok) {
     throw new Error(`HTTP ${response.status}`);
 }
 // ...
 } catch (error) {
     addMessage('Sorry, I encountered an error...', 'bot');
 }

 3. Solution

 A. Backend: Add Custom Rate Limit Error Handler

 Add to web/flask_api.py after limiter initialization:

 from flask_limiter.errors import RateLimitExceeded

 @app.errorhandler(RateLimitExceeded)
 def handle_rate_limit(e):
     """Return friendly JSON response for rate limit errors."""
     # e.description contains the limit that was exceeded (e.g., "10 per 1 minute")
     limit_info = str(e.description) if e.description else "rate limit"

     return jsonify({
         "error": "rate_limit_exceeded",
         "message": f"You've exceeded the limit of {limit_info}. Please wait and try again.",
         "limit": limit_info,
         "type": "rate_limit"
     }), 429

 B. Frontend: Handle 429 Responses Gracefully

 Modify web/vr-chatbot-embed.html error handling:

 try {
     const response = await fetch(CHATBOT_API_URL, { ... });

     // Handle rate limit specifically
     if (response.status === 429) {
         const errorData = await response.json();
         typingIndicator.remove();
         addMessage(`⚠️ ${errorData.message || "Too many requests. Please wait a moment and try again."}`,
 'bot');
         return;
     }

     if (!response.ok) {
         throw new Error(`HTTP ${response.status}`);
     }
     // ... rest of success handling
 } catch (error) {
     // This now only catches network errors, not 429
     typingIndicator.remove();
     addMessage('Sorry, I encountered a connection error. Please check your network and try again.', 'bot');
 }

 4. Files to Modify

 | File                      | Changes                                          |
 |---------------------------|--------------------------------------------------|
 | web/flask_api.py          | Add @app.errorhandler(RateLimitExceeded) handler |
 | web/vr-chatbot-embed.html | Handle 429 status code with friendly message     |

 5. User Experience

 Before

 User: [sends 11th message in 1 minute]
 Bot: "Sorry, I encountered an error. Please make sure the backend server is running and try again."

 After

 User: [sends 11th message in 1 minute]
 Bot: "⚠️ You've exceeded the limit of 10 per 1 minute. Please wait and try again."

 6. Verification

 1. Send 11 messages within 1 minute
 2. Verify chatbot shows: "You've exceeded the limit of 10 per 1 minute..."
 3. Wait 1 minute, send another message
 4. Verify normal response works again