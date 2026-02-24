#!/usr/bin/env python3
"""
通过已配置的数据源执行 SQL 获取数据（供 bash 调用）。

与业务无关：根据连接信息（环境变量中的 URL）与 SQL、可选参数执行查询并输出 JSON。
Agent 通过基础工具 bash 调用本脚本，无需在 config 中单独注册 data_fetch_db 工具。
连接串通过环境变量传入，例如 DATABASE_URL 或脚本参数 --connection-url-env 指定变量名。

用法:
  export DATABASE_URL="mysql+pymysql://user:pass@host:3306/db"
  python fetch_db.py --sql "SELECT * FROM t WHERE id = %(id)s" --params '{"id": "1"}'
  python fetch_db.py --connection-url-env ANALYTICS_DB_URL --sql "SELECT 1"
"""

import argparse
import json
import os
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description="数据库查询数据获取")
    parser.add_argument("--connection-url-env", default="DATABASE_URL", help="存放连接 URL 的环境变量名")
    parser.add_argument("--sql", required=True, help="要执行的 SQL，支持 %(name)s 占位")
    parser.add_argument("--params", default="{}", help="参数 JSON，与 SQL 占位对应")
    args = parser.parse_args()

    url = os.environ.get(args.connection_url_env, "").strip()
    if not url:
        print(json.dumps({"error": f"环境变量 {args.connection_url_env} 未设置或为空"}, ensure_ascii=False))
        return 1

    params = {}
    if args.params.strip():
        try:
            params = json.loads(args.params)
        except json.JSONDecodeError as e:
            print(json.dumps({"error": f"params 不是合法 JSON: {e}"}, ensure_ascii=False))
            return 1

    try:
        import sqlalchemy
        from sqlalchemy import text
        engine = sqlalchemy.create_engine(url)
        with engine.connect() as conn:
            if params:
                result = conn.execute(text(args.sql), params)
            else:
                result = conn.execute(text(args.sql))
            rows = result.mappings().fetchall()
            data = [dict(r) for r in rows]
        print(json.dumps(data, ensure_ascii=False, indent=2, default=str))
        return 0
    except ImportError:
        print(json.dumps({"error": "需要安装 sqlalchemy 及对应驱动，例如: pip install sqlalchemy pymysql"}, ensure_ascii=False))
        return 1
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    sys.exit(main())
