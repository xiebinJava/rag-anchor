# `mattpocock/skills` 研究笔记

研究日期：2026-10-27  
资料范围：仅使用 [GitHub 仓库](https://github.com/mattpocock/skills) `main` 分支中的 README、目录 README、`SKILL.md`、插件 manifest、`.agents` 说明和 ADR。`main` 会变化，下面的链接指向当时的仓库内容。

## 结论摘要

`mattpocock/skills` 是一组给编码 agent 使用的、以软件工程流程和纪律为核心的 skills，不是运行时库，也不是项目脚手架。作者将它们定位为“小、易改、可组合、适用于任何模型”的工程工作流，目标是减少需求误解、反馈不足和代码复杂度增长。[README](https://github.com/mattpocock/skills/blob/main/README.md#L9-L16)

对普通软件项目，最实用的最小闭环是：

1. 每个仓库先运行一次 `setup-matt-pocock-skills`，确定 issue tracker、triage 标签和领域文档位置。
2. 开始需求时用 `grill-with-docs` 澄清目标，并在必要时沉淀 `GLOSSARY.md` / ADR。
3. 多会话或较大的工作用 `to-spec` → `to-tickets`；小改动可直接进入 `implement`。
4. 实现过程用 `tdd` 做 red → green → refactor 的垂直切片。
5. 完成后用 `code-review` 做 Standards / Spec 双轴评审，提交 PR 时让 `pr` 生成摘要、证据和合并风险。
6. 难 bug 走 `diagnosing-bugs`；大规模、模糊的工作才使用 `wayfinder`；架构维护用 `improve-codebase-architecture`。

这是一套有明确偏好的工作方法，不会替项目提供测试、类型检查、issue tracker、浏览器、凭据或部署环境。它能约束 agent 的工作方式，但不能替代这些工程基础设施。

## 1. 仓库是什么，以及目录如何组织

### 仓库定位

顶层 README 将它描述为作者日常用于“real engineering”的 agent skills，并明确强调它们不是一个接管整个流程的重型方法论，而是可组合、可改造的较小单元。[README](https://github.com/mattpocock/skills/blob/main/README.md#L13-L16)

仓库的发布集合由两个 bucket 组成：

| 目录 | 当前角色 | 主要内容 |
| --- | --- | --- |
| [`skills/engineering`](https://github.com/mattpocock/skills/tree/main/skills/engineering) | promoted，日常代码工作 | 澄清、领域建模、设计、规格、票据、实现、TDD、调试、评审、PR、研究等 |
| [`skills/productivity`](https://github.com/mattpocock/skills/tree/main/skills/productivity) | promoted，通用工作流 | grilling、handoff、teach、问卷、重新解释等 |
| [`skills/misc`](https://github.com/mattpocock/skills/tree/main/skills/misc) | 保留但不 promoted | 少用的工具，例如 Claude Code git guardrails、shoehorn 迁移、pre-commit 设置 |
| [`skills/in-progress`](https://github.com/mattpocock/skills/tree/main/skills/in-progress) | beta，公开征求反馈 | 不进插件、不进顶层 README、没有 docs 页面，可能无预警改变或消失 |
| [`skills/deprecated`](https://github.com/mattpocock/skills/tree/main/skills/deprecated) | 退役 | 当前为空 |

这些 bucket 的边界和发布规则写在仓库的 [`CLAUDE.md`](https://github.com/mattpocock/skills/blob/main/CLAUDE.md#L1-L16) 以及各目录 README 中。当前插件 manifest 明确列出 27 个 promoted skills：engineering 20 个，productivity 7 个。[`plugin.json`](https://github.com/mattpocock/skills/blob/main/.claude-plugin/plugin.json#L20-L47)

顶层还有几类重要文件：

- [`.claude-plugin/plugin.json`](https://github.com/mattpocock/skills/blob/main/.claude-plugin/plugin.json)：插件名称、版本、描述和显式 skill 路径列表；当前版本为 `1.3.1`。
- [`.claude-plugin/marketplace.json`](https://github.com/mattpocock/skills/blob/main/.claude-plugin/marketplace.json)：仓库自己的 marketplace 定义。
- [`.agents/install-block.md`](https://github.com/mattpocock/skills/blob/main/.agents/install-block.md)：所有安装说明的 canonical source，规定 managed install 和 skills.sh 两种路线。
- [`.agents/invocation.md`](https://github.com/mattpocock/skills/blob/main/.agents/invocation.md)：解释 user-invoked 与 model-invoked，以及各 harness 的调用约束。
- [`docs/`](https://github.com/mattpocock/skills/tree/main/docs)：engineering/productivity skill 的人类可读文档页面。
- [`scripts/`](https://github.com/mattpocock/skills/tree/main/scripts)：仓库维护脚本；`link-skills.sh` 是维护者开发脚本，不是受支持的用户安装器。[脚本](https://github.com/mattpocock/skills/blob/main/scripts/link-skills.sh#L1-L11)
- [`package.json`](https://github.com/mattpocock/skills/blob/main/package.json)：仓库版本、changesets 和 plugin version 同步脚本，仓库本身是 `private` npm package，不是供项目 `npm install` 的运行时包。[package.json](https://github.com/mattpocock/skills/blob/main/package.json#L1-L19)

### 安装方式

README 明确要求同一个 agent 选择一条路线：插件会自动更新，`skills.sh` 会把可编辑文件复制到项目并由用户手动更新；两者都装会产生重复 skills。[README 安装说明](https://github.com/mattpocock/skills/blob/main/README.md#L21-L24)

#### Codex

```bash
codex plugin marketplace add mattpocock/skills
codex plugin add mattpocock-skills@mattpocock
```

仓库 README 说明 Codex 默认在启动时更新。[README](https://github.com/mattpocock/skills/blob/main/README.md#L37-L46)

#### 其他 README 中列出的路线

```bash
# Claude Code
claude plugin install mattpocock-skills@claude-plugins-official

# GitHub Copilot CLI
copilot plugin marketplace add mattpocock/skills
copilot plugin install mattpocock-skills@mattpocock

# Gemini CLI，两个 promoted bucket 分别安装
gemini skills install https://github.com/mattpocock/skills.git --path skills/engineering
gemini skills install https://github.com/mattpocock/skills.git --path skills/productivity

# 其他 agent，或需要可编辑副本
npx skills@latest add mattpocock/skills -a <agent>
```

Copilot 还需要一次性在 `~/.copilot/settings.json` 配置 `extraKnownMarketplaces` 和 `autoUpdate: true`；VS Code 使用 “Chat: Install Plugin From Source” 并输入仓库 URL。Gemini 需要重新运行两个 install 命令更新；其他 agent 使用 `npx skills@latest update`，若要拿到新增 skill 还要重新运行 `add`。[README 完整安装块](https://github.com/mattpocock/skills/blob/main/README.md#L24-L89)；仓库维护的 canonical 版本也提示不要把 `skills.sh` 与 managed plugin 混装。[`install-block.md`](https://github.com/mattpocock/skills/blob/main/.agents/install-block.md#L4-L17)

### 使用方式

安装后，skills 通过 agent 的 skill picker、slash command 或自然语言触发。仓库按“谁可以触发”分为：

- **User-invoked**：只能由人显式输入，例如 `setup-matt-pocock-skills`、`grill-with-docs`、`to-spec`、`to-tickets`、`implement`。它们负责编排流程，不能被模型隐式调用，也不能由另一个 skill 调用。
- **Model-invoked**：人可以显式使用，模型也可在任务匹配时调用，例如 `tdd`、`domain-modeling`、`codebase-design`、`diagnosing-bugs`、`code-review`、`pr`、`research`。

这条边界不是只有 README 标签：每个 skill 旁边都有 `agents/openai.yaml`。例如 `grill-with-docs` 的 Codex metadata 设置了 `policy.allow_implicit_invocation: false`，而 `tdd` 只有 UI metadata，没有该限制。[invocation 规则](https://github.com/mattpocock/skills/blob/main/.agents/invocation.md#L1-L14)、[`grill-with-docs/agents/openai.yaml`](https://github.com/mattpocock/skills/blob/main/skills/engineering/grill-with-docs/agents/openai.yaml)、[`tdd/agents/openai.yaml`](https://github.com/mattpocock/skills/blob/main/skills/engineering/tdd/agents/openai.yaml)

首次在某个仓库使用 engineering skills，应由人运行：

```text
/setup-matt-pocock-skills
```

它会询问 issue tracker、triage 标签和文档保存位置。默认领域文档布局是单一上下文：根目录 `GLOSSARY.md` 加 `docs/adr/`；只有检测到 monorepo 信号时才建议 `GLOSSARY-MAP.md` 和多上下文布局。[setup skill](https://github.com/mattpocock/skills/blob/main/skills/engineering/setup-matt-pocock-skills/SKILL.md#L5-L13)、[setup 的配置选项](https://github.com/mattpocock/skills/blob/main/skills/engineering/setup-matt-pocock-skills/SKILL.md#L32-L49)

## 2. 普通软件项目的推荐阶段和 skill

下面是从仓库自己的 [`ask-matt`](https://github.com/mattpocock/skills/blob/main/skills/engineering/ask-matt/SKILL.md) 主流程整理出的实用顺序。它是推荐路径，不要求每个项目每次都调用全部 skills。

### 阶段 A：安装和一次性项目配置

**使用：** `setup-matt-pocock-skills`（user-invoked）

先检查远端、已有 `AGENTS.md` / `CLAUDE.md`、glossary、ADR、`.scratch/` 和 monorepo 信号，再确认配置并写入。它支持 GitHub、GitLab、本地 markdown 或用户描述的其他 tracker；没有远端的小项目可以选择 `.scratch/<feature>/`。[setup skill](https://github.com/mattpocock/skills/blob/main/skills/engineering/setup-matt-pocock-skills/SKILL.md#L14-L25)、[issue tracker 选项](https://github.com/mattpocock/skills/blob/main/skills/engineering/setup-matt-pocock-skills/SKILL.md#L32-L49)

### 阶段 B：处理外部进入的 issue 或 PR

**使用：** `triage`（user-invoked，仅当 issue 是外部进入、尚未形成 agent-ready brief）

它将 issue/外部 PR 通过 `bug` / `enhancement` 分类和 `needs-triage`、`needs-info`、`ready-for-agent`、`ready-for-human`、`wontfix` 状态推进，并要求验证复现、查找重复实现和既有拒绝记录。`to-tickets` 生成的 ticket 已经 agent-ready，不应再走 triage。[triage skill](https://github.com/mattpocock/skills/blob/main/skills/engineering/triage/SKILL.md#L5-L13)、[triage 状态与边界](https://github.com/mattpocock/skills/blob/main/skills/engineering/triage/SKILL.md#L19-L37)、[`ask-matt` 的 triage 入口](https://github.com/mattpocock/skills/blob/main/skills/engineering/ask-matt/SKILL.md#L35-L41)

### 阶段 C：澄清需求、建立共享语言

**首选：** `grill-with-docs`（user-invoked）  
**底层：** `grilling` + `domain-modeling`（model-invoked）

在已有工作目录时，仓库建议从 `grill-with-docs` 开始。它会调用 grilling 和 domain modeling，逐轮澄清设计树，并把已确定的术语写进 `GLOSSARY.md`，把难逆且有真实取舍的决定写成 ADR。没有工作目录时使用不落地文档的 `grill-me`。[`ask-matt` 主流程](https://github.com/mattpocock/skills/blob/main/skills/engineering/ask-matt/SKILL.md#L11-L19)、[`grill-with-docs`](https://github.com/mattpocock/skills/blob/main/skills/engineering/grill-with-docs/SKILL.md)、[`domain-modeling`](https://github.com/mattpocock/skills/blob/main/skills/engineering/domain-modeling/SKILL.md#L4-L6)

如果关键问题必须通过可运行的状态模型或 UI 才能回答，先用 `prototype` 做一次性原型；原型不应带生产级持久化、测试和抽象，验证结果要回写到真实实现和 issue，原型本身放在临时 branch。[prototype skill](https://github.com/mattpocock/skills/blob/main/skills/engineering/prototype/SKILL.md#L5-L20)

### 阶段 D：把共识变成规格和可执行工作单元

**多会话、较大功能：** `to-spec` → `to-tickets`  
**单会话、小功能：** 可以跳过这两个，直接 `implement`

`to-spec` 不再访谈，而是综合当前对话和代码库，先确认测试 seam，再把问题、解决方案、用户故事、实现/测试决定和 out-of-scope 发布到配置的 tracker；没有 tracker 配置时应先运行 setup。[to-spec skill](https://github.com/mattpocock/skills/blob/main/skills/engineering/to-spec/SKILL.md#L5-L15)

`to-tickets` 将规格切为可独立验证的 tracer-bullet 垂直切片，并给每张 ticket 声明 blockers；它强调一个切片要贯穿 schema、API、UI、测试，而不是按层切成“先全写后端、再全写前端”。[to-tickets skill](https://github.com/mattpocock/skills/blob/main/skills/engineering/to-tickets/SKILL.md#L5-L34)

若项目是巨大且一开始无法看清路径的工作，才用 `wayfinder` 先建立 issue tracker 上的 decision-ticket map；它默认只解决决策，不直接交付实现，地图清晰后再回到 `to-spec`。[wayfinder skill](https://github.com/mattpocock/skills/blob/main/skills/engineering/wayfinder/SKILL.md#L5-L18)、[`ask-matt` 的大工作入口](https://github.com/mattpocock/skills/blob/main/skills/engineering/ask-matt/SKILL.md#L40-L44)

### 阶段 E：设计模块和测试 seam

**使用：** `codebase-design`（model-invoked，作为设计词汇和参考）；需要扫描既有代码健康时加 `improve-codebase-architecture`（user-invoked）。

`codebase-design` 要求围绕 deep module 设计：小 interface、较多行为隐藏在 implementation 中、在清晰 seam 上测试；还强调“接受依赖而不是自己创建”“返回结果而不是在内部产生副作用”。[codebase-design skill](https://github.com/mattpocock/skills/blob/main/skills/engineering/codebase-design/SKILL.md#L4-L20)、[其可测试性规则](https://github.com/mattpocock/skills/blob/main/skills/engineering/codebase-design/SKILL.md#L49-L81)

`improve-codebase-architecture` 是调查器，不是旧代码自动救援器：它提出 deepening candidates，选中的机会再带回 `grill-with-docs`。README 建议每隔几天运行一次，但应按项目规模和维护成本调整。[README 架构说明](https://github.com/mattpocock/skills/blob/main/README.md#L164-L180)、[`ask-matt` 的 codebase health](https://github.com/mattpocock/skills/blob/main/skills/engineering/ask-matt/SKILL.md#L45-L54)

### 阶段 F：实现和测试

**默认：** `implement` + `tdd`  
**整份规格并行推进：** `implement-spec` + `tdd`

`implement` 按 spec/ticket 工作，在预先约定的 seam 上调用 `tdd`，实现中定期跑类型检查和单文件测试，最后跑完整测试套件，完成后调用 `code-review` 并提交当前 branch。[implement skill](https://github.com/mattpocock/skills/blob/main/skills/engineering/implement/SKILL.md#L5-L15)

`implement-spec` 适合完整规格：读取 ticket task graph，在 integration branch 上对 ready frontier 并行调度 implementer，合并后统一 code review。它要求 worktree、branch、subagent 和 tracker 的关闭规则，普通小改动不值得使用它。[implement-spec skill](https://github.com/mattpocock/skills/blob/main/skills/engineering/implement-spec/SKILL.md#L5-L31)

`tdd` 是每个垂直切片的具体纪律：先写能针对用户行为的失败测试，再写刚好让它通过的代码，再进入下一个切片。测试应通过 public interface / seam 验证行为，不能测 private implementation、内部 mock 结构或水平地把所有测试一次写完。[tdd skill](https://github.com/mattpocock/skills/blob/main/skills/engineering/tdd/SKILL.md#L4-L30)

### 阶段 G：困难 bug 和性能回归

**使用：** `diagnosing-bugs`；修复仍应留下 regression test。

它要求先建立一个已经能对“这个具体 bug”变红的 tight feedback loop，然后再 reproduce/minimise、列 3–5 个可证伪假设、逐个 instrument、先写回归测试再修复，最后清理 debug 日志并重跑原始场景。[diagnosing-bugs skill](https://github.com/mattpocock/skills/blob/main/skills/engineering/diagnosing-bugs/SKILL.md#L5-L18)、[诊断阶段](https://github.com/mattpocock/skills/blob/main/skills/engineering/diagnosing-bugs/SKILL.md#L47-L54)

### 阶段 H：完成前评审和 PR

**使用：** `code-review`；若要创建 PR，再使用 `pr`。

`code-review` 必须有用户指定的 fixed point，先确认 ref 可解析且 diff 非空，然后分成两个不混淆的轴：

- **Standards**：是否符合仓库标准，并检查 Fowler smell baseline。
- **Spec**：是否完整、正确地实现 originating issue/spec，是否发生 scope creep。

没有 spec 时，Spec 轴会明确报告没有 spec，而不是凭空补一个。[code-review skill](https://github.com/mattpocock/skills/blob/main/skills/engineering/code-review/SKILL.md#L4-L18)、[双轴规则](https://github.com/mattpocock/skills/blob/main/skills/engineering/code-review/SKILL.md#L19-L33)

`pr` 的 PR body 只保留三部分：最小的 Summary 视觉化、Before/After Evidence、Merge Danger（one-way/two-way door 和 blast radius）。[pr skill](https://github.com/mattpocock/skills/blob/main/skills/engineering/pr/SKILL.md#L11-L31)、[Evidence / Merge Danger](https://github.com/mattpocock/skills/blob/main/skills/engineering/pr/SKILL.md#L149-L160)

### 阶段 I：复盘和持续维护

**使用：** `retro`；代码库健康巡检用 `improve-codebase-architecture`。

`retro` 复盘的是 agent 环境，不是直接重写业务代码：优先找导航指针、可自动化的检查、应交给 reviewer 的编码标准、信息访问和昂贵工具调用。它特别指出，没有 lint/typecheck/test 的 pre-commit 或 CI guardrail 本身就是一个发现。[retro skill](https://github.com/mattpocock/skills/blob/main/skills/engineering/retro/SKILL.md#L5-L23)

### 其他按需 skill

- `research`：需要外部事实时，读取一手资料并留下有引用的 Markdown，结果再带回 `grill-with-docs` 的思考过程。[research skill](https://github.com/mattpocock/skills/blob/main/skills/engineering/research/SKILL.md)
- `wizard`：只有需要人亲自打开第三方 dashboard、配置凭据、写 CI secret 或执行迁移时使用；agent 能自己做的步骤不应包装成 wizard。[wizard skill](https://github.com/mattpocock/skills/blob/main/skills/engineering/wizard/SKILL.md#L1-L8)
- `handoff`：跨 agent、跨目录或跨 session 交接时写临时 handoff，不复制已经存在的 spec、issue、ADR、commit 或 diff。[handoff skill](https://github.com/mattpocock/skills/blob/main/skills/productivity/handoff/SKILL.md#L1-L12)
- `grill-me`：没有工作目录时的无状态澄清入口；有工作目录时优先 `grill-with-docs`。[grill-me](https://github.com/mattpocock/skills/blob/main/skills/productivity/grill-me/SKILL.md)、[`ask-matt` 的 standalone 说明](https://github.com/mattpocock/skills/blob/main/skills/engineering/ask-matt/SKILL.md#L64-L70)

## 3. 前置条件、局限和 Codex 适配

### 前置条件

1. **要有兼容的 agent harness。** 插件、slash command、skill picker、`agents/openai.yaml` 和 `skills.sh` 的行为取决于 agent。仓库把“任意模型可用”作为设计目标，但不同 harness 的安装和隐式调用策略仍不同。
2. **先完成 repo setup。** engineering skills 依赖 issue tracker 和 domain docs 配置。`to-spec`、`to-tickets`、`wayfinder`、`implement-spec` 在没有 tracker 配置时都会要求先运行 setup。[to-spec](https://github.com/mattpocock/skills/blob/main/skills/engineering/to-spec/SKILL.md#L5-L10)、[to-tickets](https://github.com/mattpocock/skills/blob/main/skills/engineering/to-tickets/SKILL.md#L5-L10)、[wayfinder](https://github.com/mattpocock/skills/blob/main/skills/engineering/wayfinder/SKILL.md#L13-L18)
3. **要有可用的反馈回路。** TDD、implement 和调试假设项目能运行测试、类型检查、CLI、HTTP 或浏览器验证；README 也把 static types、browser access 和 automated tests 视为必要反馈来源。[README](https://github.com/mattpocock/skills/blob/main/README.md#L149-L163)
4. **外部 tracker 需要权限和 CLI。** GitHub/GitLab 路线需要相应的仓库权限和 `gh` / `glab` 等环境；本地路线要允许写 `.scratch/`。其他 tracker 需要用户明确描述 workflow，skills 不会凭空猜 API。
5. **大规模实现需要额外执行能力。** `implement-spec` 依赖 task graph、integration branch、独立 worktree、implementer/merger subagent；没有这些条件时使用 `implement` 按 ticket 顺序更稳妥。[implement-spec](https://github.com/mattpocock/skills/blob/main/skills/engineering/implement-spec/SKILL.md#L15-L31)

### 局限和风险

- **它是流程指令，不是质量保证系统。** skill 不会自动让代码正确，也不替代 CI、测试、类型检查、代码审查者、产品决策或安全审查。
- **它有强烈的方法论偏好。** 共享 glossary、深模块、垂直 tracer bullet、tracker blockers、red-green-refactor 和双轴 review 都是作者的工程判断。适合团队前，先按项目规模和已有流程裁剪。
- **setup 会写仓库配置。** 它会先探索和确认，但完成后可能新增或编辑 `CLAUDE.md` / `AGENTS.md`、`docs/agents/*.md`、`GLOSSARY.md`、ADR 或 tracker 标签。第一次使用应明确审阅这些写入内容。[setup 写入规则](https://github.com/mattpocock/skills/blob/main/skills/engineering/setup-matt-pocock-skills/SKILL.md#L50-L95)
- **不要把所有 skill 当成稳定发布物。** `misc` 不 promoted，`in-progress` 是 beta，可能变动或消失；deprecated 为空但保留 bucket 作为分类。[in-progress README](https://github.com/mattpocock/skills/blob/main/skills/in-progress/README.md#L1-L14)、[misc README](https://github.com/mattpocock/skills/blob/main/skills/misc/README.md#L1-L6)
- **两条安装路线不能混装。** managed plugin 是订阅式、只读 bundle；skills.sh 是项目内可编辑副本。混装会把每个 skill 安装两份；选择 skills.sh 后，更新还要重新 `add` 才能获取上游新增 skill。[install-block](https://github.com/mattpocock/skills/blob/main/.agents/install-block.md#L79-L108)
- **不是所有阶段都应该自动化。** user-invoked skill 刻意保留人工触发，因为它们会改变 tracker、branch、文档或工作分解；model-invoked skill 只应在任务真的匹配时触发。
- **当前链接跟随 `main`。** 如果团队需要可复现行为，应锁定已验证的 commit/版本并在升级时重新检查 manifest、安装器和 SKILL.md，而不是假设 README 永远不变。

### 与 Codex 的适配

#### 已有的原生适配

1. 仓库 README 已给出 Codex marketplace 安装命令，并说明默认启动时更新。[README Codex block](https://github.com/mattpocock/skills/blob/main/README.md#L37-L46)
2. 每个 skill 有 `agents/openai.yaml`，提供 Codex skill picker 的 `interface.display_name` / `short_description`；user-invoked skill 额外设置 `policy.allow_implicit_invocation: false`。[invocation 说明](https://github.com/mattpocock/skills/blob/main/.agents/invocation.md#L2-L7)
3. 仓库 ADR 记录：截至 2026-10-07，Codex 已支持 manifest 中的 `skills` 字符串数组，并在没有 `.codex-plugin/` 时回退读取 `.claude-plugin/`；当前 marketplace 安装会加载 promoted skills，不加载 `misc/` 或 `in-progress/`。[ADR 更新](https://github.com/mattpocock/skills/blob/main/.agents/adr/0002-ship-as-a-claude-code-plugin.md#L30-L38)
4. 这解释了为什么当前仓库可以用自己的 `.claude-plugin/marketplace.json` 服务 Codex，而不需要用户把整个 `skills/` 目录复制进项目。插件 manifest 的显式 skill 列表仍是发布边界。[plugin manifest](https://github.com/mattpocock/skills/blob/main/.claude-plugin/plugin.json#L20-L47)

#### Codex 使用建议

- 首选 README 中的两条 `codex plugin ...` 命令，安装后在 Codex 中显式输入 user-invoked skill 名称；不要期待模型自动触发 `setup-matt-pocock-skills`、`to-spec`、`to-tickets`、`implement` 等编排 skill。
- 先运行 `/setup-matt-pocock-skills`，因为 Codex 能加载 skill 不代表当前仓库已经配置 tracker、标签和 domain docs。
- `tdd`、`domain-modeling`、`codebase-design`、`diagnosing-bugs`、`code-review`、`pr`、`research` 可由模型按任务匹配，但仍要检查它们是否拥有可运行的测试/调试/评审工具和足够权限。
- 如果当前 Codex 版本不支持该 marketplace/manifest 路线，使用 README 的 `npx skills@latest add mattpocock/skills -a <agent>` 作为手动副本路线；注意这会牺牲自动更新，并且不要与插件路线同时安装。
- `implement-spec` 的并行实现依赖 Codex 的 subagent/worktree 能力。没有多 agent、worktree 或 tracker 时，改用 `to-tickets` 后逐张 `implement`，保留同一套 TDD 和 review 纪律。
- 不要把仓库维护者的 `scripts/link-skills.sh` 当普通 Codex 安装命令。它会在 `~/.agents/skills` 创建 symlink，源码明确称它为 dev-only、unsupported installer；它适合维护该仓库的本地开发环境，不适合作为项目使用者的默认安装方式。[link-skills.sh](https://github.com/mattpocock/skills/blob/main/scripts/link-skills.sh#L1-L20)

## 主要一手证据索引

- [顶层 README](https://github.com/mattpocock/skills/blob/main/README.md)
- [Engineering bucket README](https://github.com/mattpocock/skills/blob/main/skills/engineering/README.md)
- [Productivity bucket README](https://github.com/mattpocock/skills/blob/main/skills/productivity/README.md)
- [插件 manifest](https://github.com/mattpocock/skills/blob/main/.claude-plugin/plugin.json)
- [canonical 安装说明](https://github.com/mattpocock/skills/blob/main/.agents/install-block.md)
- [调用模型说明](https://github.com/mattpocock/skills/blob/main/.agents/invocation.md)
- [Codex / Claude plugin ADR](https://github.com/mattpocock/skills/blob/main/.agents/adr/0002-ship-as-a-claude-code-plugin.md)
- [仓库范围和取舍](https://github.com/mattpocock/skills/blob/main/SCOPE.md)
- [主流程路由 `ask-matt`](https://github.com/mattpocock/skills/blob/main/skills/engineering/ask-matt/SKILL.md)
- [setup](https://github.com/mattpocock/skills/blob/main/skills/engineering/setup-matt-pocock-skills/SKILL.md)、[grill-with-docs](https://github.com/mattpocock/skills/blob/main/skills/engineering/grill-with-docs/SKILL.md)、[to-spec](https://github.com/mattpocock/skills/blob/main/skills/engineering/to-spec/SKILL.md)、[to-tickets](https://github.com/mattpocock/skills/blob/main/skills/engineering/to-tickets/SKILL.md)
- [implement](https://github.com/mattpocock/skills/blob/main/skills/engineering/implement/SKILL.md)、[implement-spec](https://github.com/mattpocock/skills/blob/main/skills/engineering/implement-spec/SKILL.md)、[tdd](https://github.com/mattpocock/skills/blob/main/skills/engineering/tdd/SKILL.md)、[diagnosing-bugs](https://github.com/mattpocock/skills/blob/main/skills/engineering/diagnosing-bugs/SKILL.md)
- [domain-modeling](https://github.com/mattpocock/skills/blob/main/skills/engineering/domain-modeling/SKILL.md)、[codebase-design](https://github.com/mattpocock/skills/blob/main/skills/engineering/codebase-design/SKILL.md)、[code-review](https://github.com/mattpocock/skills/blob/main/skills/engineering/code-review/SKILL.md)、[pr](https://github.com/mattpocock/skills/blob/main/skills/engineering/pr/SKILL.md)、[retro](https://github.com/mattpocock/skills/blob/main/skills/engineering/retro/SKILL.md)
