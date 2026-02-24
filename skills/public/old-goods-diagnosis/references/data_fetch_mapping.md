# 老品诊断与建议 — 通用数据获取映射

本文件描述各步骤与 **bash 调用的 data-fetch 脚本**（fetch_api.py / fetch_db.py）的对应关系。部署时请将占位 URL 或 SQL 替换为实际环境配置。脚本路径：`/mnt/skills/public/data-fetch/scripts/`。

## 约定

- `{{goods_id}}`、`{{data_range}}` 等由 agent 从用户输入或上一步结果中替换。
- 若使用 **fetch_api.py**：需配置决策支持服务或内部 API 的 base_url（如环境变量 `OLD_GOODS_DIAGNOSIS_API_URL`），下面 url 为相对路径或完整 URL。
- 若使用 **fetch_db.py**：连接由环境变量提供（如 `DATABASE_URL` 或 `STARROCKS_URL`）；下面 sql 为示例，按实际表结构修改。不依赖 config 的 data_sources。

---

## Step 2：商品新老品标识查询

- **fetch_api.py**：`--url {base_url}/api/tools/query_new_old_tag`，`--method GET`，`--params '{"goods_id": "{{goods_id}}"}'`；或 POST 时 `--body '{"goods_id": "{{goods_id}}"}'`。
- **fetch_db.py**：`--sql "SELECT goods_id, new_old_tag FROM ... WHERE goods_id = %(goods_id)s"`，`--params '{"goods_id": "{{goods_id}}"}'`；连接由环境变量（如 DATABASE_URL）提供。

---

## Step 3a：查询目标信息

- **fetch_api.py**：`--url {base_url}/api/tools/query_target_info`，`--params` 或 `--body` 含 goods_id、data_range。
- **fetch_db.py**：`--sql` 查询目标表，`--params '{"goods_id": "{{goods_id}}", "data_range": "{{data_range}}"}'`。

## Step 3b：查询业务表现数据

- **fetch_api.py**：`--url {base_url}/api/tools/query_business_data`，params/body 含 goods_id、data_range。
- **fetch_db.py**：`--sql` 查询业务表现表，params 同上。

## Step 3c：查询 OKR 信息

- **fetch_api.py**：`--url {base_url}/api/tools/query_okr`，params/body 含 goods_id、data_range。
- **fetch_db.py**：`--sql` 查询 OKR 表，params 同上。

---

## Step 4：基于新老品标签查询知识库

- **fetch_api.py**：`--url {base_url}/api/tools/query_kb`，`--body` 含 Step 2 得到的 new_old_tag（及可选 goods_id）。
- **fetch_db.py**：若知识库在 DB，`--sql` 按标签查内容表，`--params` 含 tag 等。

---

## Step 5：生成诊断结果

- **fetch_api.py**：`--url {base_url}/api/tools/generate_diagnosis`，`--method POST`，`--body` 为 JSON，包含 Step 3、4 的汇总及 goal、description。
- 通常不由 fetch_db 完成（LLM 生成逻辑在后端接口内）。

---

## Step 6：写入诊断结果

- **fetch_api.py**：`--url {base_url}/api/tools/write_diagnosis`，`--method POST`，`--body` 含诊断内容、goods_id、健康度等。
- **fetch_db.py**：`--sql` 为 INSERT/UPDATE 诊断结果表，`--params` 含诊断内容与业务键。
