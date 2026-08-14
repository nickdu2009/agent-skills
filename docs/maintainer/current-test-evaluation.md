# 当前项目测试评价

**Status**: Current authority
**Date**: 2026-08-13

当前公共测试面只验证 portable Agent Skills 内容，不声称覆盖任何具体运行时。

## 已覆盖

- `validate_agent_skills.py`: 标准 frontmatter 与目录名一致性。
- 官方 `skills-ref==0.1.0`: 以固定源码 commit 对 catalog 中 12 个标准包逐包校验。
- `validate_skill_catalog.py`: core 10、optional 2、retired 6、迁移矩阵和旧名称例外边界。
- `check_cross_references.py`: Skill 名称、chain alias 与文档根路径引用。
- `run_trigger_tests.py`: 101 个 metadata 触发案例、ID 唯一性与 12/12 正向覆盖。
- `run_artifact_routing_tests.py --mode report`: 38 个评审对象、模式、provenance 与写范围的确定性 fixture 合同。
- `test_artifact_routing_contract.py`: subtype 覆盖、self-delivery truth table、prompt/scorer 与全局触发覆盖的负例。
- `test_review_loop_output_contract.py`: 统一评审输出、权限和 result/issues 一致性合同。
- `test_adr_contract.py`: ADR producer/consumer 合同。
- `measure_prompt_surface.py`: exact `o200k_base` discovery、主文件、reference manifest、典型/重路径和全包绝对预算。
- `generate_skill_index.py --check` 与 `compare_prompt_sizes.py`: deterministic index 与 canonical metadata parity。
- `validate_repo_layout.py`: 单一 canonical `skills/` 与仓库布局边界。

## 未覆盖

- 运行时发现路径与冲突优先级。
- 显式调用、自动触发开关与权限语义。
- 子代理、上下文压缩和 supporting-file 实际读取。
- 插件或运行时 sidecar。
- 真实模型对 raw prompts 的路由等价性；report 模式验证 fixture/合同，不等同于 API 行为通过。

这些差异只有在出现明确适配需求后，才应以目标运行时的当前版本建立隔离验收；不能由 portable core 猜测。
