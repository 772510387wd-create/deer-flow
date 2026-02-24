#!/usr/bin/env python3
"""
通过 HTTP 接口获取数据（供 bash 调用）。

与业务无关：仅根据 URL、请求方法、请求参数/体发起请求并输出响应。
Agent 通过基础工具 bash 调用本脚本，无需在 config 中单独注册 data_fetch_api 工具。

用法:
  python fetch_api.py --url "https://api.example.com/v1/query" [--method GET] [--params '{}'] [--body '{}'] [--headers '{}']
"""

import argparse
import json
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description="HTTP 接口数据获取")
    parser.add_argument("--url", required=True, help="请求 URL")
    parser.add_argument("--method", default="GET", help="GET|POST|PUT|PATCH|DELETE")
    parser.add_argument("--headers", default="{}", help="请求头 JSON")
    parser.add_argument("--params", default="", help="查询参数 JSON，GET 时常用")
    parser.add_argument("--body", default="", help="请求体 JSON，POST 时常用")
    args = parser.parse_args()

    try:
        import requests
    except ImportError:
        print(json.dumps({"error": "requests 未安装，请在环境中 pip install requests"}, ensure_ascii=False))
        return 1

    method = (args.method or "GET").strip().upper()
    headers = {}
    if args.headers.strip():
        headers = json.loads(args.headers)
    params = json.loads(args.params) if args.params.strip() else None
    body = json.loads(args.body) if args.body.strip() else None
    if method in ("GET", "HEAD", "DELETE"):
        body = None

    kwargs = {"timeout": 30, "headers": headers}
    if params:
        kwargs["params"] = params
    if body is not None:
        kwargs["json"] = body

    try:
        resp = requests.request(method, args.url, **kwargs)
        resp.raise_for_status()
        ct = resp.headers.get("Content-Type", "")
        if "application/json" in ct:
            print(json.dumps(resp.json(), ensure_ascii=False, indent=2))
        else:
            print(resp.text)
        return 0
    except requests.RequestException as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        return 1
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"JSON 解析失败: {e}"}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    sys.exit(main())
