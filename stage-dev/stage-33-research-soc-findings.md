# Stage 33: CMU SOC System Research Findings

**Date:** 2025-12-10
**Status:** Complete
**Target URL:** `https://enr-apps.as.cmu.edu/open/SOC/SOCServlet/search`

---

## 1. System Overview

The **Schedule of Classes (SOC)** is a legacy Java Servlet application that serves as the central source of truth for CMU courses. Unlike the individual department pages (which are fragmented and inconsistent), the SOC provides a unified interface for all departments with a consistent data structure.

### Key Discovery
We found a hidden "API" endpoint used by the frontend modal system that returns clean HTML fragments for course details (Description, Prerequisites, etc.), bypassing the need for complex browser automation or popup handling.

---

## 2. Technical Architecture

### 2.1 Course List Retrieval (Search)

**Method:** `POST`
**URL:** `https://enr-apps.as.cmu.edu/open/SOC/SOCServlet/search`
**Content-Type:** `application/x-www-form-urlencoded`

**Required Payload:**
```
SEMESTER=S26          # S=Spring, F=Fall, M=Summer + YY (e.g., S26)
DEPT=CS               # Department Code (see Mapping below)
GRAD_UNDER=All        # 'All', 'U' (Undergrad), 'G' (Graduate)
PRG_LOCATION=All      # 'All', 'PIT' (Pittsburgh), 'DOH' (Doha), 'SJC' (Silicon Valley), etc.
BEG_TIME=All          # 'All'
KEYWORD=              # Optional search keyword
TITLE_ONLY=YES        # 'YES' (checkbox for title only search, likely irrelevant for full scrape)
SUBMIT=Retrieve Schedule
```

**Response:**
- Returns a full HTML page.
- Contains a generic table with `class="table table-striped table-hover"` (or similar structure, easy to identify).
- **Course IDs** are in the first column as links.
- **Titles**, **Units**, **Sections**, **Days**, **Times**, **Locations** are in subsequent columns.

### 2.2 Course Detail Retrieval (The "Hidden" API)

**Method:** `GET`
**URL:** `https://enr-apps.as.cmu.edu/open/SOC/SOCServlet/courseDetails`

**Query Parameters:**
- `COURSE`: The 5-digit course number (e.g., `15112`).
- `SEMESTER`: The semester code (matching the search, e.g., `S26`).

**Example:**
`https://enr-apps.as.cmu.edu/open/SOC/SOCServlet/courseDetails?COURSE=15112&SEMESTER=S26`

**Response:**
- Returns a raw HTML fragment (not a full page).
- **Description:** Found in a `<p>` tag immediately following a `<h4>Description:</h4>` header.
- **Prerequisites:** Found in a `<dd>` tag following a `<dt>Prerequisites</dt>` (or similar definition list structure).
- **Corequisites:** Similar to Prerequisites.
- **Reservations:** A table at the bottom listing restriction logic (e.g., "M - Some reservations are for Students in SCS").

---

## 3. Data Dictionary & Mapping

| SOC Field | HTML Element | Target Model Field | Extraction Strategy |
|-----------|--------------|--------------------|---------------------|
| **Course ID** | Table Col 1 (`<a>`) | `id` (e.g., "15-112") | Extract text, format to XX-XXX |
| **Title** | Table Col 2 | `title` | Text content |
| **Units** | Table Col 3 | `units` | Text content (float/int) |
| **Description** | Detail Page `<h4>Description:</h4> + <p>` | `description` | Text content of the sibling `<p>` |
| **Prereqs** | Detail Page `Prerequisites` term | `prerequisites` | Text content of `<dd>` sibling |
| **Coreqs** | Detail Page `Corequisites` term | `corequisites` | Text content of `<dd>` sibling |
| **Department** | Form Input `DEPT` | `department` | Derived from the search parameter (e.g., "CS" -> "Computer Science") |

---

## 4. Implementation Strategy (Stage 34)

We can replace the complex multi-site scraping with a standardized 2-phase process:

### Phase 1: Fetch Course List
1.  Iterate through target departments (e.g., `CS`, `ECE`, `ROB`... or scrape the `DEPT` list from the main page first to get all codes).
2.  Send `POST` request to `/search` for the target semester (e.g., `S26` or current).
3.  Parse the returned HTML table to build a list of `Course` objects (ID, Title, Units).

### Phase 2: Enrich with Details
1.  For each unique course found in Phase 1:
2.  Construct the GET URL: `/courseDetails?COURSE={id}&SEMESTER={sem}`.
3.  Fetch the HTML fragment.
4.  Parse `Description` and `Prerequisites`.
5.  Update the `Course` object.
6.  (Optional) Rate limit these requests to avoid IP bans (e.g., 5-10 requests/second).

### Recommendation
Use standard `requests` and `BeautifulSoup` (Python) or `fetch` (Node). **FireCrawl is not strictly necessary** and might be overkill since the site structure is simple and static (server-side rendered). Standard HTTP libraries will be faster and more controllable for the thousands of detail requests.

---

## 5. Department Code Mapping (Sample)

- **Computer Science:** `CS` (15XXX)
- **Robotics:** `ROB` (16XXX)
- **Machine Learning:** `MLG` (10XXX)
- **HCI:** `HCI` (05XXX)
- **ECE:** `ECE` (18XXX)
- **Mechanical Eng:** `MEG` (24XXX)
- **Mathematical Sci:** `MSC` (21XXX)
- **Statistics:** `STA` (36XXX)
- **Information Systems:** `ISM` (95XXX), `ISP` (67XXX)

*Full list can be extracted from the `<select name="DEPT">` element on the search page.*
