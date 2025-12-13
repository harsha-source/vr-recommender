Stage 39: Adopt Harsha's Full-Page Chat Interface Design

 Date: 2025-12-12
 Focus: Replace embedded widget chatbot with Harsha's full-page chat interface design.

 1. Overview

 Replace the current floating widget chatbot (vr-chatbot-embed.html) with Harsha's full-page chat interface
 (chat_interface.html) for the main user experience.

 2. Design Comparison

 | Aspect  | Current (Widget)      | Harsha's (Full-Page)                    |
 |---------|-----------------------|-----------------------------------------|
 | Type    | Floating popup widget | Full-page centered interface            |
 | Width   | 420px popup           | 800px max-width                         |
 | Font    | System fonts          | Inter (Google Fonts)                    |
 | Welcome | Bot message bubble    | Welcome screen + 4 suggestion cards     |
 | Layout  | Fixed bottom-right    | Centered, full viewport                 |
 | Input   | Textarea in popup     | Rounded input with absolute send button |

 3. Key Features of Harsha's Design

 - Welcome Screen: Shows 4 clickable suggestion cards (Machine Learning, Data Visualization, Soft Skills,
 Cybersecurity)
 - Modern Typography: Uses Inter font from Google Fonts
 - Clean Layout: 800px max-width, centered, full-height
 - Smooth Animations: Fade-in messages, bouncing typing indicator
 - Header: Simple brand bar with chat icon
 - Footer: Disclaimer text below input

 4. Required Integrations

 Harsha's design needs these modifications to work with current backend:

 A. Add Conversation History Support

 // Current Harsha: sends only { message }
 // Need to add: { message, history: conversationHistory }
 let conversationHistory = [];

 B. Handle Rate Limit Errors (Stage 38)

 if (response.status === 429) {
     const errorData = await response.json();
     typingIndicator.remove();
     appendMessage('bot', `⚠️ ${errorData.message}`);
     return;
 }

 C. Keep Session/User Tracking

 The current system uses cookies for user tracking - ensure compatibility.

 5. Files to Modify

 | File                      | Action                                                    |
 |---------------------------|-----------------------------------------------------------|
 | web/chat_interface.html   | CREATE - New file with Harsha's design + our integrations |
 | web/flask_api.py          | MODIFY - Change home() route to serve chat_interface.html |
 | web/vr-chatbot-embed.html | KEEP - Retain as embeddable widget option                 |

 6. Implementation Steps

 Step 1: Create chat_interface.html

 Create new file with Harsha's design, adding:
 1. Conversation history tracking (conversationHistory array)
 2. Modified sendMessage() to pass { message, history }
 3. Rate limit error handling (429 status)
 4. Keep appendMessage() to update history array

 Step 2: Update flask_api.py

 Change line 161:
 # Before:
 return send_file("vr-chatbot-embed.html", mimetype="text/html")

 # After:
 return send_file("chat_interface.html", mimetype="text/html")

 Step 3: Test Integration

 1. Access http://localhost:5001/
 2. Verify welcome screen with suggestion cards appears
 3. Click suggestion cards - verify they populate input
 4. Send messages - verify conversation works
 5. Send 11+ messages - verify rate limit shows friendly error
 6. Verify conversation context is maintained (multi-turn)

 7. Rollback Plan

 If issues arise, simply change flask_api.py back to serve vr-chatbot-embed.html.

 8. Documentation

 Create stage-dev/stage-39-harsha-ui.md documenting:
 - What changed
 - Design comparison
 - How to switch between designs

 Status: PLANNED