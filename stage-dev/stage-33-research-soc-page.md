# Stage 33: Research CMU Schedule of Classes (SOC) Page Structure

**Date:** 2025-12-11
**Type:** Research / Investigation
**Focus:** Deep-dive analysis of CMU SOC system to understand data extraction approach

---

## 1. Background

### Current Problem
- Course fetcher shows "0 with full details" for all non-CS courses
- Current approach uses multiple department catalog pages (fragmented)
- Only CS (15-XXX) has working detail page URLs

### New Data Source Discovered
User provided the **correct** unified data source:
```
https://enr-apps.as.cmu.edu/open/SOC/SOCServlet/search
```

This is CMU's **Schedule of Classes (SOC)** system:
- Contains ALL courses across ALL departments
- Single unified interface
- Course details available via popup when clicking course number
- No need to scrape individual department pages

---

## 2. Research Objectives

### 2.1 Page Structure Analysis
- [ ] Understand the search form parameters
- [ ] Identify semester selection mechanism
- [ ] Map department/college filter options
- [ ] Document search result format

### 2.2 Course Detail Popup Analysis
- [ ] How are course details loaded? (AJAX? iframe? JavaScript?)
- [ ] What URL/endpoint provides course details?
- [ ] What data fields are available in the popup?
  - Course number
  - Title
  - Description
  - Units
  - Prerequisites
  - Corequisites
  - Instructor
  - Schedule/Time
  - Location

### 2.3 API/Endpoint Discovery
- [ ] Is there a REST API behind the search?
- [ ] Can we get JSON/XML responses?
- [ ] What are the request parameters for:
  - Search by keyword
  - Search by course number
  - Search by department
  - Filter by semester

### 2.4 Technical Constraints
- [ ] Authentication requirements?
- [ ] Rate limiting?
- [ ] Session/cookie requirements?
- [ ] CORS restrictions?

---

## 3. Research Methodology

### Step 1: Manual Browser Inspection
1. Open SOC page in Chrome DevTools
2. Perform searches and observe:
   - Network requests (XHR/Fetch)
   - Request/response payloads
   - URL patterns
3. Click course numbers and observe:
   - How popup is triggered
   - What data is loaded
   - Source of course details

### Step 2: Document Findings
For each discovery, document:
- URL pattern
- Request method (GET/POST)
- Required parameters
- Response format (HTML/JSON/XML)
- Example data

### Step 3: Test API Endpoints
If API endpoints are found:
- Test with curl/httpie
- Document authentication needs
- Test rate limits
- Verify data completeness

---

## 4. Expected Deliverables

### 4.1 SOC System Documentation
```markdown
## SOC System Architecture
- Base URL: https://enr-apps.as.cmu.edu/open/SOC/SOCServlet/...
- Search endpoint: ???
- Detail endpoint: ???
- Semester format: ???
```

### 4.2 Data Field Mapping
| SOC Field | Our Course Model Field | Available? |
|-----------|----------------------|------------|
| Course Number | course_id | ? |
| Title | title | ? |
| Description | description | ? |
| Units | units | ? |
| Prerequisites | prerequisites | ? |
| Department | department | ? |

### 4.3 Recommended Approach
Based on research findings, recommend:
- Best method to fetch course list
- Best method to fetch course details
- API vs scraping decision
- Rate limiting strategy

---

## 5. Success Criteria

Stage 33 is complete when:
1. SOC page structure is fully documented
2. Course detail retrieval method is identified
3. All available data fields are mapped
4. Technical constraints are understood
5. Recommended approach for Stage 34 is clear

---

## 6. Next Stages Preview

- **Stage 34:** Implement new SOC-based course fetcher
- **Stage 35:** Integrate and test with existing system
