# LLM缓存优化指南

**版本**: 1.0  
**日期**: 2026-04-11  
**状态**: 建议实施  
**适用范围**: Trigger测试、批量评估、CI/CD流水线

## 执行摘要

当前的token优化工作**部分缓存友好**，但存在显著改进空间。通过实施分层缓存策略和prompt结构标准化，可以将缓存命中率从~20%提升到~60%，实现**3倍成本效率提升**。

## 当前缓存友好性评估

### ✅ 已实现的缓存友好优化

| 优化项 | 缓存友好性 | 命中率估算 | 说明 |
|--------|----------|-----------|------|
| **skill_index.json** | ⭐⭐⭐⭐⭐ | ~95% | 固定JSON格式，每次加载完全相同 |
| **CLAUDE.md集中化** | ⭐⭐⭐⭐ | ~90% | 单一数据源，治理规则稳定 |
| **治理模板压缩** | ⭐⭐⭐⭐ | ~90% | 低变更频率，可作为prompt前缀缓存 |
| **链别名引用** | ⭐⭐⭐ | ~75% | CLAUDE.md定义稳定，但引用点分散 |

### ⚠️ 缓存不够友好的部分

| 问题 | 影响 | 命中率 | 改进潜力 |
|------|------|--------|---------|
| **技能SKILL.md动态加载** | 排列组合导致低命中率 | ~30% | 高（改用skill_index.json） |
| **技能列表顺序不固定** | 相同技能组不同顺序=不同prompt | ~40% | 高（固定排序） |
| **Prompt结构不统一** | 每个测试用例结构不同 | ~20% | 中等（模板化） |
| **评估提示过度动态** | 上下文频繁变化 | ~25% | 中等（分层设计） |

## 缓存优化策略

### 🎯 Tier 1: 立即可实施（零代码改动）

#### 1. 启用Compact模式作为默认

**当前:**
```bash
python3 maintainer/scripts/evaluation/run_trigger_tests.py  # 使用verbose模式
```

**优化后:**
```bash
python3 maintainer/scripts/evaluation/run_trigger_tests.py --compact-mode  # 缓存友好
```

**收益:**
- 缓存命中率: 30% → 55% (+25%)
- 原因: skill_index.json是固定快照，不受文件系统变化影响

**在CI/CD中应用:**
```yaml
# .github/workflows/token-efficiency-check.yml
- name: Run trigger tests
  run: |
    python3 maintainer/scripts/evaluation/run_trigger_tests.py \
      --compact-mode \  # 启用缓存友好模式
      --mode report
```

#### 2. 固定技能描述排序

**修改 `generate_skill_index.py`:**
```python
# 在生成skill_index.json时按字母顺序排序
skills = sorted(skills, key=lambda s: s['name'])
```

**收益:**
- 缓存命中率: 55% → 65% (+10%)
- 原因: 相同技能集合产生相同prompt，无论加载顺序

### 🚀 Tier 2: 短期实施（小代码改动）

#### 3. 分层Prompt构造

**实现分层缓存结构:**

```python
# maintainer/scripts/evaluation/prompt_builder.py (新文件)

class CacheFriendlyPromptBuilder:
    """
    构造LLM缓存友好的分层prompt
    
    Prompt结构:
    [Layer 1: 固定治理前缀]  <- 高缓存命中 (~95%)
    [Layer 2: 排序技能列表]  <- 中等缓存命中 (~75%)
    [Layer 3: 具体测试用例]  <- 低缓存命中 (~25%)
    """
    
    @staticmethod
    def build_governance_prefix():
        """Layer 1: 完全固定的治理规则（高缓存）"""
        return f"""
You are evaluating skill trigger precision.

Governance rules (from CLAUDE.md):
{load_claude_md_trigger_section()}

Quality criteria:
- Trigger on exact match to task characteristics
- Skip when task doesn't match skill's "Use when" clause
- Provide clear reasoning for each decision
"""
    
    @staticmethod
    def build_skill_context(skill_names: List[str]):
        """Layer 2: 排序后的技能列表（中等缓存）"""
        # 关键: 固定排序以提高缓存命中率
        sorted_skills = sorted(skill_names)
        index = load_skill_index()
        
        skills_block = "\n\n".join([
            f"**{name}**: {index[name]['description']}"
            for name in sorted_skills
        ])
        
        return f"""
Available skills (alphabetically sorted):

{skills_block}
"""
    
    @staticmethod
    def build_test_case(test_data: dict):
        """Layer 3: 可变测试用例（低缓存，但前两层已缓存）"""
        return f"""
Test case:
Prompt: {test_data['prompt']}
Expected triggers: {test_data['should_trigger']}
Expected skips: {test_data['should_not_trigger']}

Evaluate and respond.
"""
    
    def build_full_prompt(self, skill_names: List[str], test_case: dict) -> str:
        """组合所有层级，最大化缓存重用"""
        return "\n\n".join([
            self.build_governance_prefix(),      # Layer 1: 缓存
            self.build_skill_context(skill_names),  # Layer 2: 缓存
            self.build_test_case(test_case)      # Layer 3: 不缓存
        ])
```

**使用示例:**
```python
# 在run_trigger_tests.py中集成

builder = CacheFriendlyPromptBuilder()

# 批处理相同技能集合的测试用例
for skill_group, test_cases in group_by_skills(all_tests):
    # Layer 1和Layer 2对整个批次保持不变，最大化缓存
    for test_case in test_cases:
        prompt = builder.build_full_prompt(
            skill_names=skill_group,
            test_case=test_case
        )
        # 发送到LLM...
```

**收益:**
- 缓存命中率: 65% → 75% (+10%)
- Layer 1缓存: ~95%（governance规则基本不变）
- Layer 2缓存: ~75%（相同技能组合多次复用）
- Layer 3缓存: ~25%（每个测试用例不同）

#### 4. 批处理相同上下文测试

**优化测试执行顺序:**

```python
# 按技能组合分组测试用例
def group_tests_by_skill_context(test_cases):
    """
    将测试用例按技能上下文分组，最大化缓存重用
    
    示例:
    Input: [test1(bugfix-workflow), test2(plan-before-action), test3(bugfix-workflow)]
    Output: {
        (bugfix-workflow,): [test1, test3],
        (plan-before-action,): [test2]
    }
    """
    groups = defaultdict(list)
    for test in test_cases:
        # 标准化技能集合为排序的元组
        skill_set = tuple(sorted(test.applicable_skills))
        groups[skill_set].append(test)
    return groups

# 批量执行
for skill_set, tests in group_tests_by_skill_context(all_tests):
    print(f"Executing {len(tests)} tests with context: {skill_set}")
    # Layer 1+2在整个批次中缓存命中
    for test in tests:
        execute_test(skill_set, test)
```

**收益:**
- 缓存命中率: 75% → 80% (+5%)
- 减少LLM调用延迟（缓存命中时快10-100倍）
- 成本节省: ~60%

### 🏗️ Tier 3: 中期实施（架构优化）

#### 5. Prompt模板注册系统

创建prompt模板注册表，标准化所有评估场景:

```python
# maintainer/scripts/evaluation/prompt_templates.py

PROMPT_TEMPLATES = {
    "trigger_evaluation": {
        "governance_prefix": "...",  # 固定，高缓存
        "skill_context": "{sorted_skills}",  # 半固定，中等缓存
        "test_case": "{test_data}",  # 可变，低缓存
        "cache_layers": [
            {"name": "governance", "ttl": "7d", "expected_hit_rate": 0.95},
            {"name": "skills", "ttl": "1d", "expected_hit_rate": 0.75},
            {"name": "test_case", "ttl": "0", "expected_hit_rate": 0.25}
        ]
    },
    "skill_review": {
        # 其他场景模板...
    }
}
```

#### 6. 缓存命中率监控

在审计系统中添加缓存指标:

```python
# maintainer/scripts/audit/cache_efficiency_report.py

def measure_cache_efficiency():
    """
    测量LLM调用的缓存效率
    
    指标:
    - 缓存命中率 (实际 vs 预期)
    - 每层缓存命中次数
    - 成本节省估算
    """
    return {
        "layer1_governance": {
            "hit_rate": 0.94,
            "expected": 0.95,
            "status": "OK"
        },
        "layer2_skills": {
            "hit_rate": 0.68,
            "expected": 0.75,
            "status": "WARN",  # 低于预期
            "recommendation": "检查技能列表排序是否一致"
        },
        "layer3_test_case": {
            "hit_rate": 0.22,
            "expected": 0.25,
            "status": "OK"
        },
        "overall": {
            "hit_rate": 0.61,
            "target": 0.60,
            "cost_savings": "59%"
        }
    }
```

## 缓存命中率对比

### 优化前（当前状态）

```
Prompt构造: 动态+无序
├─ 治理规则: 每次重新加载 CLAUDE.md
├─ 技能列表: 随机顺序，18! 种可能
└─ 测试用例: 每个不同

估算缓存命中率: ~20%
成本效率: 基线 (1x)
```

### 优化后（Tier 1+2实施）

```
Prompt构造: 分层+固定排序
├─ [Layer 1] 治理规则: 固定前缀 (~95% 缓存)
├─ [Layer 2] 技能列表: 字母排序 (~75% 缓存)
└─ [Layer 3] 测试用例: 可变 (~25% 缓存)

估算缓存命中率: ~60%
成本效率: 3倍提升 (3x)
```

### 优化后（Tier 1+2+3实施）

```
Prompt构造: 模板化+批处理+监控
├─ [Layer 1] 固定模板 (~95% 缓存)
├─ [Layer 2] 批处理复用 (~80% 缓存)
├─ [Layer 3] 最小可变 (~30% 缓存)
└─ [Monitor] 实时监控+优化

估算缓存命中率: ~75%
成本效率: 4倍提升 (4x)
```

## 实施路线图

### Phase 1: 立即行动（本周）

- [x] 文档当前缓存友好性
- [ ] CI/CD中启用`--compact-mode`
- [ ] 修改`generate_skill_index.py`固定排序
- [ ] 重新生成`skill_index.json`
- [ ] 验证缓存命中率提升

**预期收益:** 30% → 65% 缓存命中率

### Phase 2: 短期实施（2周内）

- [ ] 实现`CacheFriendlyPromptBuilder`
- [ ] 更新`run_trigger_tests.py`使用分层prompt
- [ ] 实现测试用例批处理分组
- [ ] A/B测试对比成本

**预期收益:** 65% → 80% 缓存命中率

### Phase 3: 中期优化（1个月内）

- [ ] 建立prompt模板注册系统
- [ ] 集成缓存效率监控到审计系统
- [ ] 优化所有评估场景
- [ ] 建立缓存最佳实践文档

**预期收益:** 80% → 90% 缓存命中率（理论上限）

## 验证方法

### 1. 本地测试

```bash
# 测试compact模式缓存效率
time python3 maintainer/scripts/evaluation/run_trigger_tests.py --mode report
# 首次运行: ~60秒

time python3 maintainer/scripts/evaluation/run_trigger_tests.py --mode report  
# 二次运行（缓存命中）: ~20秒
# 缓存命中率 ≈ (60-20)/60 = 67%
```

### 2. 监控LLM API缓存指标

如果使用支持缓存的API（如OpenAI、Anthropic）:

```python
# 解析API响应中的缓存头
response.headers.get('X-Cache-Hit')  # 'true' or 'false'
response.usage.prompt_tokens_cached  # 缓存token数
```

### 3. 成本对比

```python
# 记录优化前后成本
cost_before = count_trigger_tests * avg_prompt_tokens * token_price
cost_after = count_trigger_tests * (1 - cache_hit_rate) * avg_prompt_tokens * token_price

savings = (cost_before - cost_after) / cost_before
# 预期节省: ~60%
```

## 注意事项

### 缓存失效场景

1. **CLAUDE.md更新** → Layer 1缓存全部失效
2. **技能索引重新生成** → Layer 2缓存失效
3. **测试用例修改** → Layer 3缓存失效（预期行为）

**建议:** 
- 定期批量更新（不要频繁小改）
- 使用版本号标记缓存层
- 监控失效率，异常时告警

### 缓存与质量权衡

⚠️ **警告:** 过度缓存可能掩盖质量问题

- ✅ 对固定内容缓存（governance规则）
- ✅ 对排序后的技能列表缓存
- ⚠️ 不缓存测试用例本身
- ❌ 不缓存评估结果（每次都应重新评估）

## 总结

当前token优化工作为缓存优化奠定了良好基础:

✅ **优势:**
- skill_index.json提供稳定快照
- 治理规则集中化在CLAUDE.md
- 链别名减少重复

⚠️ **待改进:**
- 技能列表排序不固定
- Prompt结构未分层
- 缺乏缓存监控

**优先级建议:**
1. **立即:** 启用compact模式 (零成本，高收益)
2. **短期:** 固定排序+分层prompt (小改动，大收益)
3. **中期:** 模板化+监控 (架构优化，持续收益)

**预期总收益:** 3-4倍成本效率提升
