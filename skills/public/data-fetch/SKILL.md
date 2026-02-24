---
name: data-fetch
description: 通过 HTTP 接口或数据库获取数据。使用 bash 调用本技能下的脚本 fetch_api.py / fetch_db.py，无需在 config 中注册额外工具。适用于需要按 URL+参数请求接口、或按 SQL+数据源执行查询的任何场景（如老品诊断、报表、画像等）。
---

# 通用数据获取（脚本方式）

## 概述

数据获取的本质只有两种：**接口查询**（URL + 请求参数/体）和 **数据库查询**（数据源连接 + SQL）。本技能提供两个可被 **bash** 调用的脚本，不占用 config 中的 tool 名额。

- **fetch_api.py**：发起 HTTP 请求，差异仅在 URL 与请求参数。
- **fetch_db.py**：执行 SQL 查询，差异仅在连接 URL（环境变量）与 SQL。

## 何时使用

- 需要调用内部或外部 REST API 获取数据时，用 bash 执行 `fetch_api.py`。
- 需要从已配置的数据库（通过环境变量提供连接串）执行只读查询时，用 bash 执行 `fetch_db.py`。

## 脚本路径（沙箱内）

- 接口：`/mnt/skills/public/data-fetch/scripts/fetch_api.py`
- 数据库：`/mnt/skills/public/data-fetch/scripts/fetch_db.py`

## fetch_api 用法

使用 **bash** 工具执行，例如：

```bash
python /mnt/skills/public/data-fetch/scripts/fetch_api.py \
  --url "https://api.example.com/v1/query" \
  --method GET \
  --params '{"goods_id": "123", "data_range": "2025-01-01~2025-01-31"}'
```

POST 且带 body：

```bash
python /mnt/skills/public/data-fetch/scripts/fetch_api.py \
  --url "https://api.example.com/v1/query" \
  --method POST \
  --body '{"goods_id": "123", "data_range": "2025-01-01~2025-01-31"}'
```

| 参数 | 必填 | 说明 |
|------|------|------|
| --url | 是 | 完整请求 URL |
| --method | 否 | 默认 GET；可选 POST, PUT, PATCH, DELETE |
| --headers | 否 | 请求头 JSON |
| --params | 否 | 查询参数 JSON（GET 常用） |
| --body | 否 | 请求体 JSON（POST 常用） |

## fetch_db 用法

连接串由**环境变量**提供（如 `DATABASE_URL`），使用 **bash** 工具执行，例如：

```bash
python /mnt/skills/public/data-fetch/scripts/fetch_db.py \
  --sql "SELECT * FROM target_info WHERE goods_id = %(goods_id)s AND data_range = %(data_range)s" \
  --params '{"goods_id": "123", "data_range": "2025-01-01~2025-01-31"}'
```

指定连接串所在环境变量名：

```bash
python /mnt/skills/public/data-fetch/scripts/fetch_db.py \
  --connection-url-env ANALYTICS_DB_URL \
  --sql "SELECT 1"
```

| 参数 | 必填 | 说明 |
|------|------|------|
| --sql | 是 | 要执行的 SQL，支持 %(name)s 占位 |
| --params | 否 | 参数 JSON，与占位对应 |
| --connection-url-env | 否 | 默认 DATABASE_URL；存放连接 URL 的环境变量名 |

沙箱或运行环境需已设置对应环境变量（如 `DATABASE_URL`），并安装 `sqlalchemy` 及对应驱动（如 `pymysql`）。

## 与业务的关系

- 本技能不包含任何业务逻辑，仅提供「按 URL 请求」和「按 SQL 查询」两种能力。
- 具体用哪个 URL、传哪些参数、用哪条 SQL，由调用方（如老品诊断 Skill）在文档或 references 中说明；部署时在环境或配置中提供 base_url、环境变量等即可。
