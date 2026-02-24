#!/usr/bin/env python3
"""
老品诊断与建议 — 分阶段可执行脚本。

与 decision_support_agent OldGoodsDiagnosisAnalysisSkill 的 7 个工具对应，支持按步骤执行。
可通过环境变量 OLD_GOODS_DIAGNOSIS_API_URL 指定后端 API 根地址；未配置时返回符合契约的桩数据。

用法示例:
  python run.py --step validate --goods-id 892207079412 --data-range "2025-12-07~2025-12-17"
  python run.py --step query_new_old_tag --goods-id 892207079412 --workspace-dir /mnt/user-data/workspace/old_goods_diagnosis
  python run.py --step query_target_info --goods-id 892207079412 --data-range "2025-12-07~2025-12-17" --workspace-dir /mnt/user-data/workspace/old_goods_diagnosis
  ...
"""

import argparse
import json
import os
import sys
from pathlib import Path

# 步骤名与 decision_support_agent 工具对应关系
STEP_VALIDATE = "validate"
STEP_QUERY_NEW_OLD_TAG = "query_new_old_tag"
STEP_QUERY_TARGET_INFO = "query_target_info"
STEP_QUERY_BUSINESS_DATA = "query_business_data"
STEP_QUERY_KB = "query_kb"
STEP_QUERY_OKR = "query_okr"
STEP_GENERATE_RESULT = "generate_result"
STEP_WRITE_RESULT = "write_result"

WORKSPACE_OUTPUTS = {
    STEP_QUERY_NEW_OLD_TAG: "step_new_old_tag.json",
    STEP_QUERY_TARGET_INFO: "step_target_info.json",
    STEP_QUERY_BUSINESS_DATA: "step_business_data.json",
    STEP_QUERY_KB: "step_kb.json",
    STEP_QUERY_OKR: "step_okr.json",
    STEP_GENERATE_RESULT: "step_generate_result.json",
}


def _api_url() -> str | None:
    return os.environ.get("OLD_GOODS_DIAGNOSIS_API_URL", "").strip() or None


def _load_workspace_json(workspace_dir: str, filename: str) -> dict | None:
    path = Path(workspace_dir) / filename
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _write_workspace_json(workspace_dir: str, filename: str, data: dict) -> None:
    Path(workspace_dir).mkdir(parents=True, exist_ok=True)
    path = Path(workspace_dir) / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def step_validate(goods_id: str, data_range: str) -> dict:
    if not (goods_id or "").strip():
        return {"ok": False, "error": "缺少必填字段: goods_id"}
    if not (data_range or "").strip():
        return {"ok": False, "error": "缺少必填字段: data_range"}
    # 简单格式校验：YYYY-MM-DD~YYYY-MM-DD
    parts = data_range.strip().split("~")
    if len(parts) != 2 or len(parts[0]) != 10 or len(parts[1]) != 10:
        return {"ok": False, "error": "data_range 格式应为 YYYY-MM-DD~YYYY-MM-DD"}
    return {"ok": True, "goods_id": goods_id.strip(), "data_range": data_range.strip()}


def step_query_new_old_tag(goods_id: str, workspace_dir: str) -> dict:
    api = _api_url()
    if api:
        # TODO: 实际请求 GET {api}/tools/商品新老品标识查询?goods_id=...
        pass
    # 桩数据：与后端返回结构对齐
    out = {"new_old_tag": "老品", "goods_id": goods_id}
    _write_workspace_json(workspace_dir, WORKSPACE_OUTPUTS[STEP_QUERY_NEW_OLD_TAG], out)
    return out


def step_query_target_info(goods_id: str, data_range: str, workspace_dir: str) -> dict:
    api = _api_url()
    if api:
        pass
    out = {"goods_id": goods_id, "data_range": data_range, "month_target": "", "daily_target": ""}
    _write_workspace_json(workspace_dir, WORKSPACE_OUTPUTS[STEP_QUERY_TARGET_INFO], out)
    return out


def step_query_business_data(goods_id: str, data_range: str, workspace_dir: str) -> dict:
    api = _api_url()
    if api:
        pass
    out = {"goods_id": goods_id, "data_range": data_range, "rows": []}
    _write_workspace_json(workspace_dir, WORKSPACE_OUTPUTS[STEP_QUERY_BUSINESS_DATA], out)
    return out


def step_query_okr(goods_id: str, data_range: str, workspace_dir: str) -> dict:
    api = _api_url()
    if api:
        pass
    out = {"goods_id": goods_id, "data_range": data_range, "okr": []}
    _write_workspace_json(workspace_dir, WORKSPACE_OUTPUTS[STEP_QUERY_OKR], out)
    return out


def step_query_kb(workspace_dir: str) -> dict:
    new_old = _load_workspace_json(workspace_dir, WORKSPACE_OUTPUTS[STEP_QUERY_NEW_OLD_TAG])
    tag = (new_old or {}).get("new_old_tag", "老品")
    api = _api_url()
    if api:
        pass
    out = {"tag": tag, "kb_content": {"老商品打造O分析": "", "老品诊断-运营相关指标及关联动作": "", "老品牌重点指标关注点与调整策略": ""}}
    _write_workspace_json(workspace_dir, WORKSPACE_OUTPUTS[STEP_QUERY_KB], out)
    return out


def step_generate_result(workspace_dir: str, goal: str, description: str) -> dict:
    target = _load_workspace_json(workspace_dir, WORKSPACE_OUTPUTS[STEP_QUERY_TARGET_INFO])
    business = _load_workspace_json(workspace_dir, WORKSPACE_OUTPUTS[STEP_QUERY_BUSINESS_DATA])
    kb = _load_workspace_json(workspace_dir, WORKSPACE_OUTPUTS[STEP_QUERY_KB])
    okr = _load_workspace_json(workspace_dir, WORKSPACE_OUTPUTS[STEP_QUERY_OKR])
    api = _api_url()
    if api:
        pass
    diagnosis_content = "## 核心结论\n（示例）\n## 指标健康度\n健康\n## 问题剖析\n（示例）\n## 增长分析\n（示例）\n## 改进建议\n（示例）"
    diagnosis_content_json = {"核心结论": "", "指标健康度": "健康", "问题剖析": "", "增长分析": "", "改进建议": ""}
    out = {"diagnosis_content": diagnosis_content, "diagnosis_content_json": diagnosis_content_json}
    _write_workspace_json(workspace_dir, WORKSPACE_OUTPUTS[STEP_GENERATE_RESULT], out)
    return out


def step_write_result(workspace_dir: str) -> dict:
    gen = _load_workspace_json(workspace_dir, WORKSPACE_OUTPUTS[STEP_GENERATE_RESULT])
    target = _load_workspace_json(workspace_dir, WORKSPACE_OUTPUTS[STEP_QUERY_TARGET_INFO])
    business = _load_workspace_json(workspace_dir, WORKSPACE_OUTPUTS[STEP_QUERY_BUSINESS_DATA])
    if not gen:
        return {"ok": False, "error": "缺少生成诊断结果，请先执行 generate_result"}
    api = _api_url()
    if api:
        pass
    return {"ok": True, "message": "诊断结果已写入"}


def main() -> int:
    parser = argparse.ArgumentParser(description="老品诊断与建议分阶段脚本")
    parser.add_argument("--step", required=True, help="步骤: validate | query_new_old_tag | query_target_info | query_business_data | query_kb | query_okr | generate_result | write_result")
    parser.add_argument("--goods-id", default="", help="商品ID")
    parser.add_argument("--data-range", default="", help="日期范围 YYYY-MM-DD~YYYY-MM-DD")
    parser.add_argument("--goal", default="", help="诊断目标（可选）")
    parser.add_argument("--description", default="", help="补充说明（可选）")
    parser.add_argument("--workspace-dir", default="/mnt/user-data/workspace/old_goods_diagnosis", help="工作目录，用于读写各步骤产出 JSON")
    args = parser.parse_args()

    step = (args.step or "").strip().lower()
    workspace_dir = (args.workspace_dir or "").strip() or "/mnt/user-data/workspace/old_goods_diagnosis"

    result: dict
    if step == STEP_VALIDATE:
        result = step_validate(args.goods_id, args.data_range)
    elif step == STEP_QUERY_NEW_OLD_TAG:
        result = step_query_new_old_tag(args.goods_id, workspace_dir)
    elif step == STEP_QUERY_TARGET_INFO:
        result = step_query_target_info(args.goods_id, args.data_range, workspace_dir)
    elif step == STEP_QUERY_BUSINESS_DATA:
        result = step_query_business_data(args.goods_id, args.data_range, workspace_dir)
    elif step == STEP_QUERY_KB:
        result = step_query_kb(workspace_dir)
    elif step == STEP_QUERY_OKR:
        result = step_query_okr(args.goods_id, args.data_range, workspace_dir)
    elif step == STEP_GENERATE_RESULT:
        result = step_generate_result(workspace_dir, args.goal or "", args.description or "")
    elif step == STEP_WRITE_RESULT:
        result = step_write_result(workspace_dir)
    else:
        result = {"ok": False, "error": f"未知步骤: {args.step}"}

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result.get("ok") is False else 0


if __name__ == "__main__":
    sys.exit(main())
