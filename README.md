# Helper Paper Skill

## 一句话说明

`helper-paper` 是一个 Codex 本地 skill，用来把英文论文阅读变成可执行的每日流程：筛论文、下载 PDF、生成中英对照 reader、带你读论文、检查你的理解，并把审稿人视角的写作提醒沉淀成长期记忆。

## 效果与特点

- **每天有入口**：打开 Obsidian 的 `paper/000_开始这里.md`，就知道今天读哪篇、点哪里、没读完怎么续。
- **英文论文可读**：默认生成中英对照 reader，不要求你直接硬啃全英文 PDF。
- **导师式阅读**：你在精读笔记里写理解，Codex 负责检查、斧正和指出可引用/不可夸大的地方。
- **审稿人教练**：每天只教少量写作 WARN；同一 WARN 被你确认 5 次后归档，后续不再重复轰炸。
- **质量优先翻译**：默认 provider 是 DeepSeek Pro；MiMo token-plan 保留为备用路线。
- **开源工具协同**：主翻译调度 GitHub 开源项目 [binary-husky/gpt_academic](https://github.com/binary-husky/gpt_academic)，摘要复核调度 [kaixindelele/ChatPaper](https://github.com/kaixindelele/ChatPaper)。
- **Obsidian 友好**：论文关系图谱只看 `paper/03_notes` 的论文笔记互链，系统文件不进入主图谱。

## 最终会生成什么

在你的 Obsidian paper vault 中，`helper-paper` 会维护这些产物：

- `00_inbox/pdfs/`：已下载论文 PDF。
- `01_candidates/`：候选论文清单，包含发布日期、venue/status、含金量和优先级。
- `02_daily/`：每日启动记录和未完成事项。
- `03_notes/`：你的精读笔记、理解记录和导师斧正记录。
- `04_full_readers/`：中英对照全文 reader、source map、翻译说明和图表资产。
- `05_reviewer_coach/`：Reviewer Coach 学习记忆、WARN 计数和 5 次归档文件。

## 5 分钟快速开始

在 Windows PowerShell 中运行：

```powershell
git clone <repo-url> helper-paper-skill
cd helper-paper-skill
powershell -NoProfile -ExecutionPolicy Bypass -File .\install.ps1 -Force
```

配置 DeepSeek Pro。不要把 key 写进 README、GitHub 仓库或 Obsidian vault；示例环境变量见 [archive/example-env.md](archive/example-env.md)。

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
2. 安装外部开源工具：把 `gpt_academic` 和 `ChatPaper` clone 到 `E:\skills\external-tools\`。
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
- Python 包：`pdfplumber`、`pypdf`、`pillow`。

安装推荐 Python 包：

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

除 `helper-paper`、`gpt-academic` wrapper、`chatpaper` wrapper 之外，本文后面“配套 Skills 下载清单”列出的其他 skills 都不会由本脚本安装。用户需要自行到 Codex skills 网站、Codex 插件/技能市场、GitHub 或搜索引擎搜索下载。

指定 Codex skills 目录：

```powershell
.\install.ps1 -CodexSkillsDir "C:\Users\<你的用户名>\.codex\skills"
```

如果目标目录已经存在，安装脚本会先备份为：

```text
helper-paper.backup-YYYYMMDD-HHmmss
```

## 外部开源工具：gpt_academic 与 ChatPaper

`helper-paper` 本体不打包大型外部项目源码。本仓库只提供两个 wrapper skills，让 Codex 能调度你本机安装的开源工具。

### gpt_academic

- 来源：GitHub 开源项目 [binary-husky/gpt_academic](https://github.com/binary-husky/gpt_academic)。
- 在本系统中的角色：主翻译后端。
- 负责内容：读取英文论文 PDF 或文本块，生成中文翻译材料，供 `helper-paper` 组装进中英对照 reader。

### ChatPaper

- 来源：GitHub 开源项目 [kaixindelele/ChatPaper](https://github.com/kaixindelele/ChatPaper)。
- 在本系统中的角色：摘要与理解复核后端。
- 负责内容：生成摘要、贡献、方法、局限和阅读问答，帮助用户理解论文。

推荐把外部工具放在：

```text
E:\skills\external-tools\
```

首次安装外部工具：

```powershell
mkdir E:\skills\external-tools
git clone --depth=1 https://github.com/binary-husky/gpt_academic.git E:\skills\external-tools\gpt_academic
git clone --depth=1 https://github.com/kaixindelele/ChatPaper.git E:\skills\external-tools\ChatPaper
```

建议为两个工具分别使用 Python 3.10 环境。当前验证过的本地形式是 conda 环境放在各项目 `.venv` 目录：

```powershell
conda create -p E:\skills\external-tools\gpt_academic\.venv python=3.10 -y
conda create -p E:\skills\external-tools\ChatPaper\.venv python=3.10 -y

E:\skills\external-tools\gpt_academic\.venv\python.exe -m pip install --prefer-binary -r E:\skills\external-tools\gpt_academic\requirements.txt
E:\skills\external-tools\gpt_academic\.venv\python.exe -m pip install "setuptools<81"

E:\skills\external-tools\ChatPaper\.venv\python.exe -m pip install --prefer-binary -r E:\skills\external-tools\ChatPaper\requirements.txt
E:\skills\external-tools\ChatPaper\.venv\python.exe -m pip install "setuptools<81"
```

日常使用时，用户不需要手动打开这两个项目；`helper-paper` 会在需要生成 reader 时调度 wrapper skills。

## API Key 配置

API key 不要写进仓库。运行翻译前通过环境变量或工具自己的安全配置方式提供。

默认 provider 策略是 `auto`：优先使用 DeepSeek Pro 生产路线；Xiaomi MiMo token-plan 保留为备用路线。

DeepSeek Pro 默认需要设置：

- `DEEPSEEK_API_KEY`
- `DEEPSEEK_API_BASE_URL`
- `DEEPSEEK_MODEL`

MiMo token-plan 备用路线需要设置：

- `MIMO_API_KEY`
- `MIMO_API_BASE_URL`
- `MIMO_ANTHROPIC_BASE_URL`
- `MIMO_MODEL`

GPT Academic 走 MiMo token-plan 时还需要：

- `CUSTOM_API_KEY_PATTERN`
- `LLM_MODEL`
- `AVAIL_LLM_MODELS`
- `API_URL_REDIRECT`

完整示例命令见 [archive/example-env.md](archive/example-env.md)。如果没有 API key，或 smoke test 失败，`helper-paper` 只会完成安装和检查，不会替换现有 reader，也不会伪装已经完成翻译。

## 配套 Skills 下载清单

`install.ps1` 只会自动安装 `helper-paper`、`gpt-academic` wrapper、`chatpaper` wrapper。其他 skills 需要用户自己去 Codex skills 网站、Codex 插件/技能市场、GitHub 或搜索引擎搜索下载。

推荐搜索关键词格式：

- `Codex skill <skill-name>`
- `<skill-name> SKILL.md`
- `OpenAI Codex skills <skill-name>`

### 本仓库自动安装

- `helper-paper`
  - 用途：每日论文阅读调度、候选筛选、DeepSeek Pro 默认翻译路线、导师带读、Reviewer Coach、WARN 记忆。
  - 何时用：每天启动论文阅读、更新阅读状态、生成候选和导读时。
  - 搜索关键词：本仓库内置。
- `gpt-academic`
  - 用途：调用本地 `binary-husky/gpt_academic`，作为主翻译后端 wrapper。
  - 何时用：生成英文论文中英对照 reader 的主翻译材料时。
  - 搜索关键词：本仓库 wrapper；外部源码搜 `binary-husky/gpt_academic GitHub`。
- `chatpaper`
  - 用途：调用本地 `kaixindelele/ChatPaper`，生成摘要、贡献、方法、局限和问答复核。
  - 何时用：生成论文导读、方法/贡献/局限复核、阅读问答时。
  - 搜索关键词：本仓库 wrapper；外部源码搜 `kaixindelele ChatPaper GitHub`。

### 核心推荐安装

- `nature-reader`
  - 用途：source-grounded reader 结构、稳定块 ID、图表位置和全文对照格式。
  - 何时用：需要可追溯的中英全文 reader、图表就近放置、块 ID 对齐时。
  - 搜索关键词：`Codex skill nature-reader`。
- `pdf`
  - 用途：PDF 抽取、渲染、页面/图表资产检查。
  - 何时用：检查 PDF 是否可读、抽取页面、验证图表资产时。
  - 搜索关键词：`Codex skill pdf`。
- `cs-paper-checklist`
  - 用途：Reviewer Coach 写作提醒和投稿/审稿清单。
  - 何时用：从顶会/期刊审稿人视角提炼写作 WARN 时。
  - 搜索关键词：`Codex skill cs-paper-checklist`。
- `nature-academic-search`
  - 用途：venue/date/DOI/arXiv/ACL/Crossref 元数据核验。
  - 何时用：判断论文发布日期、会议期刊状态、DOI 和引用真实性时。
  - 搜索关键词：`Codex skill nature-academic-search`。
- `citation-relevance-auditor`
  - 用途：判断引用是否真的支撑论点。
  - 何时用：检查某篇论文能不能支撑你的论文表述时。
  - 搜索关键词：`Codex skill citation-relevance-auditor`。

### 论文写作扩展

- `literature-review`：文献综述选题、筛选、结构规划和写作。搜索 `Codex skill literature-review`。
- `ml-paper-writing`：ML/AI 论文结构、实验叙事和投稿准备。搜索 `Codex skill ml-paper-writing`。
- `nature-writing`：Nature 风格论文段落、摘要、引言、讨论写作。搜索 `Codex skill nature-writing`。
- `nature-polishing`：Nature 风格英文润色和学术表达优化。搜索 `Codex skill nature-polishing`。
- `nature-citation`：高质量引用补充和引用段落匹配。搜索 `Codex skill nature-citation`。
- `nature-figure`：高水平论文图表设计、审稿级图形检查。搜索 `Codex skill nature-figure`。
- `nature-data`：数据可用性、FAIR、数据仓库和声明。搜索 `Codex skill nature-data`。
- `nature-response`：审稿意见逐点回复。搜索 `Codex skill nature-response`。
- `nature-paper2ppt`：从论文生成组会/汇报 PPT。搜索 `Codex skill nature-paper2ppt`。

### 交付与维护扩展

- `doc` / `documents`：Word 文档创建、修改、渲染和版式检查。搜索 `Codex skill doc` 或 `Codex documents plugin`。
- `presentations`：PowerPoint 创建、修改、渲染和导出。搜索 `Codex presentations plugin`。
- `avoid-ai-writing`：清理英文/中文文本中的 AI 写作痕迹。搜索 `Codex skill avoid-ai-writing`。
- `chinese-de-aigc`：中文论文降 AIGC 痕迹。搜索 `Codex skill chinese-de-aigc`。
- `skill-installer`：从 curated list 或 GitHub repo 安装 Codex skills。搜索 `Codex skill-installer`。
- `skill-creator`：更新、打包或校验 skill 结构。搜索 `Codex skill-creator`。

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

部分 plugin skills 可能安装在 Codex 插件目录中，不一定出现在 `$env:USERPROFILE\.codex\skills`，此检查只作为本机可用性提示。

如果你使用默认论文库路径，可以继续检查 vault：

```powershell
python C:\Users\<你的用户名>\.codex\skills\helper-paper\scripts\check_paper_vault.py --root "E:\sci\commercial science\commercialscience\paper"
```

如果你的 Obsidian paper vault 在其他位置，把 `--root` 改成你的 `paper` 目录。

## 默认 Obsidian paper vault

当前 skill 默认围绕以下路径工作：

```text
E:\sci\commercial science\commercialscience\paper
```

推荐 vault 入口是：

```text
paper\000_开始这里.md
```

如果给其他人使用，可以让对方创建同名结构，或在安装后修改 `helper-paper/SKILL.md` 与 `helper-paper/references/orchestration.md` 中的默认路径。

## 目录结构

```text
helper-paper-skill/
├── README.md
├── install.ps1
├── .gitignore
├── archive/
│   └── example-env.md
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
```

## 更新方法

如果本仓库已经绑定 GitHub，进入仓库根目录：

```powershell
cd E:\skills\helper-paper-skill
git pull
.\install.ps1
```

外部翻译工具更新：

```powershell
cd E:\skills\external-tools\gpt_academic
git pull
.\.venv\python.exe -m pip install --prefer-binary -r requirements.txt
.\.venv\python.exe -m pip install "setuptools<81"

cd E:\skills\external-tools\ChatPaper
git pull
.\.venv\python.exe -m pip install --prefer-binary -r requirements.txt
.\.venv\python.exe -m pip install "setuptools<81"
```

更新后再次运行“验证安装”中的命令。

## 故障排查

P1 重译后沉淀下来的硬规则，后续 P4/P5 也按这个执行：

- MiMo key 可用但返回 `Invalid API Key`：token-plan key 必须用 `https://token-plan-cn.xiaomimimo.com/v1`。
- 工具自动用了旧 OpenAI 模型：不要让 `gpt-3.5-turbo-16k` 进入 MiMo，强制使用 `mimo-v2.5-pro`。
- GPT Academic 不认 `tp-...` key：设置 `CUSTOM_API_KEY_PATTERN`，示例见 [archive/example-env.md](archive/example-env.md)。
- MiMo smoke test 200 但内容空：token 太少，smoke test 至少给足输出 token，空内容按失败处理。
- ChatPaper 读错配置：从临时工作目录运行，不从 ChatPaper 仓库根目录读取旧 `apikey.ini`。
- ChatPaper 配置文件报 BOM 错：临时 `apikey.ini` 必须写成无 BOM UTF-8。
- ChatPaper 成功响应被当成失败：运行 `patch_chatpaper_mimo.py`，让 `response_ms` 变成可选字段。
- 中文标签变成 `???`：PowerShell 先设置 UTF-8，再运行含中文脚本。
- 翻译中途失败覆盖旧 reader：必须先生成到 `_staging`，校验通过后再备份并替换正式 reader。
- API key 泄漏：完成前扫描 `.codex\skills`、GitHub 包、vault、reader 输出。

相关规则已经写入：

```text
helper-paper/references/translation-failure-playbook.md
helper-paper/scripts/check_translation_providers.py
helper-paper/scripts/check_reader_integrity.py
helper-paper/scripts/patch_chatpaper_mimo.py
```
