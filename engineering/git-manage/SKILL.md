---
name: git-manage
description: "管理 Git-Flow 分支初始化、中文原子提交、合并、release/hotfix 双向回流、Submodule 与语义化版本 x.y.z。适用于 git-manage、git-commit、git-merge、git-init、提交代码、新建分支、合并到 develop/main、预发布、发版、热修复、版本号升级、变更分类、发布说明和版本号判断；大版本仅在用户明确确认破坏性变更或重大架构调整时升级。"
version: 2.1.0
platforms: [linux, macos, windows]
metadata:
  short-description: "Manage complete Git-Flow lifecycle (master, develop, feature, release, hotfix), branch context detection, repo init, Chinese conventional atomic commits, pre-commit checks, and submodule sync"
  tags: [git, commit, conventional-commits, git-flow, release-branches, hotfixes, merge, rebase, branch-management, git-manage, atomic-commits, git-init, branch-init, plan-a-rule, monorepo]
---

# Git Workflow & Lifecycle Management Assistant (经典 Git-Flow 完整中文落地版)

本技能严格参照 Vincent Driessen 提出的经典 **Git-Flow 架构模型**，结合团队工程标准与中文约定式提交规范落地，旨在构建**结构清晰、权责分明、安全可控、双向回流、历史纯净**的企业级版本演进体系。

```text
feature         develop         release         hotfix          master / main
branches        (开发主线)      branches        (紧急热修)      (生产发布)
   │               │               │               │               │
   │               ○───────────────────────────────────────────────● Tag 0.1
   │              ╱│               │              ╱                │
   │   Major feat  │               │    Severe bug                 │
   │   for release │               │    in prod:                   │
   │       ┌───────○               │    hotfix 0.2                 │
   │       │      ╱│               │       ┌───────────────────────●
   ○       │     ╱ │   Incorporate │       │                       │
   │       ○    ╱  │   bugfix into │       ○                       │
   ○       │   ╱   │   develop     │       │                       │
   │       ○───    │ ◀─────────────┼───────○───────────────────────● Tag 0.2
   │       │       │               │                               │
   │       │       ○ Start release │                               │
   │       │       │ branch for 1.0│                               │
   │       │       │──────┐        │                               │
   │       │       │      ○ Only   │                               │
   │       │       │      │ bugfixes                               │
   │       │       │      ○        │                               │
   │       │       │ ◀────┴────────┤ (Continuous bugfix backport)  │
   │       │       │      ○        │                               │
   │       │       │ ◀────┼────────┴───────────────────────────────● Tag 1.0
   │       │       ○      │                                        │
   │       └───▶───○──────┘                                        │
   │               │                                               │
   ▼               ▼                                               ▼ (Time)
```

---

## 0. 核心法则：每次启用优先执行“分支上下文感知与操作决策”

涉及 Git 提交、分支、合并或发布操作时，先执行以下分支上下文检查；仅判断版本号时，直接按第 4.1 节检查版本来源与变更范围，不创建分支、提交或标签。

### 步骤 1：判断当前所在分支与仓库拓扑 (Branch Detection)
立即执行指令获取当前 Git 上下文：
```bash
git rev-parse --abbrev-ref HEAD   # 获取当前所在分支
git branch -a                     # 检查本地与远程分支结构
git status -s                     # 查看当前工作区状态
```

### 步骤 2：识别当前分支角色与执行意图矩阵 (Action Matrix)
根据当前所处分支角色，核对用户要求进行的操作，严格匹配图中逻辑并给出指引/执行：

| 当前所在分支 | 允许操作 / 图中生命周期节点 | 行为指引与约束 |
| :--- | :--- | :--- |
| **`master` / `main`** | • 检出 `hotfix/*` 分支<br>• 查看生产版本 Tag<br>• 项目初始化检出 `develop` | **生产基线禁区**。严禁在此写业务代码；严禁直接合并 `develop`；生产缺陷直接基于此检出 `hotfix/<version>`。 |
| **`develop` / `dev`** | • 派生 `feat/*` 特性分支<br>• 派生 `release/*` 发版分支<br>• 合并接收 `feat/*`、`release/*`、`hotfix/*` | **开发主干集线器**。新需求从这里派生；接收特性合入与双向回流；**严禁直接 push/merge 到 `master`/`main`**。 |
| **`feat/*` 或 `feature/*`** | • 方案 A 原子提交代码<br>• 保持与 `develop` 同步 (rebase)<br>• 完成后合入 `develop` 并删除自身 | **特性开发区**。仅针对特定需求开发；不可派生 release 或 hotfix。 |
| **`release/*`** | • 修复发布前验收 Bug (Only bugfixes)<br>• 同步回流 Bug 修复到 `develop`<br>• 完成后**双向合入** `master` (打 Tag) + `develop` | **预发布收敛区**。功能已冻结！严禁新增 feature，仅修 Bug 并持续回流至 develop。 |
| **`hotfix/*`** | • 紧急修复线上生产缺陷<br>• 升级补丁版本号<br>• 完成后**双向合入** `master` (打 Tag) + `develop` | **生产救火通道**。直接基于 master 检出；修复完毕后必须同时合入 master 与 develop，避免 Bug 在后续版本复发。 |

> **分支越位拦截与重定向**：
> - 遇到“合并到 main/发版/同步到 master”等指令，**严禁直接执行 `git merge develop`**：发版强制走 `Workflow D/E`（release 双合），线上救火走 `Workflow F`（hotfix 双合）。
> - 在 `master` 上开发新特性或在 `release/*` 上写新功能时，主动制止并引导至对应正确分支。
---

## 1. 仓库环境智能初始化与分支补全 (Init & Bootstrap Ability)
*Trigger: `git-init`, `git init`, `初始化`, `初始化分支`, `补全分支`, `检查分支环境`*

当仓库刚创建、克隆自空仓库、或缺少 Git-Flow 关键基线分支时，本技能提供一键初始化与自动补齐能力：

### 1.1 初始化流程与分支补全标准
1. **核实主干分支存在性**：
   - 检查生产主分支（`master` 或 `main`）；
   - 若本地或远程不存在 `master`/`main`，且仓库为空，先创建初始提交并确立主分支：
     ```bash
     git checkout -b main
     # 或 master
     ```
2. **检测并补齐开发主线 (`develop`)**：
   - 如果仓库仅有 `main`/`master`，而缺少 `develop` 分支：
     ```bash
     # 基于 master 检出并创建 develop 分支
     git checkout -b develop master
     # 若有 remote 则推送到远程建立跟踪
     git push -u origin develop 2>/dev/null || true
     ```
3. **识别并配置分支命名约定**：
   - 生产分支：`master`（或 `main`）
   - 开发主线：`develop`
   - 特性分支前缀：`feat/`（或 `feature/`）
   - 预发布分支前缀：`release/`
   - 热修复分支前缀：`hotfix/`
   - 版本 Tag 前缀：`v`（如 `v0.1.0`、`v1.0.0`）

---

## 2. 方案 A 黄金法则：原子化提交优先 (The Plan A Rule: Atomic Over Monolithic)

在日常与分支合并提交流程中，面对累积的改动，始终贯彻**方案 A（原子化分解提交）**准则：

> **抉择铁律**：当面临“方案 A（按关注点拆解为多个高内聚原子提交）”与“方案 B（整包合并为一个大杂烩 Commit）”的抉择时，**永远无条件坚定选择方案 A**！严禁任何形式的方案 B 笼统提交。

### 原子提交三大支柱
1. **单一职责 (Single Responsibility)**：
   - 一个 Commit 只聚焦一个关注点（Separation of Concerns）。
   - 严禁将“后端契约/模型/数据迁移”与“前端交互/视图样式”、“核心业务逻辑”与“无关代码重构/格式化”混在一个提交中。
2. **独立可验证性 (Bisect-Friendly / Always Green)**：
   - 拆分出的每一个原子提交都必须自洽闭环。
   - 任意原子提交单独检出（`git checkout <hash>`）时，必须能够通过项目构建与自动化测试，绝不允许产生破坏构建的中间态破损提交。
3. **精准可溯与安全回滚 (Revertible & Reviewable)**：
   - 细粒度、高内聚的提交使 Code Review、Cherry-pick 与线上单项故障定向 `git revert` 成本降至最低。

---

## 3. Commit Message Specification (中文约定式提交)

严格遵循工程规范，所有提交信息**必须使用中文**描述，格式为：
```text
<type>(<optional scope>): <中文动词引导的描述>

[可选 详细描述 Body]
[可选 关联 Issue Footer]
```

### Commit Types 标准对照表

| Type | 语义 | 动词前缀规范 (中文) | 示例 |
| :--- | :--- | :--- | :--- |
| **`feat`** | 新功能 / Feature | `feat: 新增...` / `feat(scope): 新增...` | `feat(auth): 新增企业微信扫码登录支持` |
| **`fix`** | 修复缺陷 / Bug fix | `fix: 修复...` / `fix(scope): 修复...` | `fix(user): 修复分页列表总数计算错误` |
| **`docs`** | 文档变更 / Documentation | `docs: 更新...` / `docs: 补充...` | `docs: 更新 AGENTS.md 与部署指南` |
| **`style`** | 代码格式（不影响逻辑） | `style: 格式化...` | `style: 格式化 Python 与前端代码` |
| **`refactor`** | 代码重构（非 feat 非 fix） | `refactor: 重构...` / `refactor(scope): 重构...` | `refactor(db): 重构通用 CRUD 抽象基类` |
| **`perf`** | 性能提升 / Performance | `perf: 优化...` / `perf(scope): 优化...` | `perf(query): 优化用户列表联表查询索引` |
| **`test`** | 测试用例 / Testing | `test: 增加...测试` / `test: 完善...` | `test(auth): 增加登录鉴权单元测试` |
| **`build`** | 构建系统 / 工具链 / 依赖 | `build: 构建/工具链调整...` | `build(web): 迁移前端工具链至 Vite+ 并接入 Oxlint` |
| **`ci`** | 持续集成配置 / CI/CD | `ci: 添加...流水线` | `ci: 添加 GitHub Actions 自动化测试流水线` |
| **`chore`** | 杂项维护 / 配置更新 | `chore: 更新...` | `chore: 更新 .gitignore 忽略临时缓存文件` |
| **`revert`** | 回滚历史提交 | `revert: 回滚提交 <commit-hash>` | `revert: 回滚提交 4de74d7` |

---

## 4. 提交前自动质量门禁 (Pre-commit Quality Checks)

在执行 `git commit` 或分支合并前，必须确保通过对应工程的静态检查与测试校验：

1. **后端校验 (Python / FastAPI / Go / etc.)**：
   - 行宽约束与语法检查（如 `ruff check`、`pytest` 等）；
   - 涉及模型变更时，确保数据库迁移脚本完备有效。
2. **前端校验 (Vue / React / Vite+ / Node)**：
   - 执行静态检查与打包构建自检（如 `pnpm lint` / `vp check` / `pnpm build`）。
3. **干净交付铁律**：
   - 严禁提交 `print`、`console.log`、调试断点残留及未使用的引用导入。

### 4.1 语义化版本与发布说明

按三个非负整数 `x.y.z` 管理版本；发布标签使用 `v<version>`。

- `x`：仅当用户明确确认或要求发布破坏性变更、重大架构调整、不兼容 API/数据协议时递增，重置 `y.z` 为 `0.0`；否则保持不变，说明不兼容风险并请求确认或采用兼容方案。
- `y`：新增向后兼容的功能、接口、配置或用户可见能力，使用 `x.(y+1).0`。
- `z`：修复现有缺陷、兼容性、安全、文档或构建问题且没有新增功能，使用 `x.y.(z+1)`。

执行顺序：

1. 读取项目实际版本源与 Git 标签，检查 `package.json`、`pyproject.toml`、`go.mod`、构建配置和发布脚本中适用的来源。
2. 根据当前工作区 diff、近期提交或变更说明分类，采用最高级别变更；同批功能与修复只升级 `y`。不能确定时选择较小的兼容版本并说明依据，不自行升级 `x`。
3. 修改前列出当前版本、分类依据、目标版本和受影响文件。只要求判断时，给出建议与理由，不修改文件。
4. 只修改实际使用的版本源；仅在项目流程要求时同步生成文件和锁文件，检查版本引用、构建配置、发布说明及标签一致性。
5. 完成时报告旧版本、目标版本、分类依据、修改文件和验证结果。

示例：`1.4.2` 修复登录超时 → `1.4.3`；新增可选导出接口 → `1.5.0`；删除旧接口且用户确认大版本升级 → `2.0.0`。

---

## 5. 标准工作流与执行指令 (Standard Workflows & Commands)

### Workflow 0: 仓库初始化与分支补全 (Init & Branch Bootstrap)
*Trigger: `git-init`, `初始化`, `补全分支`, `init`*

用于快速建立符合 Git-Flow 标准的分支骨架：
```bash
# 1. 检查主分支 (master 或 main)
MAIN_BRANCH=$(git branch --list master main | head -n1 | tr -d ' *')
if [ -z "$MAIN_BRANCH" ]; then
  MAIN_BRANCH="master"
  git checkout -b "$MAIN_BRANCH"
fi

# 2. 检查并建立 develop 分支
if ! git show-ref --verify --quiet refs/heads/develop; then
  git checkout -b develop "$MAIN_BRANCH"
  echo "已基于 $MAIN_BRANCH 建立并切换至 develop 分支"
fi
```

---

### Workflow A: 极简智能提交与方案 A 原子拆解 (Smart Atomic Commit)
*Trigger: `/git-manage`, `/git-commit`, `提交代码`, `提交`, `写commit`, `commit`*

1. **状态与全景分析（前置感知当前分支）**：
   - 执行 `git rev-parse --abbrev-ref HEAD` 确认当前分支；
   - 执行 `git status -s`、`git diff`；
   - 识别变动范围是否跨越多个架构层级（文档、数据库、API、前端组件）；
2. **执行方案 A 拆解**：
   - 规划拓扑顺序：契约/文档 ➔ 数据库模型/迁移 ➔ 后端服务 ➔ 前端界面；
   - 精准暂存（`git add <files>`），逐一形成高内聚的中文约定式提交；
3. **门禁自检与结果汇报**。

---

### Workflow B: 新建特性分支 (Start Feature Branch)
*Trigger: `新增功能`, `新建功能`, `开发...`, `新建分支`, `基于develop开分支`*

按照图中逻辑，**所有 Feature 分支必须统一从最新的 `develop` 主线派生**：
```bash
git checkout develop
git pull origin develop 2>/dev/null || true
git checkout -b feat/<feature-name>
```

---

### Workflow C: 完成特性并汇入 `develop` (Finish Feature Branch)
*Trigger: `合并到dev`, `合并到develop`, `完成功能`, `特性完成`*

有两种被广泛采用的标准模式（根据项目规范选用）：
- **模式 1：保持 develop 纯线性（推荐，优先选用）**：
  先在特性分支上变基对齐 `develop`，然后快进合并并清理分支：
  ```bash
  git checkout feat/<feature-name>
  git rebase develop
  git checkout develop
  git merge feat/<feature-name> --ff-only
  git branch -d feat/<feature-name>
  ```
- **模式 2：经典保留特性整体气泡（Git-Flow 经典 --no-ff）**：
  ```bash
  git checkout develop
  git merge feat/<feature-name> --no-ff -m "feat(merge): 合并特性分支 feat/<feature-name>"
  git branch -d feat/<feature-name>
  ```

---

### Workflow D: 开启预发布分支并进行收敛测试 (Start Release Branch)
*Trigger: `预发布`, `准备发版`, `开启release`, `release分支`, `创建release`*

当下一版本的功能在 `develop` 均已就绪且达到功能冻结（Feature Freeze）时，从 `develop` 拉出 `release` 分支：

先按第 4.1 节确定 `<version>` 与受影响版本源，再创建分支和更新发布说明；分支名和示例不构成大版本升级授权。
```bash
# 1. 从 develop 检出 release 分支
git checkout develop
git pull origin develop 2>/dev/null || true
git checkout -b release/<version>   # 例如: release/1.0.0

# 2. 修改版本元数据（如 package.json、__version__.py 等）
git commit -am "chore(release): 升级版本号至 <version>"
```
> **预发布分支铁律（严格对照图中规则）**：
> - **严禁在此分支上开发任何新 Feature (Only bugfixes!)**！从此时起，"next release" 指向 1.0 之后的版本，新功能继续进 `develop`。
> - **只允许修 Bug、补充测试用例和更新文档**。
> - **持续回流机制 (Continuous Backport)**：在 release 分支上产出的 Bug 修复，可根据需要随时或在发版时合并回 `develop`（`Bugfixes from rel. branch may be continuously merged back into develop`）。

---

### Workflow E: 完成预发布并双向合并 (Finish Release Branch · 双向回流)
*Trigger: `完成发版`, `发版`, `release完成`, `合并release`, `大版本发布`*

这是经典 Git-Flow 架构的**核心关键点**（图中 Release 结束节点）：必须完成向生产（`master`）和开发（`develop`）的**双向回流**，绝不能只推生产！

```bash
# 步骤 1: 确保预发布分支代码最新且测试通过
git checkout release/<version>

# 步骤 2: 合入生产主线 (master / main)，必须带 --no-ff 生成版本发布节点
git checkout master
git merge release/<version> --no-ff -m "feat(release): 发布 <version> 版本"

# 步骤 3: 生产打上版本 Tag (例如 Tag 1.0)
git tag -a "v<version>" -m "版本发布: v<version>"

# 步骤 4: 核心关键——双向回流！将发版分支上的所有修复与版本号变动回合至 develop
git checkout develop
git merge release/<version> --no-ff -m "chore(release): 将 release/<version> 的修复与配置同步回 develop"

# 步骤 5: 删除已完成生命周期的 release 分支
git branch -d release/<version>

# 步骤 6: 推送代码与标签至远端 (若有 remote)
git push origin master --tags 2>/dev/null || true
git push origin develop 2>/dev/null || true
```

---

### Workflow F: 生产紧急热修复 (Hotfix Branch · 救火双合)
*Trigger: `hotfix`, `热修复`, `紧急修复`, `线上bug`, `生产报错`*

线上生产环境发现严重故障（Severe bug fixed for production），无法等待常规版本迭代发布时，启动 **Hotfix 救火通道**：

按第 4.1 节从生产版本计算补丁版本，更新实际版本源与发布说明后再打标签。

```text
master ──────────●────────────────────────● Tag 0.2 / Tag 1.0.1 (合入生产打 Tag)
                  \                      /
hotfix/0.2         ●───● (修 Bug)       /
                                        \
develop ─────────────────────────────────● Incorporate bugfix in develop (必须双向回合！)
```

**执行标准步骤**：
```bash
# 步骤 1: 直接基于 master (生产线故障现场) 创建热修复分支
git checkout master
git checkout -b hotfix/<version>   # 例如: hotfix/0.2 或 hotfix/1.0.1

# 步骤 2: 定位并修复线上 Bug，执行原子提交
git commit -m "fix(prod): 修复生产环境..."

# 步骤 3: 升级修订补丁版本号
git commit -am "chore(version): 更新补丁版本号至 <version>"

# 步骤 4: 合入生产主线 master 并打 Tag
git checkout master
git merge hotfix/<version> --no-ff -m "fix(release): 紧急热修复发布 <version>"
git tag -a "v<version>" -m "紧急热修复发布: v<version>"

# 步骤 5: 致命重点——双向回合 develop (Incorporate bugfix in develop)！
# 如果当前恰好存在活跃的 release 分支，应将 hotfix 合入 release 分支；
# 否则，直接合入 develop，保证未来的迭代版本永远不会漏修此 Bug！
git checkout develop
git merge hotfix/<version> --no-ff -m "chore(hotfix): 将 hotfix/<version> 紧急修复同步回 develop"

# 步骤 6: 清理分支并推送
git branch -d hotfix/<version>
git push origin master --tags 2>/dev/null || true
git push origin develop 2>/dev/null || true
```

---

### Workflow G: 聚合大仓与子模块联动管理 (Monorepo & Submodule Management)
*Trigger: `submodule`, `更新子模块`, `更新指针`, `大仓提交`, `同步大仓`*

当处于包含子模块（Submodule）的聚合大仓环境时，支持自动化子模块状态同步与指针记录：

1. **全景状态巡检**：
   - 自动遍历所有已配置的子模块，检查工作区是否有未提交改动：
     ```bash
     git submodule foreach --recursive 'git status -s'
     ```
2. **更新大仓引用的子模块指针**：
   - 当某个业务子项目（如 `services/face-service` 或 `apps/face-web`）在本地有新提交时，大仓会感知到目录指针位移。
   - 自动生成符合规范的中文约定式提交：
     ```bash
     git add <submodule-path>
     git commit -m "chore(submodule): 同步 <submodule-name> 引用指针"
     ```
3. **双轨推送安全校验**：
   - 提醒或自动校验：确保子项目自身的 Commit 已经先行推送到独立远程仓库，再行推送聚合大仓指针，避免团队成员或换机拉取时指针悬空。

---

## 6. 常见冲突与防错守则 (Safety Rules & Anti-Patterns)

1. **绝对禁止 `develop` 直接合入 `master` / `main`**：生产分支变动必须且只能来自 `release/*`（发版）或 `hotfix/*`（救火），必须附带 SemVer Tag。
2. **严禁生产“漏修” (Never Skip Develop on Hotfix/Release)**：
   - 任何在 `hotfix/*` 或 `release/*` 上的修复，**必须双向同步回合至 `develop`**。绝不允许只合入 `master`，否则下一次发版将导致线上 Bug 离奇复发。
3. **严禁在 Release 分支开发新功能 (Feature Freeze)**：
   - `release/*` 分支一旦开辟，严格执行 Feature Freeze。只能提交 Bug 修复和文档变更。如果有新功能突发需求，必须提交至 `develop` 参与下一代发布。
4. **保护长线分支纯洁性 (Protected Branches)**：
   - `master` 与 `develop` 为永久受保护分支，除特定合并操作外，严禁在此两分支上直接进行日常未测试的脏修改。
5. **版本 Tag 规范化**：
   - 生产发布的每一次 `--no-ff` 合并节点，必须配套规范的语义化版本号标签（SemVer：`v主版本.次版本.修订号`，如 `v1.0.0`、`v1.0.1`），严禁无 Tag 裸合入生产。
6. **大仓子模块双轨顺序铁律**：
   - 聚合大仓更新子模块时，必须先在子仓内完成 Commit 并 Push 到对应远端，再在大仓中提交指针变动（`chore(submodule): 同步 <name> 引用指针`），严禁提交悬空指针。
