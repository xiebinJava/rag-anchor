# Matt Pocock Skills 在 AI Coding 开发流程中的使用指南（第一版）

更新时间：2026-10-27

## 一、先说结论

`mattpocock/skills` 不是业务代码库，也不是需要加入项目依赖的 npm/Python 包，而是一套给编码 Agent 使用的工程流程规范。它通过 `SKILL.md` 告诉 Agent：面对不同类型的开发任务，应该先问什么、先读什么、如何拆分、如何测试、如何验证和如何复盘。

它解决的核心问题不是“让 Agent 写更多代码”，而是让 Agent 在 AI Coding 过程中更稳定地完成以下闭环：

```text
明确目标
  → 澄清需求和术语
  → 形成设计/规格
  → 拆成可交付切片
  → 测试驱动实现
  → 运行验证
  → 代码评审
  → 复盘并改进开发环境
```

建议团队不要每次把所有 skill 都调用一遍，而是根据任务规模和问题类型选择最小闭环。

## 二、AI Coding 中的人、Agent、Skill 如何分工

| 角色 | 主要职责 |
| --- | --- |
| 人 | 说明业务目标，做取舍和关键决策，确认验收标准，批准高风险操作 |
| Agent | 阅读代码和文档，提出问题，修改代码，运行测试，汇报证据 |
| Skill | 约束 Agent 的工作顺序、提问方式、测试方式和输出格式 |
| 项目系统 | 保存代码、Issue、规格、ADR、测试结果和审计记录，作为事实来源 |

Skill 不是业务规则本身，也不能替代测试、类型检查、CI、权限控制或人工验收。它更像是 Agent 的“工作方法”和“流程护栏”。

## 三、Skill 分类和使用时机总表

### 1. 每个项目建议优先掌握的 skill

| Skill | 什么时候使用 | 主要作用 | 典型产出 |
| --- | --- | --- | --- |
| `setup-matt-pocock-skills` | 一个仓库第一次使用这套工程流程时，只运行一次 | 配置 Issue tracker、标签、领域文档和 ADR 目录 | `docs/agents/`、`GLOSSARY.md`、ADR 约定 |
| `grill-with-docs` | 新需求、新功能、重要设计开始时 | 通过连续提问澄清目标、边界、术语和关键取舍 | 明确的问题定义、`GLOSSARY.md`、ADR |
| `implement` | 已经有明确任务、规格或 Ticket，需要开始写代码时 | 按任务实现，定期运行类型检查和测试，完成后做 review | 代码、测试、验证结果、提交 |
| `tdd` | 新功能、行为变更、Bug 修复，且存在可测试的行为边界时 | 采用 red → green → refactor，按垂直切片推进 | 先失败后通过的行为测试 |
| `code-review` | 完成一个功能、准备提交或创建 PR 前 | 从 Standards 和 Spec 两个维度检查变更 | 分轴的 Review 报告和问题清单 |

### 2. 按问题类型使用的 skill

| Skill | 触发条件 | 说明 |
| --- | --- | --- |
| `ask-matt` | 不确定当前任务该走哪条流程时 | 作为路由器，帮助选择后续 skill |
| `prototype` | 需求必须通过可运行的 UI、状态模型或业务逻辑才能判断时 | 做一次性原型，验证结论后再回到正式实现 |
| `to-spec` | 功能较大、会跨多个会话，或需要团队共识时 | 把讨论整理成正式规格 |
| `to-tickets` | 规格已经明确，需要多人或多阶段执行时 | 拆成带阻塞关系的垂直切片 Ticket |
| `diagnosing-bugs` | 间歇性 Bug、回归、性能问题或普通排查无法解决时 | 先建立能稳定复现该问题的反馈回路，再定位和修复 |
| `codebase-design` | 需要设计模块接口、测试 seam、适配器或重构边界时 | 使用 deep module、interface、seam、adapter 等统一设计词汇 |
| `domain-modeling` | 业务术语含糊、同一个词有多种含义、需要沉淀领域模型时 | 维护业务语言和重要领域决策 |
| `research` | 需要外部资料、技术事实或一手文档时 | 读取高可信来源并留下有引用的研究 Markdown |
| `pr` | 需要创建或整理 Pull Request 说明时 | 生成 Summary、Before/After Evidence 和 Merge Danger |
| `retro` | 一次开发结束后，尤其是过程走偏或重复踩坑后 | 改进 Agent 环境、检查项、文档和工具，而不是直接改业务代码 |

### 3. 规模较大时才使用的 skill

| Skill | 适用范围 | 不建议什么时候使用 |
| --- | --- | --- |
| `wayfinder` | 巨大、模糊、无法在一个会话中看清路径的项目或特性 | 已经能明确拆分的小功能 |
| `implement-spec` | 已有完整规格和 Ticket 图，需要在集成分支上并行推进 | 单人小项目、单个 Ticket 或没有可靠测试的项目 |
| `triage` | 外部进入、尚未整理成 Agent-ready 的 Bug/需求 | `to-tickets` 已经生成的可执行 Ticket |
| `improve-codebase-architecture` | 定期巡检模块深度、接口和代码健康 | 还没有稳定功能边界、正在快速探索的早期项目 |

## 四、推荐的 AI Coding 主流程

### 阶段 0：项目初始化和一次性配置

第一次在仓库中使用工程类 skill 时，显式调用：

```text
/setup-matt-pocock-skills
```

它会先检查仓库远端、已有的 `AGENTS.md` / `CLAUDE.md`、Issue tracker、`GLOSSARY.md` 和 ADR 目录，然后询问应该采用哪种配置。

个人项目或没有远端 Issue 系统时，可以选择本地 Markdown tracker；团队项目如果已经使用 GitHub/GitLab/Jira，则应记录真实的协作入口。配置完成后要检查它写入的文件，不要把默认配置直接当成团队规范。

### 阶段 1：需求澄清和共同语言

适用场景：用户只描述了一个想法，或者需求中存在“账户、项目、完成、发布、同步”等含义不明确的词。

调用：

```text
/grill-with-docs
```

这个阶段的目标不是马上写代码，而是确认：

- 用户真正想解决的问题是什么；
- 哪些内容属于范围内，哪些明确不做；
- 核心业务对象和术语是什么；
- 哪些决定难以逆转，是否需要写 ADR；
- 后续应该在哪个 public interface 或 seam 上验证行为。

如果关键问题必须通过运行 UI 或状态模型才能回答，先走 `prototype`，不要在正式代码中边猜边实现。

### 阶段 2：规格和任务拆分

小功能可以在澄清后直接实现。中大型功能建议走：

```text
/to-spec
  → /to-tickets
  → 按阻塞关系逐个 /implement
```

`to-spec` 负责形成团队可讨论、可追踪的规格；`to-tickets` 负责把规格拆成可独立验证的 tracer-bullet 垂直切片。一个好的 Ticket 应尽量贯穿数据、接口、业务逻辑、界面和测试，而不是把工作简单切成“先写完后端，再写前端”。

如果项目大到一开始无法判断路径，再使用 `wayfinder` 先解决关键决策；路径清楚后仍然需要回到 `to-spec` 和 `to-tickets`，不要直接从决策地图跳到写代码。

### 阶段 3：设计模块和测试 seam

在写测试或代码前，先确认要测试的 seam：

- 调用者真正使用的 public interface 是什么；
- 哪些行为应该被观察；
- 哪些实现细节不应该暴露给测试；
- 依赖是由模块接收，还是由模块自己创建；
- 模块能否用较小的 interface 隐藏更多实现复杂度。

需要讨论模块形状时使用 `codebase-design`；需要统一业务词汇时使用 `domain-modeling`。二者更像设计参考和语言层，通常由 `grill-with-docs`、`tdd` 或架构巡检流程带入。

### 阶段 4：实现和 TDD

调用：

```text
/implement
```

实现过程中让 Agent 按垂直切片循环：

```text
写一个描述用户行为的失败测试
  → 写刚好让测试通过的最小实现
  → 运行类型检查和相关测试
  → 再进入下一个切片
```

`tdd` 的重点是测试 public behavior，而不是 private method、内部 mock 结构或实现细节。测试 seam 应在开始写测试前与用户达成一致。

`implement` 的默认纪律包括：定期跑类型检查、定期跑单文件测试、结束时跑完整测试套件，并在完成后进入 `code-review`。团队需要提前确认项目有可用的测试、lint、类型检查或其他反馈回路，否则 Agent 很容易在没有证据的情况下“看起来完成”。

### 阶段 5：困难 Bug 和性能回归

普通 Bug 可以直接定位并修复；以下情况使用 `diagnosing-bugs`：

- 偶发、难以稳定复现；
- 只在特定数据、时间或并发条件下发生；
- 升级或重构后出现回归；
- 性能下降但原因不明确；
- 第一次修复后仍然反复出现。

它要求先构造一个针对“这个具体问题”的 tight feedback loop，例如失败测试、HTTP 重放脚本、CLI fixture、浏览器断言或最小复现程序，再进行假设、instrument、修复和回归验证。

### 阶段 6：完成前 Review 和 PR

完成实现后调用：

```text
/code-review
```

Review 必须指定 fixed point，例如 `main`、某个 commit 或 `HEAD~5`。它分为两个互不混淆的维度：

| Review 维度 | 关注点 |
| --- | --- |
| Standards | 是否符合仓库约定、编码标准和可维护性原则 |
| Spec | 是否真的实现了需求，是否漏实现或发生 scope creep |

如果要创建 PR，再使用 `pr` 生成简洁的变更说明、Before/After 证据和合并风险。

### 阶段 7：复盘和环境改进

一次功能结束后，可以调用：

```text
/retro
```

复盘重点不是重新评价业务代码，而是找出下一次可以提前固化的改进：导航文档、自动化检查、测试命令、编码标准、Agent 能访问的资料、重复的人工操作等。

## 五、团队建议采用的最小默认流程

对于普通功能开发，推荐默认使用以下流程：

```text
首次使用仓库：/setup-matt-pocock-skills

每个非 trivial 功能：/grill-with-docs

中大型功能：/to-spec → /to-tickets

开始写代码：/implement

实现中的纪律：tdd

完成前：code-review

创建 PR：pr

一次工作结束：retro
```

更简化地说：

| 任务类型 | 推荐路径 |
| --- | --- |
| 小功能、单会话完成 | `grill-with-docs` → `implement` → `code-review` |
| 中大型功能、多会话协作 | `grill-with-docs` → `to-spec` → `to-tickets` → `implement` → `code-review` |
| UI 或状态不确定 | `grill-with-docs` → `prototype` → `to-spec` / `implement` |
| 复杂 Bug | `diagnosing-bugs` → 回归测试 → 修复 → `code-review` |
| 需要外部技术资料 | `research` → `grill-with-docs` → `to-spec` / `implement` |
| 巨大且模糊的项目 | `wayfinder` → `to-spec` → `to-tickets` → `implement-spec` |

## 六、User-invoked 和 Model-invoked 的区别

这套 skill 大致分两类：

### User-invoked：需要人主动启动

典型包括：

- `setup-matt-pocock-skills`
- `grill-with-docs`
- `to-spec`
- `to-tickets`
- `implement`
- `implement-spec`
- `wayfinder`
- `triage`
- `retro`

它们可能创建文档、改变 Issue 状态、拆分任务、创建分支或提交代码，因此保留人工触发是合理的。

### Model-invoked：任务匹配时可自动采用

典型包括：

- `tdd`
- `domain-modeling`
- `codebase-design`
- `diagnosing-bugs`
- `code-review`
- `pr`
- `research`

模型可以根据用户描述自动采用这些纪律，但团队仍然应该检查 Agent 是否真的执行了测试、验证和回读，而不是只相信它的文字总结。

## 七、在 Codex 中的实际使用方式

如果这些 skill 已经安装在用户级 skill 目录中，就不需要重复安装或把它们复制到每个业务项目中。

在 Codex 中，可以直接用自然语言明确要求使用某个流程，例如：

```text
使用 /grill-with-docs，先不要改代码，帮我把这个需求的边界、术语和验收标准问清楚。
```

```text
按照当前 Ticket 使用 /implement；每个 public seam 先用 tdd 写失败测试，完成后运行完整测试并做 code-review。
```

```text
请使用 diagnosing-bugs 处理这个偶发问题，先建立稳定的复现回路，不要直接猜原因。
```

全局安装只代表 Agent 能找到这些 skill，不代表当前仓库已经配置了 Issue tracker、测试命令、文档目录或团队规范。项目级配置仍然需要通过 `setup-matt-pocock-skills` 完成。

## 八、使用时需要注意的风险和边界

1. 不要把 skill 当成质量保证系统。最终质量仍然依赖测试、类型检查、CI、权限校验和人工验收。
2. `setup-matt-pocock-skills` 可能写入仓库配置和文档，第一次运行后要审阅 diff。
3. `implement` 可能根据 skill 约定提交当前分支；如果团队不希望 Agent 自动提交，要在任务开始时明确说明。
4. `code-review` 需要固定比较基线；没有 fixed point 时，Review 结果不完整。
5. `triage` 只适合处理外部进入、尚未整理的 Issue，不要把已经拆好的 Ticket 再重复 triage。
6. `implement-spec` 依赖稳定的 Ticket 图、测试、分支/worktree 和多 Agent 能力；条件不足时用逐 Ticket 的 `implement` 更稳妥。
7. Skill 本身也是 Agent 指令，安装和升级时应检查其内容，尤其是涉及外部系统写入、提交、权限和凭据的流程。

## 九、建议的团队落地顺序

第一阶段先统一最小闭环：

```text
grill-with-docs → implement → tdd → code-review
```

第二阶段再补充：

```text
setup-matt-pocock-skills → to-spec → to-tickets → pr → retro
```

第三阶段根据项目规模引入：

```text
prototype、diagnosing-bugs、research、wayfinder、implement-spec、improve-codebase-architecture
```

落地时最重要的不是安装最多 skill，而是把每个 skill 和一个明确的开发阶段、输入、输出及验收门禁绑定起来。

## 十、资料来源

- [mattpocock/skills README](https://github.com/mattpocock/skills)
- [Engineering skills README](https://github.com/mattpocock/skills/blob/main/skills/engineering/README.md)
- [ask-matt 主流程](https://github.com/mattpocock/skills/blob/main/skills/engineering/ask-matt/SKILL.md)
- [implement](https://github.com/mattpocock/skills/blob/main/skills/engineering/implement/SKILL.md)
- [tdd](https://github.com/mattpocock/skills/blob/main/skills/engineering/tdd/SKILL.md)
- [code-review](https://github.com/mattpocock/skills/blob/main/skills/engineering/code-review/SKILL.md)
- [OpenAI Skills 官方说明](https://developers.openai.com/plugins/concepts/skills)
