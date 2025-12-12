"""
SOC Course Fetcher - Stage 34
Based on CMU Schedule of Classes (SOC) system
Uses simple HTTP requests instead of Firecrawl
"""

import re
import time
import json
import os
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass, asdict


@dataclass
class Course:
    """CMU Course data model"""
    course_id: str           # "15-112"
    title: str               # "Fundamentals of Programming"
    department: str          # "Computer Science"
    description: str
    units: int
    prerequisites: List[str]
    learning_outcomes: List[str]
    semester: str = ""       # "S26", "F25"

    def to_dict(self):
        return asdict(self)


# Hardcoded department codes from SOC system
# Format: "CODE": ("Department Name", "course_prefix")
DEPARTMENT_CODES = {
    # School of Computer Science
    "CS": ("Computer Science", "15"),
    "ROB": ("Robotics", "16"),
    "MLG": ("Machine Learning", "10"),
    "HCI": ("Human-Computer Interaction", "05"),
    "LTI": ("Language Technologies Institute", "11"),
    "S3D": ("Software & Societal Systems", "17"),
    "SCS": ("SCS Interdisciplinary", "15"),
    "CB": ("Computational Biology", "02"),

    # College of Engineering
    "ECE": ("Electrical & Computer Engineering", "18"),
    "MEG": ("Mechanical Engineering", "24"),
    "CEE": ("Civil & Environmental Engineering", "12"),
    "MSE": ("Materials Science & Engineering", "27"),
    "BMD": ("Biomedical Engineering", "42"),
    "CHE": ("Chemical Engineering", "06"),
    "EPP": ("Engineering & Public Policy", "19"),
    "CIT": ("CIT Interdisciplinary", "39"),

    # Heinz College
    "HC": ("Heinz College Wide Courses", "94"),
    "ISM": ("Information Systems Management", "95"),
    "ISP": ("Information Systems Program", "67"),
    "PPP": ("Public Policy & Mgt", "90"),
    "PMP": ("Public Management", "90"),
    "MED": ("Medical Management", "92"),
    "AEM": ("Arts & Entertainment Management", "93"),

    # Tepper School of Business
    "BUS": ("Business Administration", "70"),
    "ECO": ("Economics", "73"),

    # Mellon College of Science
    "STA": ("Statistics and Data Science", "36"),
    "MSC": ("Mathematical Sciences", "21"),
    "PHY": ("Physics", "33"),
    "BSC": ("Biological Sciences", "03"),
    "CMY": ("Chemistry", "09"),
    "MCS": ("MCS Interdisciplinary", "38"),

    # Dietrich College
    "ENG": ("English", "76"),
    "PSY": ("Psychology", "85"),
    "SDS": ("Social & Decision Sciences", "88"),
    "HIS": ("History", "79"),
    "PHI": ("Philosophy", "80"),
    "LCL": ("Languages Cultures & Appl Linguistics", "82"),
    "HSS": ("Dietrich College Interdisciplinary", "66"),

    # College of Fine Arts
    "ARC": ("Architecture", "48"),
    "ART": ("Art", "60"),
    "DES": ("Design", "51"),
    "DRA": ("Drama", "54"),
    "MUS": ("Music", "57"),
    "CFA": ("CFA Interdisciplinary", "62"),
    "ETC": ("Entertainment Technology", "53"),

    # Other Programs
    "INI": ("Information Networking Institute", "14"),
    "III": ("Integrated Innovation Institute", "49"),
    "CMU": ("CMU University-Wide Studies", "99"),
    "NSI": ("Neuroscience Institute", "86"),
    "ICT": ("Information & Communication Tech", "04"),
}


class SOCCourseFetcher:
    """
    CMU Schedule of Classes (SOC) based course fetcher.
    Uses simple HTTP requests - no Firecrawl dependency.
    """

    BASE_URL = "https://enr-apps.as.cmu.edu/open/SOC/SOCServlet"

    def __init__(self, logger: Optional[Callable] = None, verify_ssl: bool = False):
        """
        Initialize the fetcher.

        Args:
            logger: Optional logging function (e.g., self._log from JobManager)
            verify_ssl: Whether to verify SSL certificates (default: False for CMU's cert issues)
        """
        self.logger = logger or print
        self.verify_ssl = verify_ssl
        self.session = requests.Session()
        # Set headers to mimic browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })

        # Disable SSL warnings if not verifying
        if not self.verify_ssl:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def _log(self, message: str):
        """Log a message using the configured logger."""
        if self.logger:
            self.logger(message)

    def fetch_courses(
        self,
        max_courses: int = 100,
        department: Optional[str] = None,
        semester: str = "S26",
        fetch_details: bool = True,
        **kwargs  # Accept extra params for compatibility
    ) -> List[Course]:
        """
        Main entry point: Fetch courses from SOC.

        Args:
            max_courses: Maximum number of courses to fetch
            department: Department name to filter (e.g., "School of Computer Science")
            semester: Semester code (e.g., "S26", "F25")
            fetch_details: Whether to fetch detailed descriptions

        Returns:
            List of Course objects
        """
        self._log(f"SOC Fetcher initialized (max={max_courses}, dept={department}, semester={semester})")

        # Determine which department codes to fetch
        dept_codes = self._get_department_codes(department)
        self._log(f"Will fetch from {len(dept_codes)} department(s): {list(dept_codes.keys())}")

        all_courses = []

        for dept_code, (dept_name, course_prefix) in dept_codes.items():
            if len(all_courses) >= max_courses:
                break

            self._log(f"Fetching {dept_code} ({dept_name})...")

            # Phase 1: Get course list
            course_list = self._fetch_course_list(dept_code, semester)
            self._log(f"  Found {len(course_list)} courses in {dept_code}")

            # Phase 2: Get details for each course
            for course_info in course_list:
                if len(all_courses) >= max_courses:
                    break

                course_id = course_info.get('course_id', '')
                title = course_info.get('title', '')
                units = course_info.get('units', 0)

                # Format course_id to XX-XXX format
                formatted_id = self._format_course_id(course_id)

                if fetch_details:
                    # Get detailed description
                    detail = self._fetch_course_detail(course_id, semester)
                    description = detail.get('description', '')
                    prerequisites = detail.get('prerequisites', '')
                else:
                    description = ''
                    prerequisites = ''

                # Parse prerequisites into list
                prereq_list = self._parse_prerequisites(prerequisites)

                course = Course(
                    course_id=formatted_id,
                    title=title,
                    department=dept_name,
                    description=description,
                    units=self._parse_units(units),
                    prerequisites=prereq_list,
                    learning_outcomes=[],  # SOC doesn't have this
                    semester=semester
                )

                all_courses.append(course)

                # Rate limiting
                if fetch_details:
                    time.sleep(0.1)  # 100ms between detail requests

            # Brief pause between departments
            time.sleep(0.5)

        self._log(f"Total fetched: {len(all_courses)} courses")

        # Log stats
        with_desc = sum(1 for c in all_courses if c.description)
        self._log(f"  {with_desc} with full details (descriptions)")
        self._log(f"  {len(all_courses) - with_desc} with basic info")

        return all_courses

    def _get_department_codes(self, department: Optional[str]) -> Dict[str, tuple]:
        """
        Get department codes to fetch based on filter.

        Args:
            department: Department name filter (e.g., "School of Computer Science")

        Returns:
            Dict of {code: (name, prefix)} to fetch
        """
        if not department or department == "All Departments":
            return DEPARTMENT_CODES

        # Map department names to codes (using correct SOC codes)
        dept_mapping = {
            "School of Computer Science": ["CS", "ROB", "MLG", "HCI", "LTI", "S3D", "SCS", "CB"],
            "College of Engineering": ["ECE", "MEG", "CEE", "MSE", "BMD", "CHE", "EPP", "CIT"],
            "Heinz College": ["HC", "ISM", "ISP", "PPP", "PMP", "MED", "AEM"],
            "Tepper School of Business": ["BUS", "ECO"],
            "Dietrich College": ["ENG", "PSY", "SDS", "HIS", "PHI", "LCL", "HSS"],
            "College of Fine Arts": ["ARC", "ART", "DES", "DRA", "MUS", "CFA", "ETC"],
            "Mellon College of Science": ["STA", "MSC", "PHY", "BSC", "CMY", "MCS"],
        }

        codes = dept_mapping.get(department, [])
        if not codes:
            # Try to find by partial match
            for name, code_list in dept_mapping.items():
                if department.lower() in name.lower():
                    codes = code_list
                    break

        if not codes:
            self._log(f"Warning: Unknown department '{department}', using CS as default")
            codes = ["CS"]

        return {code: DEPARTMENT_CODES[code] for code in codes if code in DEPARTMENT_CODES}

    def _fetch_course_list(self, dept_code: str, semester: str) -> List[Dict]:
        """
        Phase 1: Fetch course list via POST request.

        Args:
            dept_code: Department code (e.g., "CS", "ECE")
            semester: Semester code (e.g., "S26")

        Returns:
            List of {course_id, title, units}
        """
        url = f"{self.BASE_URL}/search"
        payload = {
            "SEMESTER": semester.upper(),  # CMU SOC requires uppercase (S26 not s26)
            "MINI": "NO",
            "GRAD_UNDER": "All",
            "PRG_LOCATION": "All",
            "DEPT": dept_code,
            "LAST_NAME": "",
            "FIRST_NAME": "",
            "BEG_TIME": "All",
            "KEYWORD": "",
            "TITLE_ONLY": "YES",
            "SUBMIT": ""
        }

        try:
            response = self.session.post(url, data=payload, timeout=30, verify=self.verify_ssl)
            response.raise_for_status()
            return self._parse_course_table(response.text)
        except requests.RequestException as e:
            self._log(f"  Error fetching {dept_code}: {e}")
            return []

    def _parse_course_table(self, html: str) -> List[Dict]:
        """
        Parse course list HTML table.

        Args:
            html: HTML content from search response

        Returns:
            List of {course_id, title, units}
        """
        soup = BeautifulSoup(html, 'html.parser')
        courses = []

        # Find the main results table
        # The SOC page uses Bootstrap tables
        tables = soup.find_all('table', class_='table')

        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 3:
                    # First column: course number (may be a link)
                    course_cell = cols[0]
                    link = course_cell.find('a')
                    if link:
                        course_id = link.get_text(strip=True)
                    else:
                        course_id = course_cell.get_text(strip=True)

                    # Skip non-course rows
                    if not course_id or not re.match(r'^\d{5}$', course_id):
                        continue

                    # Second column: title
                    title = cols[1].get_text(strip=True)

                    # Third column: units
                    units = cols[2].get_text(strip=True)

                    courses.append({
                        'course_id': course_id,
                        'title': title,
                        'units': units
                    })

        return courses

    def _fetch_course_detail(self, course_id: str, semester: str) -> Dict:
        """
        Phase 2: Fetch course details via GET request.

        Args:
            course_id: 5-digit course number (e.g., "15112")
            semester: Semester code (e.g., "S26")

        Returns:
            Dict with description, prerequisites, etc.
        """
        # Remove any hyphens
        course_num = course_id.replace("-", "")

        url = f"{self.BASE_URL}/courseDetails"
        params = {
            "COURSE": course_num,
            "SEMESTER": semester.upper()  # CMU SOC requires uppercase
        }

        try:
            response = self.session.get(url, params=params, timeout=15, verify=self.verify_ssl)
            response.raise_for_status()
            return self._parse_course_detail(response.text)
        except requests.RequestException as e:
            self._log(f"    Error fetching detail for {course_id}: {e}")
            return {}

    def _parse_course_detail(self, html: str) -> Dict:
        """
        Parse course detail HTML fragment.

        Args:
            html: HTML content from courseDetails response

        Returns:
            Dict with description, prerequisites
        """
        soup = BeautifulSoup(html, 'html.parser')
        result = {
            'description': '',
            'prerequisites': ''
        }

        # Description: Look for <h4>Description:</h4> followed by <p>
        desc_header = soup.find(['h4', 'h5', 'strong'], string=re.compile(r'Description', re.I))
        if desc_header:
            # Try next sibling <p>
            next_p = desc_header.find_next('p')
            if next_p:
                result['description'] = next_p.get_text(strip=True)
            else:
                # Maybe it's in a div or directly after
                parent = desc_header.parent
                if parent:
                    text = parent.get_text(strip=True)
                    # Remove the "Description:" prefix
                    text = re.sub(r'^Description:?\s*', '', text)
                    result['description'] = text

        # Prerequisites: Look for <dt>Prerequisites</dt> followed by <dd>
        prereq_dt = soup.find(['dt', 'strong', 'b'], string=re.compile(r'Prerequisite', re.I))
        if prereq_dt:
            next_dd = prereq_dt.find_next(['dd', 'p', 'span'])
            if next_dd:
                result['prerequisites'] = next_dd.get_text(strip=True)

        # Also try to find in definition lists
        if not result['prerequisites']:
            dl = soup.find('dl')
            if dl:
                for dt in dl.find_all('dt'):
                    if 'prerequisite' in dt.get_text().lower():
                        dd = dt.find_next_sibling('dd')
                        if dd:
                            result['prerequisites'] = dd.get_text(strip=True)
                            break

        return result

    def _format_course_id(self, course_id: str) -> str:
        """
        Format course ID to XX-XXX format.

        Args:
            course_id: Raw course ID (e.g., "15112")

        Returns:
            Formatted ID (e.g., "15-112")
        """
        # Remove any existing hyphens
        clean_id = course_id.replace("-", "")

        # If 5 digits, format as XX-XXX
        if len(clean_id) == 5 and clean_id.isdigit():
            return f"{clean_id[:2]}-{clean_id[2:]}"

        return course_id

    def _parse_units(self, units_str) -> int:
        """
        Parse units string to integer.

        Args:
            units_str: Units string (e.g., "12", "9.0", "VAR")

        Returns:
            Integer units (0 if not parseable)
        """
        if isinstance(units_str, (int, float)):
            return int(units_str)

        try:
            # Extract first number
            match = re.search(r'(\d+)', str(units_str))
            if match:
                return int(match.group(1))
        except:
            pass

        return 0

    def _parse_prerequisites(self, prereq_str: str) -> List[str]:
        """
        Parse prerequisites string into list.

        Args:
            prereq_str: Raw prerequisites text

        Returns:
            List of prerequisite course IDs
        """
        if not prereq_str:
            return []

        # Find all course IDs (XX-XXX or XXXXX format)
        pattern = r'\b(\d{2}-\d{3}|\d{5})\b'
        matches = re.findall(pattern, prereq_str)

        # Format all to XX-XXX
        result = []
        for match in matches:
            formatted = self._format_course_id(match)
            if formatted not in result:
                result.append(formatted)

        return result

    def save_courses(self, courses: List[Course], path: str = None, merge: bool = True):
        """
        Save courses to JSON file.

        Args:
            courses: List of Course objects
            path: Output file path
            merge: Whether to merge with existing data
        """
        if path is None:
            path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "data", "courses.json"
            )

        # Ensure directory exists
        os.makedirs(os.path.dirname(path), exist_ok=True)

        # Create key function for composite unique key
        def make_key(course_dict):
            cid = course_dict.get('course_id', '')
            sem = course_dict.get('semester', '')
            return f"{cid}_{sem}" if sem else cid

        # Convert to dicts
        new_courses_dict = {make_key(c.to_dict()): c.to_dict() for c in courses}

        # Merge with existing if requested
        if merge and os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    existing = json.load(f)

                # Convert existing list to dict
                if isinstance(existing, list):
                    existing_dict = {make_key(c): c for c in existing}
                else:
                    existing_dict = existing

                # Merge: new overwrites existing
                existing_dict.update(new_courses_dict)
                new_courses_dict = existing_dict

            except Exception as e:
                self._log(f"Warning: Could not merge with existing file: {e}")

        # Save as list
        courses_list = list(new_courses_dict.values())

        with open(path, 'w') as f:
            json.dump(courses_list, f, indent=2)

        self._log(f"Saved {len(courses_list)} courses to {path}")


# CLI for testing
if __name__ == "__main__":
    import sys

    semester = sys.argv[1] if len(sys.argv) > 1 else "S26"
    dept = sys.argv[2] if len(sys.argv) > 2 else None
    limit = int(sys.argv[3]) if len(sys.argv) > 3 else 10

    print(f"Testing SOC Fetcher: semester={semester}, dept={dept}, limit={limit}")

    fetcher = SOCCourseFetcher()
    courses = fetcher.fetch_courses(
        max_courses=limit,
        department=dept,
        semester=semester
    )

    print(f"\nFetched {len(courses)} courses:")
    for c in courses[:5]:
        print(f"  {c.course_id}: {c.title}")
        if c.description:
            print(f"    Description: {c.description[:100]}...")
