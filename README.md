# Helper Paper Skill

`helper-paper` 是一个 Codex 本地 skill，用来把英文论文阅读变成可执行的每日流程：自动筛论文、下载 PDF、生成中英对照 reader、带你读论文、检查你的理解，并从审稿人视角沉淀写作提醒。

## 你能用它做什么

- 每天说 `$helper-paper start my day` 或“每日论文阅读”，启动论文阅读流程。
- 按发布日期、venue/status、含金量和课题相关性筛选候选论文。
- 自动下载已选论文 PDF，并生成中英对照 reader。
- 默认用 DeepSeek Pro 做高质量翻译；MiMo token-plan 保留为备用。
- 用 `gpt_academic` 做主翻译，用 `ChatPaper` 做摘要、贡献、方法、局限和问答复核。
- 在 Obsidian 里写个人理解笔记，再由 Codex 做导师式检查和斧正。
- 用 Reviewer Coach 记录写作警示；同一 WARN 确认 5 次后归档为长期记忆。

## 5 分钟快速开始

在 Windows PowerShell 中运行：

```powershell
git clone <repo-url> helper-paper-skill
cd helper-paper-skill
powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1 -Force
```

配置 DeepSeek Pro。不要把 key 写进 README、GitHub 仓库或 Obsidian vault；示例环境变量已归档到 `archive/example-env.md`。

检查 provider：

```powershell
python C:\Users\<你的用户名>\.codex\skills\helper-paper\scripts\check_translation_providers.py --provider auto
```

然后在 Codex 中说：

```text
$helper-paper start my day
```

或：

```text
每日论文阅读
```

如果你还没有准备外部翻译工具或 Obsidian paper vault，继续按下面的“第一次完整使用流程”配置。

## 第一次完整使用流程

1. 安装 Codex 本地 skill：运行仓库根目录的 `install.ps1`。
2. 安装外部翻译工具：把 `gpt_academic` 和 `ChatPaper` clone 到 `E:\skills\external-tools\`。
3. 配置 DeepSeek Pro API：设置 `DEEPSEEK_API_KEY`、`DEEPSEEK_API_BASE_URL`、`DEEPSEEK_MODEL`。
4. 准备 Obsidian paper vault：默认路径是 `E:\sci\commercial science\commercialscience\paper`。
5. 运行 provider 检查：确认 `auto` 默认选择 `deepseek`，模型是 `deepseek-v4-pro`。
6. 在 Codex 中启动：`$helper-paper start my day`。
7. 打开 Obsidian 里的 `000_开始这里.md`。
8. 按入口提示阅读：中英 reader -> 精读笔记 -> 理解检查 -> 完成确认。

## 日常使用口令

启动每日阅读：

```text
$helper-paper start my day
```

或：

```text
每日论文阅读
```

写完某一块理解后，让 Codex 检查：

```text
P1 我写完摘要和引言理解了，请检查我的理解。
```

当天没读完，记录明天续读：

```text
P1 今天读到方法部分，请记录未完成，明天继续。
```

完成全文阅读和理解检查后，才更新完成状态：

```text
P1 我已完成全文阅读和理解检查，请更新记忆并安排下一篇。
```

重要规则：

- 中英 reader 已生成不等于你读完。
- AI 导读已生成不等于你读完。
- 只有你写出理解并经过 Codex 检查后，才算完成阅读块。
- 只有你明确说或勾选 `我注意到了 WARN-XXX`，WARN 计数才会增加。

## 安装要求

必需：

- Codex 支持本地 skills。
- Windows PowerShell。
- Git。
- Python 3.10+。

推荐：

- Poppler / `pdftoppm`：用于 PDF 页面截图和图表资产。
- Python 包：

```powershell
python -m pip install pdfplumber pypdf pillow
```

## 安装方法

克隆或下载本仓库后，在仓库根目录运行：

```powershell
.\install.ps1
```

默认会把 `helper-paper/` 安装到：

```text
C:\Users\<你的用户名>\.codex\skills\helper-paper
```

如果仓库中存在 `wrapper-skills/`，安装脚本也会把 `gpt-academic` 和 `chatpaper` wrapper 一起安装到同一个 Codex skills 目录。外部大型源码仍然需要放在 `E:\skills\external-tools\`，不会被复制进 `.codex\skills`。

除 `helper-paper`、`gpt-academic` wrapper、`chatpaper` wrapper 之外，本文后面“配套 Skills 下载清单”列出的其他 skills 都不会由本脚本安装。用户需要自行到 Codex skills 网站、Codex 插件/技能市场、GitHub 或搜索引擎搜索下载；缺失时 `helper-paper` 应报告缺失并降级处理，而不是伪装完成对应能力。

指定 Codex skills 目录：

```powershell
.\install.ps1 -CodexSkillsDir "C:\Users\<你的用户名>\.codex\skills"
```

如果目标目录已经存在，安装脚本会先备份为：

```text
helper-paper.backup-YYYYMMDD-HHmmss
```

## 外部翻译工具

`helper-paper` 本体不打包大型外部项目源码。`gpt_academic` 来源于 GitHub 开源项目 `binary-husky/gpt_academic`，`ChatPaper` 来源于 GitHub 开源项目 `kaixindelele/ChatPaper`；本仓库只提供两个同名 wrapper skills，让 Codex 能调度本地安装的开源工具。推荐把外部工具放在：

```text
E:\skills\external-tools\
```

首次安装：

```powershell
mkdir E:\skills\external-tools
git clone --depth=1 https://github.com/binary-husky/gpt_academic.git E:\skills\external-tools\gpt_academic
git clone --depth=1 https://github.com/kaixindelele/ChatPaper.git E:\skills\external-tools\ChatPaper
`````

## API Key 配置

API key 不要写进仓库。运行翻译前通过环境变量或工具自己的安全配置方式提供。

默认 provider 策略是 `auto`：优先使用 DeepSeek Pro 生产路线；Xiaomi MiMo token-plan 保留为备用路线。

DeepSeek Pro 默认需要设置 `DEEPSEEK_API_KEY`、`DEEPSEEK_API_BASE_URL`、`DEEPSEEK_MODEL`。示例命令见 `archive/example-env.md`。

DeepSeek 当前默认用 `deepseek-v4-pro`，用于质量优先的全文翻译、复核和导师带读；`deepseek-v4-flash` 只在成本或速度优先时使用。`deepseek-chat` / `deepseek-reasoner` 只作为旧配置排查用，计划在 2026-07-24 停用。

MiMo token-plan 备用路线需要设置 `MIMO_API_KEY`、`MIMO_API_BASE_URL`、`MIMO_ANTHROPIC_BASE_URL`、`MIMO_MODEL`。示例命令见 `archive/example-env.md`。

如果你使用的不是 token-plan 订阅 key，而是官方控制台 key，请按你的控制台文档把 `MIMO_API_BASE_URL` 改成对应 base URL。

GPT Academic 走 MiMo token-plan 时还需要 `CUSTOM_API_KEY_PATTERN`、`LLM_MODEL`、`AVAIL_LLM_MODELS`、`API_URL_REDIRECT`。示例命令见 `archive/example-env.md`。

如果没有 API key，或 smoke test 失败，`helper-paper` 只会完成安装和检查，不会替换现有 reader，也不会伪装已经完成翻译。

## 配套 Skills 下载清单

`install.ps1` 只会自动安装 `helper-paper`、`gpt-academic` wrapper、`chatpaper` wrapper。其他 skills 需要用户自己去 Codex skills 网站、Codex 插件/技能市场、GitHub 或搜索引擎搜索下载。

推荐搜索关键词格式：

- `Codex skill <skill-name>`
- `<skill-name> SKILL.md`
- `OpenAI Codex skills <skill-name>`

`gpt-academic` 和 `chatpaper` 是本仓库随附的 wrapper skills；实际翻译/摘要能力来自 GitHub 开源项目 `binary-husky/gpt_academic` 与 `kaixindelele/ChatPaper`。`nature-reader`、`pdf`、`cs-paper-checklist`、`nature-academic-search`、`citation-relevance-auditor` 是核心增强能力；缺失时 `helper-paper` 必须报告缺失并降级。扩展类 skills 不是每日阅读必需，但适合后续做文献综述、论文写作、引用核验、PPT、Word 成稿、降 AI 痕迹等任务。

### 本仓库自动安装

| Skill | 是否自动安装 | 推荐程度 | 用途 | 什么时候会用到 | 用户怎么找 |
| --- | --- | --- | --- | --- | --- |
| `helper-paper` | 是 | 必需 | 每日论文阅读调度、候选筛选、DeepSeek Pro 默认翻译路线、导师带读、Reviewer Coach、WARN 记忆。 | 每天启动论文阅读、更新阅读状态、生成候选和导读时。 | 本仓库内置。 |
| `gpt-academic` | 是 | 必需 | 调用本地 `binary-husky/gpt_academic`，作为主翻译后端 wrapper。 | 生成英文论文中英对照 reader 的主翻译材料时。 | 本仓库 wrapper；外部源码搜 `binary-husky/gpt_academic GitHub`。 |
| `chatpaper` | 是 | 必需 | 调用本地 `kaixindelele/ChatPaper`，生成摘要、贡献、方法、局限和问答复核。 | 生成论文导读、方法/贡献/局限复核、阅读问答时。 | 本仓库 wrapper；外部源码搜 `kaixindelele ChatPaper GitHub`。 |

### 核心推荐安装

| Skill | 是否自动安装 | 推荐程度 | 用途 | 什么时候会用到 | 用户怎么找 |
| --- | --- | --- | --- | --- | --- |
| `nature-reader` | 否 | 强烈推荐 | source-grounded reader 结构、稳定块 ID、图表位置和全文对照格式。 | 需要可追溯的中英全文 reader、图表就近放置、块 ID 对齐时。 | 搜 `Codex skill nature-reader` 或 `nature-reader SKILL.md`。 |
| `pdf` | 否 | 强烈推荐 | PDF 抽取、渲染、页面/图表资产检查。 | 检查 PDF 是否可读、抽取页面、验证图表资产时。 | 搜 `Codex skill pdf` 或 `pdf SKILL.md Codex`。 |
| `cs-paper-checklist` | 否 | 强烈推荐 | Reviewer Coach 写作提醒和投稿/审稿清单。 | 从顶会/期刊审稿人视角提炼写作 WARN 时。 | 搜 `Codex skill cs-paper-checklist`。 |
| `nature-academic-search` | 否 | 强烈推荐 | venue/date/DOI/arXiv/ACL/Crossref 元数据核验。 | 判断论文发布日期、会议期刊状态、DOI 和引用真实性时。 | 搜 `Codex skill nature-academic-search`。 |
| `citation-relevance-auditor` | 否 | 强烈推荐 | 判断引用是否真的支撑论点。 | 检查某篇论文能不能支撑你的论文表述时。 | 搜 `Codex skill citation-relevance-auditor`。 |

### 论文写作扩展

| Skill | 是否自动安装 | 推荐程度 | 用途 | 什么时候会用到 | 用户怎么找 |
| --- | --- | --- | --- | --- | --- |
| `literature-review` | 否 | 推荐 | 文献综述选题、筛选、结构规划和写作。 | 从每日阅读积累转成综述章节时。 | 搜 `Codex skill literature-review`。 |
| `ml-paper-writing` | 否 | 推荐 | ML/AI 论文结构、实验叙事和投稿准备。 | 把项目写成 AI/ML 会议论文时。 | 搜 `Codex skill ml-paper-writing`。 |
| `nature-writing` | 否 | 可选 | Nature 风格论文段落、摘要、引言、讨论写作。 | 需要高水平英文/学术叙事框架时。 | 搜 `Codex skill nature-writing`。 |
| `nature-polishing` | 否 | 可选 | Nature 风格英文润色和学术表达优化。 | 需要润色英文摘要、引言、讨论或标题时。 | 搜 `Codex skill nature-polishing`。 |
| `nature-citation` | 否 | 可选 | 高质量引用补充和引用段落匹配。 | 需要给论文段落找高可信引用时。 | 搜 `Codex skill nature-citation`。 |
| `nature-figure` | 否 | 可选 | 高水平论文图表设计、审稿级图形检查。 | 需要把实验结果做成论文图时。 | 搜 `Codex skill nature-figure`。 |
| `nature-data` | 否 | 可选 | 数据可用性、FAIR、数据仓库和声明。 | 投稿前整理数据可用性声明时。 | 搜 `Codex skill nature-data`。 |
| `nature-response` | 否 | 可选 | 审稿意见逐点回复。 | 论文收到 reviewer comments 后。 | 搜 `Codex skill nature-response`。 |
| `nature-paper2ppt` | 否 | 可选 | 从论文生成组会/汇报 PPT。 | 做 paper sharing、组会、开题或论文汇报时。 | 搜 `Codex skill nature-paper2ppt`。 |

### 交付与维护扩展

| Skill | 是否自动安装 | 推荐程度 | 用途 | 什么时候会用到 | 用户怎么找 |
| --- | --- | --- | --- | --- | --- |
| `doc` / `documents` | 否 | 可选 | Word 文档创建、修改、渲染和版式检查。 | 把阅读成果、论文草稿或报告交付成 `.docx` 时。 | 搜 `Codex skill doc`、`Codex documents plugin`。 |
| `presentations` | 否 | 可选 | PowerPoint 创建、修改、渲染和导出。 | 把论文阅读或项目成果做成 PPT 时。 | 搜 `Codex presentations plugin`。 |
| `avoid-ai-writing` | 否 | 可选 | 清理英文/中文文本中的 AI 写作痕迹。 | 需要让文稿更像人工写作时。 | 搜 `Codex skill avoid-ai-writing`。 |
| `chinese-de-aigc` | 否 | 可选 | 中文论文降 AIGC 痕迹。 | 中文毕业论文、课程论文或报告需要降 AI 痕迹时。 | 搜 `Codex skill chinese-de-aigc`。 |
| `skill-installer` | 否 | 推荐 | 从 curated list 或 GitHub repo 安装 Codex skills。 | 用户想更方便安装上面这些配套 skills 时。 | 搜 `Codex skill-installer` 或 Codex 内置 skill 列表。 |
| `skill-creator` | 否 | 开发维护必需 | 更新、打包或校验 skill 结构。 | 维护 `helper-paper` 或创建新 skill 时。 | 搜 `Codex skill-creator` 或 Codex 系统 skills。 |

## 验证安装

安装后运行：

```powershell
python C:\Users\<你的用户名>\.codex\skills\.system\skill-creator\scripts\quick_validate.py C:\Users\<你的用户名>\.codex\skills\helper-paper
python C:\Users\<你的用户名>\.codex\skills\.system\skill-creator\scripts\quick_validate.py C:\Users\<你的用户名>\.codex\skills\gpt-academic
python C:\Users\<你的用户名>\.codex\skills\.system\skill-creator\scripts\quick_validate.py C:\Users\<你的用户名>\.codex\skills\chatpaper
python C:\Users\<你的用户名>\.codex\skills\helper-paper\scripts\check_translation_providers.py --provider auto --no-smoke
python C:\Users\<你的用户名>\.codex\skills\helper-paper\scripts\patch_chatpaper_mimo.py --check
```

检查配套 skills 是否已在本机 Codex 环境中存在。`[MISSING]` 不代表 `helper-paper` 安装失败，只代表对应增强能力当前不可用：

```powershell
$skills = @(
  "nature-reader",
  "pdf",
  "cs-paper-checklist",
  "nature-academic-search",
  "citation-relevance-auditor",
  "literature-review",
  "ml-paper-writing",
  "nature-writing",
  "nature-polishing",
  "nature-citation",
  "nature-figure",
  "nature-data",
  "nature-response",
  "nature-paper2ppt",
  "doc",
  "documents",
  "presentations",
  "avoid-ai-writing",
  "chinese-de-aigc",
  "skill-installer",
  "skill-creator"
)
foreach ($skill in $skills) {
  $path = Join-Path "$env:USERPROFILE\.codex\skills" "$skill\SKILL.md"
  if (Test-Path -LiteralPath $path) {
    Write-Host "[OK] $skill"
  } else {
    Write-Host "[MISSING] $skill"
  }
}
```

这些配套 skills 缺失不影响 `helper-paper`、`gpt-academic`、`chatpaper` 的安装校验，但会影响全文 reader 结构化、PDF 渲染、Reviewer Coach、元数据核验、引用支撑审计、论文写作、PPT/Word 交付或维护工作流。部分 plugin skills 可能安装在 Codex 插件目录中，不一定出现在 `$env:USERPROFILE\.codex\skills`，此检查只作为本机可用性提示。

如果你使用默认论文库路径，可以继续检查 vault：

```powershell
python C:\Users\<你的用户名>\.codex\skills\helper-paper\scripts\check_paper_vault.py --root "E:\sci\commercial science\commercialscience\paper"
```

如果你的 Obsidian paper vault 在其他位置，把 `--root` 改成你的 `paper` 目录。

## 默认 Obsidian paper vault

当前 skill 默认围绕以下路径工作：

```text
E:\sci\commercial science\commercialscience\paper


## 目录结构

```text
helper-paper-skill/
├── README.md
├── install.ps1
├── .gitignore
├── wrapper-skills/
│   ├── gpt-academic/
│   └── chatpaper/
└── helper-paper/
    ├── SKILL.md
    ├── agents/
    │   └── openai.yaml
    ├── references/
    │   ├── orchestration.md
    │   ├── quality-rules.md
    │   ├── reviewer-coach.md
    │   └── translation-failure-playbook.md
    └── scripts/
        ├── check_paper_vault.py
        ├── check_translation_providers.py
        ├── check_reader_integrity.py
        └── patch_chatpaper_mimo.py
#   h e l p e r - p a p e r  
 