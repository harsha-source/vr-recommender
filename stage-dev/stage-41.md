 Stage 41: Real-time Analytics Modal for Admin Dashboard

 Date: 2025-12-12
 Type: Feature Addition
 Focus: Add button + modal showing Most Frequent Recommendations & Requests

 ---
 1. Feature Requirements

 User Story

 As an admin, I want to click a button and see a popup showing:
 1. Most Frequent Recommendations - Top 3-5 VR apps that are most recommended
 2. Most Frequent Requests - Common topics/keywords users ask about (e.g., "machine learning", "communication")

 Technical Constraints

 - ❌ No additional storage - No new database collections/tables
 - ✅ Real-time processing - Analysis happens on-demand when button clicked
 - ✅ Interruptible - User can cancel the analysis
 - ✅ Progress indicator - Shows "Analyzing X/Y logs..."

 ---
 2. Current Implementation Analysis

 Existing Infrastructure

 | Component              | Status      | Location                            |
 |------------------------|-------------|-------------------------------------|
 | Admin Dashboard        | ✅ Exists    | web/admin_dashboard.html            |
 | Modal Pattern          | ✅ Exists    | Bootstrap 5 modal for log details   |
 | Interaction Logs       | ✅ Exists    | MongoDB interaction_logs collection |
 | query_text field       | ✅ Available | User's message stored in each log   |
 | recommended_apps field | ✅ Available | Array of recommended apps per log   |

 Log Structure (MongoDB)

 {
   "user_id": "uuid",
   "query_text": "I want to learn machine learning",
   "intent": "recommendation",
   "recommended_apps": [
     {"app_id": "app1", "name": "VR ML Lab", "relevance": 0.95}
   ],
   "timestamp": "2025-12-12T10:00:00Z"
 }

 ---
 3. NLP Approach Options

 For "Most Frequent Requests" (Keyword Extraction)

 | Option                    | Pros                                    | Cons                      | Complexity |
 |---------------------------|-----------------------------------------|---------------------------|------------|
 | A. Word Frequency         | Simple, fast                            | Single words only, noisy  | Low        |
 | B. N-gram + Stop Words    | Catches phrases like "machine learning" | Needs tuning              | Medium     |
 | C. TF-IDF                 | Weights important terms                 | More compute              | Medium     |
 | D. YAKE Keyword Extractor | Unsupervised, good phrases              | New dependency            | Medium     |
 | E. spaCy NER              | Extracts named entities                 | Heavy dependency (~500MB) | High       |

 Recommended: Option B (N-gram with Stop Words)

 - Extracts bigrams and trigrams (2-3 word phrases)
 - Removes common stop words ("I want to", "can you")
 - No new dependencies (uses Python collections.Counter)
 - Fast enough for real-time processing

 ---
 4. Implementation Plan

 4.1 Backend: New API Endpoint

 File: web/flask_api.py

 @app.route('/api/admin/analytics/frequent', methods=['POST'])
 @login_required
 def get_frequent_analytics():
     """Real-time analysis of frequent requests and recommendations"""
     # 1. Fetch all logs from MongoDB
     logs = interaction_logger.repo.find_all_raw()

     # 2. Extract frequent apps from recommended_apps
     app_counter = Counter()
     for log in logs:
         for app in log.get('recommended_apps', []):
             app_counter[app['name']] += 1
     top_apps = app_counter.most_common(5)

     # 3. Extract frequent keywords from query_text
     all_queries = [log['query_text'] for log in logs if log.get('query_text')]
     top_keywords = extract_keywords(all_queries, top_n=10)

     return jsonify({
         "top_recommendations": [{"name": k, "count": v} for k, v in top_apps],
         "top_requests": top_keywords,
         "logs_analyzed": len(logs)
     })

 4.2 NLP Function: Keyword Extraction

 File: src/text_analysis.py (new file)

 from collections import Counter
 import re

 STOP_WORDS = {'i', 'want', 'to', 'the', 'a', 'an', 'is', 'are', 'can', 'you',
               'help', 'me', 'with', 'for', 'in', 'of', 'and', 'or', 'my', 'some',
               'learn', 'looking', 'need', 'please', 'would', 'like', 'about'}

 def extract_keywords(queries: list[str], top_n: int = 10) -> list[dict]:
     """Extract frequent keywords/phrases from user queries"""
     ngram_counter = Counter()

     for query in queries:
         # Normalize: lowercase, remove punctuation
         text = re.sub(r'[^\w\s]', '', query.lower())
         words = [w for w in text.split() if w not in STOP_WORDS and len(w) > 2]

         # Count unigrams
         ngram_counter.update(words)

         # Count bigrams (2-word phrases)
         for i in range(len(words) - 1):
             bigram = f"{words[i]} {words[i+1]}"
             ngram_counter[bigram] += 1

     return [{"keyword": k, "count": v} for k, v in ngram_counter.most_common(top_n)]

 4.3 Frontend: Button + Modal

 File: web/admin_dashboard.html

 Add button to existing stats section:
 <button class="btn btn-primary" onclick="showFrequentAnalytics()">
     <i class="bi bi-bar-chart"></i> View Frequent Analytics
 </button>

 Add modal:
 <div class="modal fade" id="analyticsModal" tabindex="-1">
     <div class="modal-dialog modal-lg">
         <div class="modal-content">
             <div class="modal-header">
                 <h5 class="modal-title">Frequent Analytics</h5>
                 <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
             </div>
             <div class="modal-body">
                 <!-- Progress indicator -->
                 <div id="analytics-progress" class="text-center">
                     <div class="spinner-border text-primary"></div>
                     <p>Analyzing logs... <span id="progress-count">0</span></p>
                 </div>

                 <!-- Results (hidden until complete) -->
                 <div id="analytics-results" style="display:none">
                     <div class="row">
                         <div class="col-md-6">
                             <h6>Top Recommended Apps</h6>
                             <div id="top-apps-list"></div>
                         </div>
                         <div class="col-md-6">
                             <h6>Most Frequent Requests</h6>
                             <div id="top-keywords-list"></div>
                         </div>
                     </div>
                 </div>
             </div>
         </div>
     </div>
 </div>

 JavaScript handler:
 async function showFrequentAnalytics() {
     const modal = new bootstrap.Modal(document.getElementById('analyticsModal'));
     modal.show();

     // Show progress, hide results
     document.getElementById('analytics-progress').style.display = 'block';
     document.getElementById('analytics-results').style.display = 'none';

     try {
         const response = await fetch('/api/admin/analytics/frequent', {method: 'POST'});
         const data = await response.json();

         // Render top apps
         const appsHtml = data.top_recommendations.map(app =>
             `<div class="d-flex justify-content-between">
                 <span>${app.name}</span>
                 <span class="badge bg-primary">${app.count}</span>
             </div>`
         ).join('');
         document.getElementById('top-apps-list').innerHTML = appsHtml;

         // Render top keywords
         const keywordsHtml = data.top_requests.map(kw =>
             `<span class="badge bg-secondary me-1 mb-1">${kw.keyword} (${kw.count})</span>`
         ).join('');
         document.getElementById('top-keywords-list').innerHTML = keywordsHtml;

         // Show results, hide progress
         document.getElementById('analytics-progress').style.display = 'none';
         document.getElementById('analytics-results').style.display = 'block';
     } catch (error) {
         console.error('Analytics error:', error);
     }
 }

 ---
 5. Files to Modify/Create

 | File                     | Action | Description                                |
 |--------------------------|--------|--------------------------------------------|
 | web/flask_api.py         | Modify | Add /api/admin/analytics/frequent endpoint |
 | src/text_analysis.py     | Create | Keyword extraction function                |
 | web/admin_dashboard.html | Modify | Add button + modal                         |

 ---
 6. Confirmed Decisions

 | Decision     | Choice                                                    |
 |--------------|-----------------------------------------------------------|
 | NLP Approach | N-gram + Stop Words (simple, no new dependencies)         |
 | Top N Count  | Top 5 items per section                                   |
 | Time Range   | Date picker (preset: Last 7 days, Last 30 days, All time) |

 ---
 7. Updated Implementation

 Date Range Filter (Frontend)

 Add to modal header:
 <select id="analytics-range" class="form-select form-select-sm w-auto">
     <option value="7">Last 7 days</option>
     <option value="30" selected>Last 30 days</option>
     <option value="0">All time</option>
 </select>

 Date Range Filter (Backend)

 @app.route('/api/admin/analytics/frequent', methods=['POST'])
 @login_required
 def get_frequent_analytics():
     days = request.json.get('days', 30)  # Default 30 days

     # Build date filter
     if days > 0:
         cutoff = datetime.utcnow() - timedelta(days=days)
         query = {"timestamp": {"$gte": cutoff}}
     else:
         query = {}

     logs = list(interaction_logger.repo.collection.find(query))
     # ... rest of analysis

 ---
 8. Final File Changes

 | File                     | Action | Changes                                                        |
 |--------------------------|--------|----------------------------------------------------------------|
 | web/flask_api.py         | Modify | Add /api/admin/analytics/frequent endpoint with date filtering |
 | src/text_analysis.py     | Create | N-gram keyword extraction function                             |
 | web/admin_dashboard.html | Modify | Add button, modal with date picker, results display            |