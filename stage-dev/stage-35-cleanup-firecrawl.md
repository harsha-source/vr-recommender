# Stage 35: 移除 Firecrawl 依赖 & 代码清理

**Date:** 2025-12-11
**Type:** Cleanup / Refactoring
**Focus:** 移除 Firecrawl 依赖，清理旧测试文件，保留 Tavily 用于 VR 应用发现

---

## 1. 背景与目标

### 1.1 Stage 34 完成情况

Stage 34 成功实现了 `SOCCourseFetcher`，现在：
- ✅ 课程数据通过 CMU SOC 系统获取（简单 HTTP 请求）
- ✅ 不再需要 Firecrawl API
- ✅ 所有部门都能获取完整 description

### 1.2 当前问题

1. **Firecrawl 残留**：旧代码和依赖仍在项目中（已不再使用）
2. **测试文件堆积**：30+ 个旧测试脚本占用代码库空间
3. **配置冗余**：Firecrawl API key 仍在配置中

### 1.3 Stage 35 目标

1. **移除 Firecrawl 依赖**（完全删除）
2. **保留 Tavily 依赖**（用于发现新 VR 应用）
3. **清理所有旧测试文件**
4. **验证数据格式兼容性**（确保 skill extraction 正常工作）

---

## 2. 依赖分析

### 2.1 Firecrawl 依赖清单（需移除）

| 文件类型 | 数量 | 操作 |
|---------|------|------|
| 核心实现 | 2 | **删除**（已被 SOCCourseFetcher 替代）|
| 测试文件 | 23 | **删除** |
| requirements.txt | 2 | 移除 `firecrawl-py` |
| 配置文件 | 3 | 移除 `FIRECRAWL_API_KEY` |

**核心文件**（删除）：
- `data_collection/src/data_collection/course_fetcher.py`
- `data_collection/src/data_collection/course_fetcher_improved.py`

### 2.2 Tavily 依赖（保留）

| 文件类型 | 数量 | 操作 |
|---------|------|------|
| 核心实现 | 2 | **保留**（用于发现新 VR 应用）|
| 测试文件 | 6 | **删除**（清理测试文件）|
| requirements.txt | 2 | **保留** `tavily-python` |
| 配置文件 | 3 | **保留** `TAVILY_API_KEY` |

**核心文件**（保留）：
- `vr_app_fetcher.py` → 删除（旧版）
- `vr_app_fetcher_improved.py` → **保留**（生产使用）

---

## 3. "Full Details" vs "Basic Info" 分析

### 3.1 定义

| 类型 | 判断条件 | 来源 |
|------|---------|------|
| **Full Details** | `description` 非空且不含 "not available" | SOC courseDetails API |
| **Basic Info** | `description` 为空 | 仅从课程列表获取 |

### 3.2 当前状态

```python
# soc_course_fetcher.py 第 225-227 行
with_desc = sum(1 for c in all_courses if c.description)
self._log(f"  {with_desc} with full details (descriptions)")
self._log(f"  {len(all_courses) - with_desc} with basic info")
```

当前 `fetch_details=True`（默认），所有课程都会获取详情。

### 3.3 下游影响

| 组件 | 无 Description 时的处理 |
|------|------------------------|
| 知识图谱 | **跳过**（不创建 Course 节点）|
| 技能提取 | **跳过**（无法提取技能）|
| MongoDB | 存储（但 description 为空）|
| RAG 检索 | 无法通过技能桥接查询 |

### 3.4 系统 Robustness

技能提取 pipeline 已有多层防护：
1. **预过滤**：空 description 的课程在处理前被过滤
2. **错误处理**：LLM 调用失败返回空列表
3. **JSON 解析保护**：解析失败不会崩溃

**结论**：系统足够 robust，无需额外修改。

---

## 4. 数据格式兼容性验证

### 4.1 Course 数据模型

```python
@dataclass
class Course:
    course_id: str           # ✅ 必需（skill extraction）
    title: str               # ✅ 必需（skill extraction）
    department: str          # ✅ 可选（知识图谱）
    description: str         # ⭐ 关键（skill extraction 源文本）
    units: int               # ❌ 未使用
    prerequisites: List[str] # ❌ 未使用
    learning_outcomes: List[str] # ❌ 未使用
    semester: str            # ✅ 可选（MongoDB 复合键）
```

### 4.2 Skill Extraction 字段依赖

```python
# pipeline.py 第 62-66 行
title = course.get('title', '')
description = course.get('description', '')
text = f"{title}. {description}"  # 只使用这两个字段
skills = self.extractor.extract_from_text(text, "course")
```

**结论**：SOCCourseFetcher 的输出格式完全兼容。

---

## 5. 实施方案

### 5.1 Phase 1: 删除 Firecrawl 核心文件

**删除文件**：
```
data_collection/src/data_collection/
├── course_fetcher.py           # 删除（被 SOCCourseFetcher 替代）
└── course_fetcher_improved.py  # 删除（被 SOCCourseFetcher 替代）
```

**修改 requirements.txt**：
```python
# requirements.txt (根目录)
- firecrawl-py>=0.0.1  # 移除此行

# data_collection/requirements.txt
- firecrawl-py>=0.0.1  # 移除此行
```

### 5.2 Phase 2: 删除旧版 VR Fetcher

**删除文件**：
```
data_collection/src/data_collection/
└── vr_app_fetcher.py           # 删除（旧版本，improved 版本保留）
```

**保留文件**：
- `vr_app_fetcher_improved.py` → **保留**（使用 Tavily 发现新应用）

### 5.3 Phase 3: 清理所有测试文件

**删除所有测试脚本**（30+ 个文件）：
```
data_collection/
├── test_firecrawl.py
├── test_course_urls.py
├── extract_full_catalog*.py
├── check_department_pages.py
├── test_non_cs_detail.py
├── test_all_5_depts.py
├── test_vr_extraction.py
├── test_vr_apps_improved.py
├── find_cmu_catalogs.py
├── find_course_urls.py
├── search_heinz_detail_urls.py
├── analyze_vrdb.py
├── check_catalog_structure.py
├── test_3_dept_urls.py
├── test_regex_fix.py
├── test_vrdb.py
├── test_course_improved.py
├── check_all_catalogs.py
├── extract_all_dept_urls.py
├── test_main_catalog.py
├── check_catalog_data.py
├── check_scs_course_format.py
├── check_heinz_tepper.py
├── test_course_detail.py
├── debug_catalog_raw.py
└── ... (其他测试文件)
```

### 5.4 Phase 4: 清理 Firecrawl 配置

**修改 .env**：
```bash
- FIRECRAWL_API_KEY=fc-xxx  # 移除此行
# 保留 TAVILY_API_KEY
```

**修改 .env.example**：
```bash
- FIRECRAWL_API_KEY=your-key-here  # 移除此行
# 保留 TAVILY_API_KEY
```

**修改 config_manager.py**：
```python
# 删除 firecrawl_api_key 属性
- @property
- def firecrawl_api_key(self) -> Optional[str]:
-     return self.get("FIRECRAWL_API_KEY")

# 保留 tavily_api_key 属性
@property
def tavily_api_key(self) -> Optional[str]:
    return self.get("TAVILY_API_KEY")  # 保留
```

### 5.5 Phase 5: 更新 __init__.py

```python
# data_collection/src/data_collection/__init__.py
from .soc_course_fetcher import SOCCourseFetcher, Course
from .vr_app_fetcher_improved import VRAppFetcherImproved, VRApp

# 移除旧导入
# from .course_fetcher import CMUCourseFetcher
# from .course_fetcher_improved import CMUCourseFetcherImproved
# from .vr_app_fetcher import VRAppFetcher
```

---

## 6. 文件修改清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `course_fetcher.py` | **删除** | 被 SOCCourseFetcher 替代 |
| `course_fetcher_improved.py` | **删除** | 被 SOCCourseFetcher 替代 |
| `vr_app_fetcher.py` | **删除** | 被 improved 版本替代 |
| `vr_app_fetcher_improved.py` | **保留** | 继续使用 Tavily 发现新应用 |
| `__init__.py` | **修改** | 更新导出 |
| `requirements.txt` (根目录) | **修改** | 仅移除 firecrawl-py |
| `requirements.txt` (data_collection) | **修改** | 仅移除 firecrawl-py |
| `.env` | **修改** | 仅移除 FIRECRAWL_API_KEY |
| `.env.example` | **修改** | 仅移除 FIRECRAWL_API_KEY |
| `config_manager.py` | **修改** | 删除 firecrawl_api_key 属性 |
| 30+ 测试文件 | **删除** | 清理所有旧测试脚本 |

---

## 7. 测试计划

### 7.1 功能验证

- [ ] 课程获取：Admin UI → Update Courses → 验证 "X with full details"
- [ ] VR 应用获取：Admin UI → Refresh VR Apps → 验证 Tavily 搜索正常
- [ ] 技能提取：Admin UI → Extract Skills → 验证正常完成
- [ ] 知识图谱：Admin UI → Rebuild Graph → 验证 Neo4j 节点创建

### 7.2 兼容性验证

- [ ] Docker build 成功（无 firecrawl 依赖）
- [ ] 本地运行正常
- [ ] MongoDB 同步正常
- [ ] Tavily VR 应用发现功能正常

---

## 8. 成功标准

1. ✅ `pip install -r requirements.txt` 不再安装 firecrawl-py
2. ✅ Docker build 成功
3. ✅ Admin UI 课程更新功能正常（使用 SOCCourseFetcher）
4. ✅ Admin UI VR 应用更新功能正常（Tavily + 策划数据库）
5. ✅ 技能提取 pipeline 正常工作
6. ✅ 代码库减少 30+ 个测试文件
7. ✅ 无 import 错误（grep 验证）

---

## 9. 风险评估

| 风险 | 等级 | 缓解措施 |
|------|------|---------|
| 删除文件可能影响其他导入 | 低 | 先 grep 确认无其他引用 |
| config_manager 属性被调用 | 低 | 删除前确认无其他调用者 |
| Docker 构建失败 | 低 | 移除依赖后立即测试构建 |

---

## 10. 已确认事项

| 问题 | 决定 |
|------|------|
| Tavily 依赖 | **保留**（用于发现新 VR 应用）|
| 测试文件 | **全部删除** |
| Firecrawl 配置 | **完全删除**（不保留返回 None 的属性）|
