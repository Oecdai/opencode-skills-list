# Releasing / 发布规范

中文 | [English](#english)

## 中文

### 目标

本仓库采用固定的中英双语发布规范。以后只要有已经推送到 GitHub 的更新，就应创建对应的 GitHub Release，用来清楚记录本次推进、修正和调整内容。

### 何时发布

满足以下条件时应发布新 Release：

- 有新的 commit 已推送到默认分支
- 用户可感知的功能、命令、输出、安装方式或文档发生变化
- 修复了影响可用性、稳定性、路径、兼容性的问题

以下情况也建议发布：

- 只更新了 README、安装说明、About 简介，但会影响用户理解或使用方式
- 调整了命令入口、配置路径、全局/项目级加载逻辑

### 版本号规则

- `v0.x.0`：有一组明确的新功能或明显的行为变化
- `v0.0.x`：小修复、路径修正、文档修订、轻量调整
- `v1.0.0`：接口、命令、安装方式和输出结构已经稳定，适合长期使用

在当前阶段，优先使用保守版本策略：

- 明显增强：升次版本，例如 `v0.2.0`
- 小修复：升补丁版本，例如 `v0.2.1`

### Release 必须包含的内容

每个 Release 都必须包含以下章节，并保持中英双语：

1. `## 中文`
2. `### 本次更新`
3. `### 调整 / 修复`
4. `### 影响说明`
5. `## English`
6. `### Highlights`
7. `### Fixes / Adjustments`
8. `### Impact`

### 编写要求

- 先写中文，再写英文
- 中文和英文的内容要语义对应，不要一边详细一边简略
- 说明“做了什么”时，也要说明“为什么改”和“会影响什么”
- 如果有路径、命令、版本号，两个语言版本都要保留

### 推荐流程

1. 整理本次已推送的 commit
2. 确定版本号
3. 按模板写中英双语 Release Notes
4. 创建 git tag
5. 在 GitHub 创建 Release

### 最小 Release 模板

```markdown
## 中文

### 本次更新
- 

### 调整 / 修复
- 

### 影响说明
- 

## English

### Highlights
- 

### Fixes / Adjustments
- 

### Impact
- 
```

## English

### Goal

This repository follows a fixed bilingual release policy. Whenever new updates have been pushed to GitHub, a matching GitHub Release should be created to clearly document what was added, fixed, adjusted, and how the project moved forward.

### When to Publish

Create a new Release when:

- new commits have been pushed to the default branch
- user-visible behavior changes in features, commands, output, installation, or docs
- usability, stability, path, or compatibility issues were fixed

Also recommended when:

- README, installation instructions, or About text changed in ways that affect usage
- command entrypoints, config paths, or global/project loading behavior changed

### Versioning Rules

- `v0.x.0`: clear feature growth or meaningful behavior change
- `v0.0.x`: small fixes, path corrections, docs updates, lightweight adjustments
- `v1.0.0`: commands, installation, and output structure are considered stable

For the current stage, prefer a conservative versioning strategy:

- meaningful enhancement: bump minor, for example `v0.2.0`
- small fix: bump patch, for example `v0.2.1`

### Required Release Sections

Every Release must include these bilingual sections:

1. `## 中文`
2. `### 本次更新`
3. `### 调整 / 修复`
4. `### 影响说明`
5. `## English`
6. `### Highlights`
7. `### Fixes / Adjustments`
8. `### Impact`

### Writing Rules

- Write Chinese first, then English
- Keep both language sections semantically aligned
- Explain not only what changed, but also why and what users should expect
- Preserve paths, commands, and version numbers in both sections when relevant

### Recommended Flow

1. Review the commits that have already been pushed
2. Choose the new version number
3. Write bilingual Release Notes from the template
4. Create the git tag
5. Create the GitHub Release
