# Stage 34: Implement SOC-Based Course Fetcher

**Date:** 2025-12-11
**Type:** Implementation / Refactoring
**Focus:** 用简单 HTTP 请求替代复杂的 Firecrawl 爬虫逻辑

---

## 1. 背景与目标

### 1.1 Stage 33 关键发现

CMU SOC 系统有一个**隐藏的 API**：

| 功能 | 方法 | URL | 响应 |
|------|------|-----|------|
| 课程列表 | POST | `/SOCServlet/search` | HTML 表格 |
| 课程详情 | GET | `/SOCServlet/courseDetails?COURSE=15112&SEMESTER=S26` | HTML 片段 |

### 1.2 当前问题

- 使用 Firecrawl API 爬取（成本高、速度慢）
- 只有 CS (15-XXX) 有详情页，其他部门 "0 with full details"
- 维护 7 个部门目录 URL（分散、不一致）

### 1.3 Stage 34 目标

**用简单的 `requests` + `BeautifulSoup` 替代 Firecrawl**：
- 统一数据源（SOC 系统）
- 所有部门的课程详情
- 降低 API 成本
- 提高获取速度

---

## 2. 实现方案

### 2.1 新建文件：`soc_course_fetcher.py`

在 `data_collection/src/data_collection/` 下创建新的 fetcher：

```python
class SOCCourseFetcher:
    """
    基于 CMU Schedule of Classes (SOC) 系统的课程获取器
    使用简单 HTTP 请求，不依赖 Firecrawl
    """

    BASE_URL = "https://enr-apps.as.cmu.edu/open/SOC/SOCServlet"

    def fetch_courses(self, departments: List[str], semester: str) -> List[Course]:
        """主入口：获取指定部门的所有课程"""
        pass

    def _fetch_course_list(self, dept: str, semester: str) -> List[dict]:
        """Phase 1: POST 请求获取课程列表"""
        pass

    def _fetch_course_detail(self, course_id: str, semester: str) -> dict:
        """Phase 2: GET 请求获取课程详情"""
        pass

    def _parse_course_table(self, html: str) -> List[dict]:
        """解析课程列表 HTML 表格"""
        pass

    def _parse_course_detail(self, html: str) -> dict:
        """解析课程详情 HTML 片段"""
        pass
```

### 2.2 两阶段获取流程

```
┌─────────────────────────────────────────────────────────────┐
│ Phase 1: 获取课程列表                                        │
│                                                             │
│ POST /SOCServlet/search                                     │
│ Payload: SEMESTER=S26&DEPT=CS&GRAD_UNDER=All&...            │
│                                                             │
│ 响应: HTML 表格                                              │
│ 解析: Course ID, Title, Units                               │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ Phase 2: 获取课程详情 (批量)                                 │
│                                                             │
│ GET /SOCServlet/courseDetails?COURSE=15112&SEMESTER=S26     │
│                                                             │
│ 响应: HTML 片段                                              │
│ 解析: Description, Prerequisites, Corequisites              │
│                                                             │
│ 速率限制: 0.1-0.2 秒/请求 (避免 IP 封禁)                     │
└─────────────────────────────────────────────────────────────┘
                           ↓
                    返回 List[Course]
```

### 2.3 API 请求格式

**Phase 1: 课程列表**
```python
def _fetch_course_list(self, dept: str, semester: str) -> List[dict]:
    url = f"{self.BASE_URL}/search"
    payload = {
        "SEMESTER": semester,      # "S26", "F25"
        "DEPT": dept,              # "CS", "ECE", "ROB"
        "GRAD_UNDER": "All",
        "PRG_LOCATION": "All",
        "BEG_TIME": "All",
        "KEYWORD": "",
        "TITLE_ONLY": "YES",
        "SUBMIT": "Retrieve Schedule"
    }
    response = requests.post(url, data=payload)
    return self._parse_course_table(response.text)
```

**Phase 2: 课程详情**
```python
def _fetch_course_detail(self, course_id: str, semester: str) -> dict:
    # course_id: "15-112" → "15112" (去掉横杠)
    course_num = course_id.replace("-", "")
    url = f"{self.BASE_URL}/courseDetails?COURSE={course_num}&SEMESTER={semester}"
    response = requests.get(url)
    return self._parse_course_detail(response.text)
```

### 2.4 HTML 解析逻辑

**课程列表表格解析**
```python
def _parse_course_table(self, html: str) -> List[dict]:
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table', class_='table')
    courses = []
    for row in table.find_all('tr')[1:]:  # 跳过表头
        cols = row.find_all('td')
        if len(cols) >= 3:
            courses.append({
                'course_id': cols[0].get_text(strip=True),  # "15112"
                'title': cols[1].get_text(strip=True),
                'units': cols[2].get_text(strip=True),
            })
    return courses
```

**课程详情解析**
```python
def _parse_course_detail(self, html: str) -> dict:
    soup = BeautifulSoup(html, 'html.parser')

    # Description: <h4>Description:</h4> 后的 <p>
    desc_header = soup.find('h4', string=re.compile(r'Description'))
    description = desc_header.find_next('p').get_text(strip=True) if desc_header else ""

    # Prerequisites: <dt>Prerequisites</dt> 后的 <dd>
    prereq_dt = soup.find('dt', string=re.compile(r'Prerequisites'))
    prerequisites = prereq_dt.find_next('dd').get_text(strip=True) if prereq_dt else ""

    return {
        'description': description,
        'prerequisites': prerequisites,
    }
```

---

## 3. 部门代码映射（硬编码）

**用户确认**：使用硬编码列表

```python
DEPARTMENT_CODES = {
    # School of Computer Science
    "CS": ("Computer Science", "15"),
    "ROB": ("Robotics", "16"),
    "MLG": ("Machine Learning", "10"),
    "HCI": ("Human-Computer Interaction", "05"),
    "LTI": ("Language Technologies", "11"),
    "SDS": ("Software Engineering", "17"),

    # College of Engineering
    "ECE": ("Electrical & Computer Engineering", "18"),
    "MEG": ("Mechanical Engineering", "24"),
    "CEE": ("Civil & Environmental Engineering", "12"),
    "MSE": ("Materials Science", "27"),
    "BME": ("Biomedical Engineering", "42"),

    # Heinz College
    "HNZ": ("Heinz College", "94"),
    "PPM": ("Public Policy", "90"),
    "ISM": ("Information Systems", "95"),

    # Other Schools
    "STA": ("Statistics", "36"),
    "MSC": ("Mathematical Sciences", "21"),
    "TEP": ("Tepper Business", "73"),
}
```

| 部门代码 | 部门名称 | 课程前缀 |
|---------|---------|---------|
| CS | Computer Science | 15-XXX |
| ECE | Electrical & Computer Engineering | 18-XXX |
| ROB | Robotics | 16-XXX |
| MLG | Machine Learning | 10-XXX |
| HCI | Human-Computer Interaction | 05-XXX |
| ISM | Information Systems | 95-XXX |
| HNZ | Heinz College | 94-XXX |
| STA | Statistics | 36-XXX |
| MSC | Mathematical Sciences | 21-XXX |
| MEG | Mechanical Engineering | 24-XXX |
| TEP | Tepper Business | 73-XXX |
| LTI | Language Technologies | 11-XXX |

---

## 4. 文件修改清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `data_collection/src/data_collection/soc_course_fetcher.py` | 新建 | 新的 SOC 获取器 |
| `data_collection/src/data_collection/__init__.py` | 修改 | 导出新类 |
| `src/services/course_update_service.py` | 修改 | 使用新获取器 |
| `requirements.txt` | 修改 | 添加 beautifulsoup4 (如果没有) |

---

## 5. 与现有系统集成

### 5.1 保持接口兼容

新的 `SOCCourseFetcher` 输出格式与现有 `Course` 模型兼容：

```python
Course(
    course_id="15-112",          # 格式化为 XX-XXX
    title="Fundamentals of Programming",
    department="Computer Science",
    description="...",           # 从详情页获取
    units=12,
    prerequisites=["15-110"],    # 从详情页解析
    learning_outcomes=[],        # SOC 可能没有这个字段
    semester="s26"
)
```

### 5.2 完全切换（用户确认）

**不保留** `course_fetcher_improved.py`，直接使用新的 SOC 方案。

---

## 6. 速率限制策略

```python
import time

def fetch_all_course_details(self, courses: List[dict], semester: str) -> List[dict]:
    """批量获取详情，带速率限制"""
    detailed_courses = []
    for i, course in enumerate(courses):
        detail = self._fetch_course_detail(course['course_id'], semester)
        course.update(detail)
        detailed_courses.append(course)

        # 速率限制：每 100 个课程休息 2 秒
        if (i + 1) % 100 == 0:
            time.sleep(2)
        else:
            time.sleep(0.1)  # 每个请求间隔 100ms

    return detailed_courses
```

---

## 7. 测试计划

### 7.1 单元测试
- [ ] `_parse_course_table()` 解析测试
- [ ] `_parse_course_detail()` 解析测试
- [ ] 部门代码映射测试

### 7.2 集成测试
- [ ] 单部门获取测试 (CS, 5 课程)
- [ ] 多部门获取测试 (3 部门, 各 10 课程)
- [ ] 学期切换测试 (S26 vs F25)

### 7.3 验收测试
- [ ] 在 Admin UI 中测试 Update Course Data
- [ ] 验证 "X with full details" 不再是 0
- [ ] 验证数据保存到 MongoDB

---

## 8. 成功标准

Stage 34 完成标准：
1. 新的 `SOCCourseFetcher` 类实现完成
2. 所有部门的课程都能获取 Description 和 Prerequisites
3. Admin UI 显示 "X with full details" > 0
4. 不依赖 Firecrawl API（降低成本）
5. 获取速度比之前快

---

## 9. 下一步 (Stage 35)

- 移除 Firecrawl 依赖
- 清理旧代码
- 性能优化
- 文档更新
