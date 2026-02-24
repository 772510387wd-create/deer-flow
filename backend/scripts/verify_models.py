#!/usr/bin/env python3
"""验证 config.yaml 中的模型配置是否生效。

用法（在 backend 目录下执行）:
  python scripts/verify_models.py              # 仅校验配置加载与实例化
  python scripts/verify_models.py --invoke     # 校验并调用模型（会消耗 API）
"""

import argparse
import sys
from pathlib import Path

# 确保 backend/src 在 path 中
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import get_app_config
from src.models import create_chat_model


def main() -> None:
    parser = argparse.ArgumentParser(description="验证 DeerFlow 模型配置")
    parser.add_argument(
        "--invoke",
        action="store_true",
        help="对每个模型执行一次简单 invoke 以验证 API 可用（会消耗额度）",
    )
    args = parser.parse_args()

    print("正在加载 config.yaml ...")
    try:
        config = get_app_config()
    except Exception as e:
        print(f"错误: 无法加载配置 - {e}")
        sys.exit(1)

    if not config.models:
        print("警告: config.yaml 中未配置任何模型 (models 为空)")
        sys.exit(0)

    print(f"已配置 {len(config.models)} 个模型:\n")

    all_ok = True
    for m in config.models:
        print(f"  模型: {m.name} (display_name: {m.display_name or m.name})")
        print(f"    use: {m.use}, model: {m.model}")
        print(f"    supports_vision: {m.supports_vision}, supports_thinking: {m.supports_thinking}")

        try:
            instance = create_chat_model(name=m.name)
            print(f"    实例化: 成功")
        except Exception as e:
            print(f"    实例化: 失败 - {e}")
            all_ok = False
            print()
            continue

        if args.invoke:
            try:
                from langchain_core.messages import HumanMessage

                resp = instance.invoke([HumanMessage(content="Reply with exactly: OK")])
                text = getattr(resp, "content", str(resp)) or ""
                print(f"    invoke 测试: 成功 (回复: {text[:50]}...)")
            except Exception as e:
                print(f"    invoke 测试: 失败 - {e}")
                all_ok = False
        print()

    if all_ok:
        print("所有模型配置验证通过。")
    else:
        print("存在验证失败，请检查 config.yaml 与 API 密钥。")
        sys.exit(1)


if __name__ == "__main__":
    main()
