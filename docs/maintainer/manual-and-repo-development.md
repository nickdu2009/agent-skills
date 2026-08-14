# Manual And Repo Development

**Status**: Current authority

这篇文档面向维护本仓库的人。可分发内容只有 `skills/`；手册、评测与根 `AGENTS.md` 都是仓库内部表面。

## 本地预览

```bash
make docs-manual-serve
make docs-maintainer-serve
```

可用 `PORT=3001` 覆盖默认端口。

## Canonical Source

- `skills/<name>/` 是独立 Agent Skills 包。
- 不创建运行时专属镜像、安装路径映射、治理模板或 sidecar。
- 修改名称或移动 supporting file 时同步修正引用。
- 根 `AGENTS.md` 可以包含本仓库专用规则，但不会复制到任何 Skill 包。

## 固定校验顺序

```bash
python3 maintainer/scripts/analysis/validate_skill_catalog.py
python3 maintainer/scripts/analysis/validate_agent_skills.py
python3 maintainer/scripts/analysis/check_cross_references.py --fail-on-broken
python3 maintainer/scripts/analysis/validate_repo_layout.py
python3 maintainer/scripts/evaluation/test_review_loop_output_contract.py
python3 maintainer/scripts/evaluation/run_artifact_routing_tests.py --mode report --fail-on-contract-issues
python3 maintainer/scripts/evaluation/test_artifact_routing_contract.py
python3 maintainer/scripts/evaluation/test_adr_contract.py
python3 maintainer/scripts/evaluation/test_skill_catalog_contract.py
python3 maintainer/scripts/evaluation/test_token_activation_contract.py
python3 maintainer/scripts/analysis/measure_prompt_surface.py --actual-tokens --validate-activation-contract --fail-on-budget
python3 maintainer/scripts/analysis/generate_skill_index.py --check
python3 maintainer/scripts/evaluation/compare_prompt_sizes.py
python3 maintainer/scripts/evaluation/run_trigger_tests.py --mode report --fail-on-protocol-issues
```

CI 另以固定 commit 的官方 `skills-ref==0.1.0` 对 catalog 输出的 12 个目录逐包校验；本地复现前先按 `.github/workflows/ci.yml` 安装同一固定版本。文档-only 修改可缩到 cross-reference 与定向阅读；Skill metadata、协议、catalog、引用或 token 合同变化应运行对应评测。

## Token 评估

```bash
python3 maintainer/scripts/analysis/measure_prompt_surface.py \
  --actual-tokens --validate-activation-contract --fail-on-budget
```

报告要区分：

1. 所有 Skill 的发现 metadata。
2. 单个已激活 `SKILL.md`。
3. 该场景实际读取的 supporting files。
4. 全部包正文一起加载的理论上界。

不要把理论上界当作正常单轮输入。根 `AGENTS.md` 只作为本仓库内部治理成本单列。

## 修改原则

- 主文件保留目标、硬约束、执行步骤、输出契约和停止条件。
- 只有按场景选择的长材料才下沉；每次必读的模板下沉不构成 token 节省。
- supporting file 保持一层直接引用，避免二跳发现。
- 历史报告如果描述已删除的适配层，不得当作当前操作说明。
