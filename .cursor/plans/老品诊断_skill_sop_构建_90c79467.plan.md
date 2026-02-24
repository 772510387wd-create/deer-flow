---
name: 老品诊断 Skill SOP 构建
overview: 在 deer-flow 的 skills/public 下维护与 decision_support_agent 中 OldGoodsDiagnosisAnalysisSkill 对应的技能 old-goods-diagnosis。SOP 以 SKILL.md 为载体，Workflow 写清具体阶段的脚本/命令（方式一 run.py、方式二 bash 调 data-fetch 脚本），数据获取不封装为 config 的 tool，仅用基础工具 bash 执行脚本。
todos: []
isProject: false
---

# 老品诊断与建议 — skills/public 对应 Skill SOP 构建计划

## 1. 两套「技能」的对应关系


| 维度  | decision_support_agent (Python Skill)                                                                                                                      | deer-flow (skills/public)                                                                                                                        |
| --- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| 载体  | [old_goods_diagnosis_analysis_skill.py](D:\Project\ZongWei\RealProject\decision_support_agent\app\agent_core\skills\old_goods_diagnosis_analysis_skill.py) | 已有 `skills/public/old-goods-diagnosis/SKILL.md`                                                                                                  |
| 发现  | IntentAgent 用 pattern 匹配意图                                                                                                                                 | 启动时只加载 `name` + `description`，匹配任务时再读完整 SKILL.md                                                                                                 |
| 执行  | 框架按 `dependencies` 调度 7 个工具                                                                                                                                | Agent 按 SKILL.md 的 SOP 执行：**通过基础工具 bash** 调用本技能 `scripts/run.py` 或 data-fetch 的 `fetch_api.py` / `fetch_db.py`；Workflow 中写**具体阶段的脚本/命令**，而非仅语义描述 |
| 输入  | `requires`: goods_id, data_range；可选 goal, description                                                                                                      | SOP 中明确必填/可选及示例                                                                                                                                  |
| 输出  | standard_out: skill_name, tool_results                                                                                                                     | SOP 中定义期望输出结构与含义                                                                                                                                 |


deer-flow 侧技能机制（简要）：

- **发现**：只解析 SKILL.md 的 YAML 前言中的 **name**、**description**（见 [parser.py](D:\Project\ZongWei\TestProject\deer-flow\backend\src\skills\parser.py)）。
- **激活**：任务与 description 匹配时，agent 通过 `read_file` 读取该技能的 **SKILL.md 全文**（路径由 prompt 提供的 `<location>`，如 `/mnt/skills/public/old-goods-diagnosis/SKILL.md`）。
- **执行**：按 SKILL.md 正文中的步骤、输入输出、依赖顺序执行；每一步对应**可执行的脚本命令**（方式一：run.py；方式二：bash 调 data-fetch 脚本）。可按需读取 `references/`，不重复在 SKILL 中展开 URL/SQL。

因此「对应 skill 的 SOP」= 在 deer-flow 的 skills/public 中维护 **old-goods-diagnosis** 目录，**用 SKILL.md 的正文把标准操作流程写清楚**，且 **Workflow 包含具体阶段的脚本代码/命令**，与 Python skill 的意图、输入、工具链与输出对齐。

---

## 2. 数据获取的构建方式（与规范对齐）

**不在 config 中配置 data_fetch_api / data_fetch_db。** 数据获取能力由 **data-fetch 技能**的脚本提供，agent 仅用**基础工具**执行：

- **基础工具**（config 保持现状）：web（web_search, web_fetch, image_search）、file:read（ls, read_file）、file:write（write_file, str_replace）、**bash**。
- **接口查询**：URL + 方法 + 参数/体 → 用 **bash** 执行 `python /mnt/skills/public/data-fetch/scripts/fetch_api.py ...`。
- **数据库查询**：连接（环境变量）+ SQL + 参数 → 用 **bash** 执行 `python /mnt/skills/public/data-fetch/scripts/fetch_db.py ...`。

原 7 个 tool（商品新老品标识、查询目标信息、查询业务表现数据、查知识库、查询 OKR、生成诊断结果、写入诊断结果）全部通过 **bash + data-fetch 脚本**（及可选本技能 `scripts/run.py` 编排）完成，无需在 config 中为任一步骤单独注册 tool。具体 URL/SQL 由 `references/data_fetch_mapping.md` 或部署环境提供。

---

## 3. 目录与命名

- **路径**：`deer-flow/skills/public/old-goods-diagnosis/`
- **name**：`old-goods-diagnosis`（与目录一致，小写+连字符）
- **description**：一句话说明「做什么 + 何时用」，并包含关键词：老品、诊断、建议、goods_id、data_range、目标、健康度、问题剖析、增长分析、改进建议等（≤1024 字符）。

---

## 4. SKILL.md 正文 SOP 结构（含具体脚本）

1. **When to use this skill**
  与 Python 的 pattern/desc 对齐：用户表达包含「老品诊断」「老品建议」或要针对某商品做诊断、问题剖析/增长分析/改进建议时使用。
2. **Inputs**
  **必填**：`goods_id`、`data_range`（格式 `YYYY-MM-DD~YYYY-MM-DD`）。**可选**：`goal`、`description`。可给与 Python skill 一致的输入示例。
3. **Workflow（核心 SOP）**
  - 按 Python skill 的 `tool_names` 与 `dependencies` 写成**有序步骤**（Step 1 校验 → Step 2 新老品标识 → Step 3 目标/业务/OKR 可并行 → Step 4 知识库 → Step 5 生成诊断 → Step 6 写入结果），并配 Mermaid 依赖图。  
  - **每一步写清两种执行方式的具体命令**：  
    - **方式一**：本技能 `scripts/run.py` 的 bash 调用示例（`--step xxx`、`--goods-id`、`--data-range`、`--workspace-dir`）。  
    - **方式二**：bash 调用 data-fetch 的 `fetch_api.py` / `fetch_db.py` 的示例或说明，具体 URL/SQL 见 [references/data_fetch_mapping.md](references/data_fetch_mapping.md)。
  - 每一步注明：**输入来源、执行动作、产出物**。SOP 是**具体阶段的脚本代码/命令**，而非仅「调用 XX 接口」的语义描述。
4. **Output**
  与 Python skill 的 standard_out 对齐：skill_name、tool_results；生成诊断结果的 diagnosis_content / diagnosis_content_json；写入结果的持久化含义。
5. **Quality checklist（可选）**
  输入含 goods_id、data_range；知识库在新老品标识之后；生成诊断在目标/业务/知识库/OKR 齐备后；写入在生成之后并带目标与业务数据。
6. **References（渐进式披露）**
  详细 URL/SQL、表结构、后端工具名对照放在 `references/data_fetch_mapping.md`、`references/workflow.md`，SKILL 中仅摘要并链接「详见 references/xxx」，避免重复。

---

## 5. 实施项清单


| 序号  | 内容                                                                                                                                                           |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1   | 保持目录 `skills/public/old-goods-diagnosis/`，内含 `SKILL.md`、`scripts/run.py`、`references/workflow.md`、`references/data_fetch_mapping.md`。                        |
| 2   | SKILL.md：YAML 含 `name: old-goods-diagnosis`、`description`（含老品/诊断/建议/goods_id/data_range 等关键词，≤1024 字符）。                                                      |
| 3   | SKILL.md 正文：When to use、Inputs、Workflow（6 步 + 依赖图），**每步含方式一 run.py 与方式二 bash 调 data-fetch 的具体命令或链接**；Output、Quality checklist；对长表/URL/SQL 仅摘要并链到 references。 |
| 4   | 确保 Note 与步骤中无「Agent 工具」等过时表述，统一为「方式一 run.py；方式二 bash 调 data-fetch 脚本」。                                                                                       |
| 5   | **不**在 config 中添加 data_fetch_api / data_fetch_db；数据获取仅通过 bash 执行 data-fetch 脚本完成。                                                                            |
| 6   | （可选）若需技能列表展示，可增加 `agents/openai.yaml`；若有诊断报告模板或示例，可放入 `assets/`。                                                                                             |


---

## 6. 注意事项

- **不修改 decision_support_agent**：本计划仅涉及 deer-flow 的 skills/public 中 old-goods-diagnosis 的维护与对齐，不改动 Python skill 或后端。  
- **执行环境**：deer-flow agent 使用**基础工具**（web、file:read、file:write、**bash**）；「老品诊断」各步通过 **bash 执行脚本**（run.py 或 data-fetch 的 fetch_api/fetch_db）完成，不在 config 中配置 data_fetch 类 tool。  
- **Workflow 内容**：SOP 中 Workflow 为**具体阶段的脚本/命令**，便于 agent 直接执行，而非仅语义流程说明。  
- **与规范一致**：SKILL 为核、scripts 执行、references 按需；data-fetch 为独立技能提供通用数据获取脚本，old-goods-diagnosis 只描述何时调哪个脚本、参数从哪来。

按上述项即可在 skills/public 中维护与 `old_goods_diagnosis_analysis_skill.py` 对应的 skill SOP，并保持与技能规范及渐进式披露一致。