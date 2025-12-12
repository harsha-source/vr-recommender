Stage 36: 移除 Neo4j 认证 - 即插即用部署

 Date: 2025-12-11
 Type: Configuration Simplification
 Focus: 移除 Neo4j 密码认证，实现 VM 部署即插即用

 ---
 1. 背景与目标

 1.1 当前状态

 整个项目已 100% 打包到 Docker 中，部署到学校 VM：
 - ✅ 所有环境变量（API keys, MongoDB URI）已预配置
 - ✅ 数据已预装（Courses, VR Apps, Skills, Knowledge Graph）
 - ✅ Docker pull + run 即可启动

 1.2 问题

 Neo4j 仍需要密码认证：
 - 当前配置：NEO4J_AUTH=neo4j/${NEO4J_PASSWORD:-password}
 - 管理员可能需要手动配置密码
 - 增加了部署复杂性

 1.3 Stage 36 目标

 移除 Neo4j 认证，使 Docker 启动后：
 - Neo4j 无需密码即可连接
 - 管理员无需任何额外配置
 - 真正实现 "拉取即运行"

 ---
 2. 当前 Neo4j 配置分析

 2.1 涉及文件

 | 文件                      | 位置        | 当前配置                                         |
 |-------------------------|-----------|----------------------------------------------|
 | docker-compose.prod.yml | 第 55 行    | NEO4J_AUTH=neo4j/${NEO4J_PASSWORD:-password} |
 | connection.py           | 第 11-20 行 | auth=(self.user, self.password)              |
 | .env                    | 第 4-6 行   | NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD        |
 | config_manager.py       | 第 94-95 行 | neo4j_uri property                           |
 | flask_api.py            | 第 420 行   | NEO4J_URI 在 managed_keys 中                   |

 2.2 连接流程

 docker-compose.prod.yml
     ↓ 设置 NEO4J_AUTH=neo4j/password
     ↓
 Neo4j 容器启动（需要认证）
     ↓
 connection.py
     ↓ GraphDatabase.driver(uri, auth=(user, password))
     ↓
 成功连接

 ---
 3. 实施方案

 3.1 Phase 1: 修改 Docker Compose

 文件: docker-compose.prod.yml

 # 修改前 (第 55 行)
 - NEO4J_AUTH=neo4j/${NEO4J_PASSWORD:-password}

 # 修改后
 - NEO4J_AUTH=none

 这将禁用 Neo4j 容器的认证要求。

 3.2 Phase 2: 修改 Python 连接代码

 文件: knowledge_graph/src/knowledge_graph/connection.py

 # 修改前 (第 11-20 行)
 def __init__(self):
     self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
     self.user = os.getenv("NEO4J_USER", "neo4j")
     self.password = os.getenv("NEO4J_PASSWORD", "password")

     self.driver = GraphDatabase.driver(
         self.uri,
         auth=(self.user, self.password)
     )

 # 修改后
 def __init__(self):
     self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")

     # Neo4j 无认证模式
     self.driver = GraphDatabase.driver(self.uri)

 删除 self.user、self.password 和 auth 参数。

 3.3 Phase 3: 清理环境变量

 文件: .env

 # 删除以下行
 - NEO4J_USER=neo4j
 - NEO4J_PASSWORD=password

 # 保留 (URI 仍需要)
 NEO4J_URI=bolt://localhost:7687

 3.4 Phase 4: 更新 Flask API 配置列表

 文件: web/flask_api.py

 # 修改前 (第 420-421 行)
 managed_keys = ["OPENROUTER_API_KEY", "OPENROUTER_MODEL", "TAVILY_API_KEY", "MONGODB_URI", "NEO4J_URI"]
 sensitive_keys = ["OPENROUTER_API_KEY", "TAVILY_API_KEY", "MONGODB_URI", "NEO4J_URI"]

 # 保持不变 - NEO4J_URI 仍然有用（用于显示连接地址）

 3.5 Phase 5: 清理 Config Manager（可选）

 文件: src/config_manager.py

 保留 neo4j_uri property（URI 仍需要），无需修改。

 ---
 4. 文件修改清单

 | 文件                      | 操作  | 修改内容                          |
 |-------------------------|-----|-------------------------------|
 | docker-compose.prod.yml | 修改  | NEO4J_AUTH=none               |
 | connection.py           | 修改  | 移除 auth 参数                    |
 | .env                    | 修改  | 删除 NEO4J_USER, NEO4J_PASSWORD |

 总计: 3 个文件，改动量极小

 ---
 5. 测试计划

 5.1 单元测试

 # 1. 重建 Docker
 docker-compose -f docker-compose.prod.yml down
 docker-compose -f docker-compose.prod.yml build --no-cache
 docker-compose -f docker-compose.prod.yml up -d

 # 2. 等待服务启动
 sleep 30

 # 3. 检查健康状态
 curl http://localhost:5001/health

 # 4. 验证 Neo4j 连接
 docker exec vr-neo4j cypher-shell "MATCH (n) RETURN count(n)"

 5.2 功能验证

 - Docker 启动成功
 - Neo4j 无需密码即可连接
 - Knowledge Graph 查询正常
 - Admin UI → Rebuild Graph 正常
 - RAG 推荐功能正常

 ---
 6. 成功标准

 1. ✅ Neo4j 容器以 NEO4J_AUTH=none 模式启动
 2. ✅ Python 代码无需密码即可连接 Neo4j
 3. ✅ .env 中无 NEO4J_USER 和 NEO4J_PASSWORD
 4. ✅ Docker pull + run 后立即可用
 5. ✅ 所有现有功能正常工作

 ---
 7. 风险评估

 | 风险    | 等级  | 说明                        |
 |-------|-----|---------------------------|
 | 安全性降低 | 低   | Neo4j 在 Docker 内网中，外部无法访问 |
 | 功能影响  | 无   | 移除认证不影响功能                 |
 | 回滚难度  | 低   | 只需改回 3 个文件                |

 ---
 8. 安全考虑

 Neo4j 运行在 Docker 内部网络 vr-net 中：
 - 端口 7687 映射到 localhost（仅本机可访问）
 - 外部网络无法直接连接 Neo4j
 - 在 VM 环境中，这是可接受的安全级别

 ---
 9. 确认事项

 | 问题       | 决定                   |
 |----------|----------------------|
 | MongoDB  | 保持云端 Atlas（已预配置 URI） |
 | API Keys | 保持现状（已预配置在 Docker 中） |
 | 预装数据     | 已实现（无需修改）            |
 | Neo4j 认证 | 移除（Stage 36 核心任务）    |






 