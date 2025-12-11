⎿  Plan saved to: ~/.claude/plans/deep-soaring-squid.md · /plan to edit
     Stage 31: Auto-detect Current/Upcoming Semester

     Date: 2025-12-11
     Focus: Fix hardcoded semester options to automatically detect current/upcoming semester based on today's 
     date.

     1. Problem Description

     Current semester dropdown in Admin Data Management is hardcoded:
     <option value="f25" selected>Fall 2025 (f25)</option>
     <option value="s25">Spring 2025 (s25)</option>
     <option value="s26">Spring 2026 (s26)</option>
     <option value="f24">Fall 2024 (f24)</option>

     Issues:
     - Default is always "f25" regardless of current date
     - No "Current Semester" option that auto-updates
     - After December 2025, system can't fetch Spring 2026 courses properly
     - Manual code changes needed every semester

     2. CMU Semester Code Format

     | Code | Meaning     | Months       |
     |------|-------------|--------------|
     | f25  | Fall 2025   | Sep-Dec 2025 |
     | s26  | Spring 2026 | Jan-May 2026 |
     | m26  | Summer 2026 | Jun-Aug 2026 |

     Pattern: {f|s|m}{YY} where:
     - f = Fall, s = Spring, m = Summer (miniterm)
     - YY = 2-digit year

     3. Solution: Dynamic Semester Detection

     Part A: Create Semester Utility Functions (Backend)

     New file or add to existing: src/semester_utils.py or add to data_manager.py

     from datetime import datetime

     def get_current_semester() -> str:
         """
         Get current semester code based on today's date.

         CMU Academic Calendar:
         - Fall: September - December
         - Spring: January - May
         - Summer: June - August

         Returns: Semester code like 'f25', 's26'
         """
         today = datetime.now()
         year = today.year % 100  # Get 2-digit year (2025 → 25)
         month = today.month

         if month >= 9:  # September - December → Fall
             return f"f{year}"
         elif month >= 6:  # June - August → Summer
             return f"m{year}"
         else:  # January - May → Spring
             return f"s{year}"

     def get_upcoming_semester() -> str:
         """
         Get the upcoming/next semester to fetch courses for.

         Logic:
         - Jan-May: Current is Spring, upcoming is Summer/Fall
         - Jun-Aug: Current is Summer, upcoming is Fall
         - Sep-Nov: Current is Fall, upcoming is Spring (next year)
         - December: Transition month → Spring (next year)
         """
         today = datetime.now()
         year = today.year % 100
         month = today.month

         if month >= 12:  # December → Spring next year
             return f"s{year + 1}"
         elif month >= 9:  # Sep-Nov → Currently Fall, but can still fetch Fall
             return f"f{year}"
         elif month >= 6:  # Jun-Aug → Fall same year
             return f"f{year}"
         elif month >= 1:  # Jan-May → Currently Spring
             return f"s{year}"

     def get_semester_options() -> list:
         """
         Generate dynamic semester options for dropdown.
         Returns list of (value, label, is_default) tuples.
         """
         today = datetime.now()
         year = today.year % 100

         current = get_upcoming_semester()

         options = [
             (f"s{year}", f"Spring {2000+year} (s{year})", f"s{year}" == current),
             (f"m{year}", f"Summer {2000+year} (m{year})", f"m{year}" == current),
             (f"f{year}", f"Fall {2000+year} (f{year})", f"f{year}" == current),
             (f"s{year+1}", f"Spring {2000+year+1} (s{year+1})", f"s{year+1}" == current),
             (f"f{year-1}", f"Fall {2000+year-1} (f{year-1})", False),  # Previous year option
         ]

         return options

     Part B: Add API Endpoint for Semester Options

     File: web/flask_api.py

     @app.route("/api/admin/semesters", methods=["GET"])
     @limiter.exempt
     @login_required
     def get_semesters():
         """Get available semester options with auto-detected default."""
         from src.semester_utils import get_semester_options, get_upcoming_semester

         options = get_semester_options()
         current = get_upcoming_semester()

         return jsonify({
             "options": [{"value": v, "label": l, "selected": s} for v, l, s in options],
             "current": current
         })

     Part C: Update Frontend to Load Dynamic Options

     File: web/admin_data.html

     Replace hardcoded dropdown:
     <select class="form-select form-select-sm" id="course-semester">
         <!-- Options loaded dynamically -->
     </select>

     Add JavaScript to load options:
     async function loadSemesterOptions() {
         try {
             const res = await fetch(`${BASE_URL}/semesters`);
             const data = await res.json();

             const select = document.getElementById('course-semester');
             select.innerHTML = '';

             data.options.forEach(opt => {
                 const option = document.createElement('option');
                 option.value = opt.value;
                 option.textContent = opt.label;
                 if (opt.selected) option.selected = true;
                 select.appendChild(option);
             });
         } catch (e) {
             console.error('Failed to load semesters:', e);
             // Fallback to current semester
             const select = document.getElementById('course-semester');
             select.innerHTML = '<option value="s26" selected>Spring 2026 (s26)</option>';
         }
     }

     // Call on page load
     document.addEventListener('DOMContentLoaded', loadSemesterOptions);

     Part D: Update Backend Default

     File: src/data_manager.py

     def _update_courses(self, params: Dict[str, Any]):
         from src.semester_utils import get_upcoming_semester

         limit = params.get("limit", 100)
         department = params.get("department")
         semester = params.get("semester") or get_upcoming_semester()  # Auto-detect if not provided

     File: data_collection/src/data_collection/course_fetcher_improved.py

     def fetch_courses(self, max_courses: int = 100, ..., semester: str = None) -> List[Course]:
         if semester is None:
             from src.semester_utils import get_upcoming_semester
             semester = get_upcoming_semester()

     4. Files to Modify

     | File                                                           | Changes                               
     |
     |----------------------------------------------------------------|---------------------------------------
     |
     | src/semester_utils.py                                          | NEW: Semester calculation utilities   
     |
     | web/flask_api.py                                               | Add /api/admin/semesters endpoint     
     |
     | web/admin_data.html                                            | Dynamic semester dropdown loading     
     |
     | src/data_manager.py                                            | Use auto-detected semester as default 
     |
     | data_collection/src/data_collection/course_fetcher_improved.py | Use auto-detected semester as default 
     |

     5. Semester Logic Summary

     | Today's Date | get_upcoming_semester() | Reason                       |
     |--------------|-------------------------|------------------------------|
     | Dec 11, 2025 | s26                     | December → Spring next year  |
     | Jan-May 2026 | s26                     | Currently in Spring semester |
     | Jun-Aug 2026 | f26                     | Summer → upcoming is Fall    |
     | Sep-Nov 2026 | f26                     | Currently in Fall semester   |

     6. Verification

     After fix:
     1. Visit Admin → Data Management
     2. Semester dropdown should show dynamic options
     3. Default should be auto-selected based on date (Dec 2025 → s26)
     4. Run course update - should fetch Spring 2026 courses by default