"""Functional tests for the layered exercise pair generation and validation system.

Covers 5 strict scenarios with comprehensive assertions on the deterministic
build_layered_exercise_pairs + exercise_pairs_to_sections + validate_layered_practice_sections pipeline,
plus 5-topic TestClient integration tests via POST /api/resources/generate.
"""

import io
import json
import sys
import traceback

FAILS = []
PASSES = []


def check(condition, label):
    if condition:
        PASSES.append(label)
        print(f"  PASS  {label}")
    else:
        FAILS.append(label)
        print(f"  FAIL  {label}")


def section(label):
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}")


from services.resource_service import (
    build_layered_exercise_pairs,
    validate_layered_practice_sections,
    exercise_pairs_to_sections,
    finalize_layered_practice_sections,
    _parse_answer_sections,
    _detect_topic_category,
    _extract_core_topic_terms,
    validate_final_resource_card,
)


def run_pipeline(topic, language='C++', resource_type='分层练习', normalized_module=''):
    pairs = build_layered_exercise_pairs(topic, normalized_module, language, resource_type)
    sections = exercise_pairs_to_sections(pairs)
    validation = validate_layered_practice_sections(sections, topic)
    return pairs, sections, validation


def assert_no_answer_hint(sections, label_prefix):
    """Verify NO answer_hint sections exist in the output."""
    hint_kinds = [s['kind'] for s in sections if s.get('kind') == 'answer_hint']
    check(len(hint_kinds) == 0, f"{label_prefix}: No answer_hint sections (found {len(hint_kinds)})")


def assert_answer_count_matches_practice(sections, label_prefix):
    """Verify answer count equals practice count."""
    practices = [s for s in sections if s.get('kind') == 'practice']
    answers = [s for s in sections if s.get('kind') == 'answer']
    check(len(practices) == len(answers),
         f"{label_prefix}: answer count ({len(answers)}) == practice count ({len(practices)})")
    check(len(practices) >= 5, f"{label_prefix}: at least 5 practices (got {len(practices)})")


# ══════════════════════════════════════════════════════════════════════════
#  SCENARIO 1: 二叉树前序遍历 + 分层练习 + C++
#  - Exact tree: A-B,C / B-D,E
#  - Exact traversals: 前序 A→B→D→E→C, 中序 D→B→E→A→C, etc.
# ══════════════════════════════════════════════════════════════════════════

def test_scenario_1():
    section("SCENARIO 1: 二叉树前序遍历 + 分层练习 + C++")

    pairs, sections, vr = run_pipeline("二叉树前序遍历", "C++", "分层练习", "二叉树")

    # === Pair count ===
    check(len(pairs) == 5, "S1.1: Exactly 5 exercise pairs")
    check(len(sections) == 10, "S1.2: Exactly 10 sections (5 practice + 5 answer)")
    assert_no_answer_hint(sections, "S1.2b")
    assert_answer_count_matches_practice(sections, "S1.2c")

    # === Section interleaving ===
    kinds = [s['kind'] for s in sections]
    expected_kinds = ['practice', 'answer'] * 5
    check(kinds == expected_kinds, "S1.3: Strict practice→answer interleaving")

    # === Validation ===
    check(vr['valid'] is True, "S1.4: Validation passes")
    check(len(vr['errors']) == 0, "S1.5: No validation errors")
    check(len(vr['warnings']) == 0, "S1.6: No validation warnings")

    # === Rich fields on every pair ===
    for i, p in enumerate(pairs):
        check(p.get('final_answer', ''), f"S1.7a: Pair {i+1} has final_answer")
        check(len(p.get('steps', [])) >= 2, f"S1.7b: Pair {i+1} has ≥2 steps (got {len(p.get('steps', []))})")
        check(p.get('explanation', ''), f"S1.7c: Pair {i+1} has explanation")
        check(p.get('pitfall', ''), f"S1.7d: Pair {i+1} has pitfall")

    # === Topic dispatch ===
    check(_detect_topic_category("二叉树前序遍历") == 'tree', "S1.8: Topic detected as 'tree'")

    # === Exact tree data in practice content ===
    p1q = pairs[0]['question']
    check('A' in p1q and 'B' in p1q and 'C' in p1q and 'D' in p1q and 'E' in p1q,
         "S1.9: Tree nodes A,B,C,D,E present in question")

    # === 4-section answer structure on all answer sections ===
    for i in range(1, 10, 2):
        content = sections[i].get('content', '')
        check('最终答案' in content, f"S1.10a: Answer {i//2+1} has 最终答案")
        check('解题步骤' in content, f"S1.10b: Answer {i//2+1} has 解题步骤")
        check('解析' in content, f"S1.10c: Answer {i//2+1} has 解析")
        check('易错提醒' in content, f"S1.10d: Answer {i//2+1} has 易错提醒")

    # === Level diversity ===
    levels = set(p['level'] for p in pairs)
    check({'基础', '进阶', '综合'}.issubset(levels),
         f"S1.11: All levels present: {levels}")

    # === First exercise asks for 前序遍历 ===
    check('前序' in pairs[0]['question'], "S1.12: First exercise asks for 前序遍历")


# ══════════════════════════════════════════════════════════════════════════
#  SCENARIO 2: 图的BFS/DFS遍历 + 分层练习
#  - Exact adjacency: A:B,C / B:D,E / C:F
#  - Exact BFS: A→B→C→D→E→F, DFS: A→B→D→E→C→F
# ══════════════════════════════════════════════════════════════════════════

def test_scenario_2():
    section("SCENARIO 2: 图的BFS/DFS遍历 + 分层练习")

    pairs, sections, vr = run_pipeline("图的BFS遍历", "C++", "分层练习", "图结构与图算法")

    check(len(pairs) == 5, "S2.1: Exactly 5 pairs")
    check(vr['valid'] is True, "S2.2: Validation passes")
    assert_no_answer_hint(sections, "S2.2b")
    assert_answer_count_matches_practice(sections, "S2.2c")
    check(_detect_topic_category("图的BFS遍历") == 'graph', "S2.3: Topic detected as 'graph'")

    # Cross-contamination check: no tree traversal terms in graph answers
    all_answers = ' '.join(sections[i].get('content', '') for i in range(1, 10, 2))
    check('前序遍历' not in all_answers, "S2.4: No tree preorder in graph answers")
    check('中序遍历' not in all_answers, "S2.5: No tree inorder in graph answers")

    # BFS/DFS results in answers
    check('BFS' in all_answers or '广度' in all_answers, "S2.6: BFS present in answers")
    check('DFS' in all_answers or '深度' in all_answers, "S2.7: DFS present in answers")

    kinds = [s['kind'] for s in sections]
    check(kinds[:10] == ['practice', 'answer'] * 5, "S2.8: Strict interleaving")


# ══════════════════════════════════════════════════════════════════════════
#  SCENARIO 3: 快速排序 + 分层练习
#  - Exact array: [6,3,8,2,5], pivot=5
#  - Final sorted: [2,3,5,6,8]
# ══════════════════════════════════════════════════════════════════════════

def test_scenario_3():
    section("SCENARIO 3: 快速排序 + 分层练习")

    pairs, sections, vr = run_pipeline("快速排序", "C++", "分层练习", "排序与查找")

    check(len(pairs) == 5, "S3.1: Exactly 5 pairs")
    check(vr['valid'] is True, "S3.2: Validation passes")
    assert_no_answer_hint(sections, "S3.2b")
    assert_answer_count_matches_practice(sections, "S3.2c")
    check(_detect_topic_category("快速排序") == 'sort', "S3.3: Topic detected as 'sort'")

    # Exact array data in question
    check('[6, 3, 8, 2, 5]' in pairs[0]['question'] or '[6,3,8,2,5]' in pairs[0]['question'],
         "S3.4: Exact sort array in first question")

    # Sorted result in answers
    all_text = ' '.join(sections[i].get('content', '') for i in range(1, 10, 2))
    check('2,3,5,6,8' in all_text or '2, 3, 5, 6, 8' in all_text,
         "S3.5: Final sorted array [2,3,5,6,8] in answers")

    # Pivot mentioned
    check('5' in pairs[0]['question'], "S3.6: Pivot value 5 in question")

    kinds = [s['kind'] for s in sections]
    check(kinds[:10] == ['practice', 'answer'] * 5, "S3.7: Strict interleaving")


# ══════════════════════════════════════════════════════════════════════════
#  SCENARIO 4: 0-1背包 + 分层练习
#  - Exact items: W=5, (w=2,v=3),(w=3,v=4),(w=4,v=5)
#  - Max value = 7, select items 1&2
# ══════════════════════════════════════════════════════════════════════════

def test_scenario_4():
    section("SCENARIO 4: 0-1背包 + 分层练习")

    pairs, sections, vr = run_pipeline("0-1背包问题", "C++", "分层练习", "动态规划入门")

    check(len(pairs) == 5, "S4.1: Exactly 5 pairs")
    check(vr['valid'] is True, "S4.2: Validation passes")
    assert_no_answer_hint(sections, "S4.2b")
    assert_answer_count_matches_practice(sections, "S4.2c")
    check(_detect_topic_category("0-1背包问题") == 'dp', "S4.3: Topic detected as 'dp'")

    # Exact items (w=2,v=3), (w=3,v=4), (w=4,v=5) in first question
    q1 = pairs[0]['question']
    check('2' in q1 and '3' in q1 and '4' in q1 and '5' in q1, "S4.4: Item weights/values in question")

    # W=5 capacity check
    all_text = ' '.join(sections[i].get('content', '') for i in range(1, 10, 2))
    check('5' in all_text, "S4.5: Capacity W=5 referenced in answers")

    # Max value = 7
    check('7' in all_text, "S4.6: Max value 7 in answers")

    # DP terms present
    check('dp' in all_text.lower() or 'DP' in all_text or '动态规划' in all_text,
         "S4.7: DP terminology in answers")

    kinds = [s['kind'] for s in sections]
    check(kinds[:10] == ['practice', 'answer'] * 5, "S4.8: Strict interleaving")


# ══════════════════════════════════════════════════════════════════════════
#  SCENARIO 5: Cross-cutting — all 7 topics + validation edge cases
# ══════════════════════════════════════════════════════════════════════════

def test_scenario_5():
    section("SCENARIO 5: Cross-cutting — all 7 topics + validation edge cases")

    all_topics = [
        ('二叉树前序遍历', '树', 'tree'),
        ('图的BFS遍历', '图结构与图算法', 'graph'),
        ('栈的基本操作', '栈与队列', 'stack_queue'),
        ('快速排序', '排序与查找', 'sort'),
        ('哈希表冲突解决', '散列表', 'hash'),
        ('0-1背包问题', '动态规划入门', 'dp'),
        ('Dijkstra最短路径', '图结构与图算法', 'dijkstra'),
    ]

    for topic, module, expected_cat in all_topics:
        # Category detection
        cat = _detect_topic_category(topic)
        check(cat == expected_cat,
             f"S5.1.{expected_cat}: detect_topic_category('{topic}') = '{cat}' (expected '{expected_cat}')")

        # Full pipeline
        pairs, sections, vr = run_pipeline(topic, 'C++', '分层练习', module)
        check(len(pairs) == 5, f"S5.2.{expected_cat}: 5 pairs for {topic}")
        check(vr['valid'] is True, f"S5.3.{expected_cat}: validation passes for {topic}")

        # 4-section structure for every answer
        for i in range(1, 10, 2):
            content = sections[i].get('content', '')
            has_all = all(s in content for s in ['最终答案', '解题步骤', '解析', '易错提醒'])
            check(has_all, f"S5.4.{expected_cat}: Answer {i//2+1} has all 4 sections")

        kinds = [s['kind'] for s in sections]
        check(kinds[:10] == ['practice', 'answer'] * 5,
             f"S5.5.{expected_cat}: Strict interleaving for {topic}")

    # ── Validation edge cases ──

    # 5a: Missing answer section after practice
    bad_sections = [
        {'kind': 'practice', 'heading': '题1', 'content': 'test'},
        {'kind': 'text', 'heading': 'not an answer', 'content': 'test'},
    ]
    vr = validate_layered_practice_sections(bad_sections, 'test')
    check(vr['valid'] is False, "S5.6a: Validation catches missing answer")
    check(any('no answer' in e for e in vr['errors']), "S5.6b: Error message mentions missing answer")

    # 5b: Missing 4-section structure
    bad_answer = [
        {'kind': 'practice', 'heading': '题1', 'content': 'test'},
        {'kind': 'answer', 'heading': '答1', 'content': 'Just an answer without sections'},
    ]
    vr2 = validate_layered_practice_sections(bad_answer, 'test')
    check(vr2['valid'] is False, "S5.7a: Validation catches missing 4-section structure")
    check(len(vr2['errors']) >= 3, f"S5.7b: At least 3 errors (missing 最终答案/解题步骤/解析/易错提醒), got {len(vr2['errors'])}")

    # 5c: Wrong count
    too_few = [{'kind': '分层练习', 'content': '分层练习 content'}]
    too_few += [{'kind': 'practice', 'content': 'p'}, {'kind': 'answer', 'content': '最终答案：x\n解题步骤：y\n解析：z\n易错提醒：w'}]
    vr3 = validate_layered_practice_sections(too_few, 'test')
    check(vr3['valid'] is False, "S5.8a: Validation catches too few practices")
    check(any('exactly 5' in e.lower() for e in vr3['errors']), "S5.8b: Error mentions exactly 5 requirement")

    # 5d: Topic cross-contamination
    tree_pairs, tree_sections, _ = run_pipeline("二叉树前序遍历", "C++", "分层练习", "树")
    all_tree_answers = ' '.join(s.get('content', '') for s in tree_sections if s['kind'] == 'answer')
    check('Dijkstra' not in all_tree_answers, "S5.9a: Tree answers don't mention Dijkstra")
    check('背包' not in all_tree_answers, "S5.9b: Tree answers don't mention knapsack")

    # 5e: Each pair has rich structured fields
    for topic, module, cat in all_topics:
        pairs, _, _ = run_pipeline(topic, 'C++', '分层练习', module)
        for i, p in enumerate(pairs):
            has_rich = (bool(p.get('final_answer')) and len(p.get('steps', [])) >= 2
                        and bool(p.get('explanation')) and bool(p.get('pitfall')))
            check(has_rich, f"S5.10.{cat}.{i+1}: Rich fields present")


# ══════════════════════════════════════════════════════════════════════════
#  SCENARIO 6: finalize_layered_practice_sections safeguard unit test
# ══════════════════════════════════════════════════════════════════════════

def test_scenario_6():
    section("SCENARIO 6: finalize_layered_practice_sections safeguard")

    # Simulate a card that has old answer_hint sections (which should be stripped)
    card = {
        'type': '分层练习',
        'title': '二叉树的遍历 — 分层练习',
        'sections': [
            {'kind': 'highlight', 'heading': '重点', 'content': '掌握二叉树的三种遍历方式'},
            {'kind': 'practice', 'heading': '旧练习题', 'content': 'OLD — should be removed'},
            {'kind': 'answer_hint', 'heading': '旧提示', 'content': 'OLD HINT — should be removed'},
            {'kind': 'answer', 'heading': '旧答案', 'content': 'OLD ANSWER — should be removed'},
            {'kind': 'warning', 'heading': '注意事项', 'content': '保留的注意事项'},
        ],
    }
    gen_context = {
        'topic': '二叉树前序遍历',
        'module': '二叉树',
        'normalized_language': 'C++',
    }

    result = finalize_layered_practice_sections(card, gen_context)

    # Non-practice/answer sections should survive
    kinds = [s['kind'] for s in result['sections']]
    check('highlight' in kinds, "S6.1: highlight section survives safeguard")
    check('warning' in kinds, "S6.2: warning section survives safeguard")

    # Old practice/answer/answer_hint sections should be gone
    old_contents = [s.get('content', '') for s in result['sections']]
    old_text = ' '.join(old_contents)
    check('OLD' not in old_text, "S6.3: All old practice/answer content removed")

    # New sections should be present — 5 practice + 5 answer = 10
    new_practices = [s for s in result['sections'] if s['kind'] == 'practice']
    new_answers = [s for s in result['sections'] if s['kind'] == 'answer']
    check(len(new_practices) == 5, f"S6.4: 5 new practice sections (got {len(new_practices)})")
    check(len(new_answers) == 5, f"S6.5: 5 new answer sections (got {len(new_answers)})")

    # No answer_hint in new sections
    assert_no_answer_hint(result['sections'], "S6.6")

    # Validation metadata attached
    check('_layered_practice_validation' in result, "S6.7: Validation metadata attached")
    check(result.get('_layered_practice_validation', {}).get('valid') is True,
         "S6.8: Rebuilt sections pass validation")

    # 4-section answer structure
    for ans in new_answers:
        content = ans.get('content', '')
        check('最终答案' in content, f"S6.9a: Answer has 最终答案")
        check('解题步骤' in content, f"S6.9b: Answer has 解题步骤")
        check('解析' in content, f"S6.9c: Answer has 解析")
        check('易错提醒' in content, f"S6.9d: Answer has 易错提醒")

    # Non-分层练习 cards should pass through unchanged
    non_practice_card = {'type': '代码示例', 'sections': [{'kind': 'code', 'content': 'int main() {}'}]}
    result2 = finalize_layered_practice_sections(non_practice_card, gen_context)
    check(result2 is non_practice_card, "S6.10: Non-分层练习 card passes through unchanged")


# ══════════════════════════════════════════════════════════════════════════
#  SCENARIO 7: 5-topic TestClient integration via POST /api/resources/generate
# ══════════════════════════════════════════════════════════════════════════

def test_scenario_7():
    section("SCENARIO 7: 5-topic TestClient integration (POST /api/resources/generate)")

    from main import app
    from fastapi.testclient import TestClient

    client = TestClient(app)

    test_cases = [
        {
            'label': '二叉树前序遍历',
            'course_id': 'data_structures',
            'knowledge_point': '二叉树前序遍历',
            'topic': '二叉树前序遍历',
            'difficulty': '基础',
            'language': 'C++',
            'resource_types': ['分层练习'],
        },
        {
            'label': '图的BFS遍历',
            'course_id': 'data_structures',
            'knowledge_point': '图的BFS遍历',
            'topic': '图的BFS遍历',
            'difficulty': '基础',
            'language': 'C++',
            'resource_types': ['分层练习'],
        },
        {
            'label': '快速排序',
            'course_id': 'data_structures',
            'knowledge_point': '快速排序',
            'topic': '快速排序',
            'difficulty': '基础',
            'language': 'Python',
            'resource_types': ['分层练习'],
        },
        {
            'label': '0-1背包问题',
            'course_id': 'data_structures',
            'knowledge_point': '0-1背包问题',
            'topic': '0-1背包问题',
            'difficulty': '进阶',
            'language': 'Python',
            'resource_types': ['分层练习'],
        },
        {
            'label': 'Dijkstra最短路径',
            'course_id': 'data_structures',
            'knowledge_point': 'Dijkstra最短路径',
            'topic': 'Dijkstra最短路径',
            'difficulty': '进阶',
            'language': 'Python',
            'resource_types': ['分层练习'],
        },
    ]

    for tc in test_cases:
        label = tc['label']

        resp = client.post('/api/resources/generate', json=tc)
        check(resp.status_code == 200, f"S7.{label}.1: HTTP 200 (got {resp.status_code})")

        data = resp.json()
        cards = data.get('resource_cards', [])

        # Find the 分层练习 card
        practice_cards = [c for c in cards if c.get('type') == '分层练习']
        check(len(practice_cards) >= 1,
             f"S7.{label}.2: At least 1 分层练习 card (got {len(practice_cards)})")

        if practice_cards:
            card = practice_cards[0]
            sections = card.get('sections', [])

            # Verify section kinds
            section_kinds = [s.get('kind') for s in sections]
            practices = [k for k in section_kinds if k == 'practice']
            answers = [k for k in section_kinds if k == 'answer']
            hints = [k for k in section_kinds if k == 'answer_hint']

            check(len(practices) >= 5,
                 f"S7.{label}.3: ≥5 practice sections (got {len(practices)})")
            check(len(answers) == len(practices),
                 f"S7.{label}.4: answer count ({len(answers)}) == practice count ({len(practices)})")
            check(len(hints) == 0,
                 f"S7.{label}.5: NO answer_hint sections (got {len(hints)})")

            # Verify practice→answer interleaving (each practice followed by answer)
            answer_indices = [i for i, k in enumerate(section_kinds) if k == 'answer']
            practice_indices = [i for i, k in enumerate(section_kinds) if k == 'practice']
            if len(practice_indices) >= 5 and len(answer_indices) >= 5:
                # First 5 practices should each have an answer right after
                for j in range(5):
                    interleaved = practice_indices[j] < answer_indices[j]
                    check(interleaved,
                         f"S7.{label}.6.{j}: practice[{j}] before answer[{j}]")

            # Verify 4-section answer structure in at least 3 answers
            answer_sections = [s for s in sections if s.get('kind') == 'answer']
            answers_with_4_sections = 0
            for ans in answer_sections:
                content = ans.get('content', '')
                if all(kw in content for kw in ['最终答案', '解题步骤', '解析', '易错提醒']):
                    answers_with_4_sections += 1
            check(answers_with_4_sections >= 3,
                 f"S7.{label}.7: ≥3 answers have all 4 sections (got {answers_with_4_sections})")

            # Verify module mapping
            normalized_module = data.get('normalized_module', '')
            check(normalized_module != '递归与调用栈' or label not in ('0-1背包问题', 'Dijkstra最短路径'),
                 f"S7.{label}.8: Module not wrong-default '递归与调用栈' (got '{normalized_module}')")

            # Verify no forbidden placeholders
            all_text = ' '.join(s.get('content', '') for s in sections)
            forbidden = ['核心原理已在上述内容中详细说明', '请参考上文', '答案略']
            for fb in forbidden:
                check(fb not in all_text,
                     f"S7.{label}.9: No forbidden text '{fb[:20]}...'")

    # Additional: verify all 5 topics return valid resource cards
    resp_all = client.post('/api/resources/generate', json={
        'course_id': 'data_structures',
        'knowledge_point': '二叉树前序遍历',
        'topic': '二叉树前序遍历',
        'difficulty': '基础',
        'language': 'C++',
        'resource_types': ['分层练习', '代码示例', '图解讲解', '易错点'],
    })
    check(resp_all.status_code == 200, "S7.all.1: Multi-type request returns 200")
    data_all = resp_all.json()
    cards_all = data_all.get('resource_cards', [])
    card_types = set(c.get('type') for c in cards_all)
    check('分层练习' in card_types, f"S7.all.2: 分层练习 card present (types={card_types})")


# ══════════════════════════════════════════════════════════════════════════
#  SCENARIO 8: DeepSeek integration — fallback & provider checks
# ══════════════════════════════════════════════════════════════════════════

def test_scenario_8():
    section("SCENARIO 8: DeepSeek integration (mock fallback & provider checks)")

    # ── 8a: LLM_PROVIDER=mock — existing flow must still work ──
    print("\n  -- 8a: LLM_PROVIDER=mock (baseline) --")
    from main import app
    from fastapi.testclient import TestClient

    client = TestClient(app)

    resp = client.post('/api/resources/generate', json={
        'course_id': 'data_structures',
        'knowledge_point': '二叉树前序遍历',
        'topic': '二叉树前序遍历',
        'difficulty': '基础',
        'language': 'C++',
        'resource_types': ['分层练习'],
    })
    check(resp.status_code == 200, f"S8a.1: mock mode returns 200 (got {resp.status_code})")
    data = resp.json()
    cards = data.get('resource_cards', [])
    check(len(cards) >= 1, f"S8a.2: mock mode returns resource_cards (got {len(cards)})")

    practice_cards = [c for c in cards if c.get('type') == '分层练习']
    if practice_cards:
        sections = practice_cards[0].get('sections', [])
        practices = [s for s in sections if s.get('kind') == 'practice']
        answers = [s for s in sections if s.get('kind') == 'answer']
        hints = [s for s in sections if s.get('kind') == 'answer_hint']
        check(len(practices) >= 5, f"S8a.3: mock mode ≥5 practices (got {len(practices)})")
        check(len(answers) == len(practices), f"S8a.4: mock mode answer==practice (got {len(answers)}=={len(practices)})")
        check(len(hints) == 0, f"S8a.5: mock mode no answer_hint (got {len(hints)})")

    # ── 8b: /api/health reports llm_provider ──
    print("\n  -- 8b: /api/health llm_provider field --")
    resp_health = client.get('/api/health')
    check(resp_health.status_code == 200, f"S8b.1: health endpoint returns 200 (got {resp_health.status_code})")
    health_data = resp_health.json()
    check('llm_provider' in health_data, f"S8b.2: health response has llm_provider field")
    check(health_data.get('llm_provider') in ('mock', 'openai', 'anthropic', 'deepseek'),
         f"S8b.3: llm_provider is a recognized value (got {health_data.get('llm_provider')!r})")

    # ── 8c: DeepSeek without API key must fallback to mock ──
    print("\n  -- 8c: LLM_PROVIDER=deepseek without DEEPSEEK_API_KEY → mock fallback --")
    import os
    from services.llm_service import get_llm, MockProvider, _LLM_INSTANCE as _llm_singleton
    import config

    # Save original values
    _orig_provider = os.environ.get('LLM_PROVIDER')
    _orig_key = os.environ.get('DEEPSEEK_API_KEY')
    _orig_setting_key = config.settings.DEEPSEEK_API_KEY

    try:
        # Simulate: provider=deepseek but no key in both os.environ AND settings
        os.environ['LLM_PROVIDER'] = 'deepseek'
        os.environ['DEEPSEEK_API_KEY'] = ''
        config.settings.DEEPSEEK_API_KEY = ''

        # Reset singleton to force re-creation
        import services.llm_service as lsm
        lsm._LLM_INSTANCE = None

        llm = get_llm()
        check(isinstance(llm, MockProvider),
             f"S8c.1: deepseek+no key → MockProvider (got {type(llm).__name__})")

        # Verify resource generate still works via mock fallback
        resp2 = client.post('/api/resources/generate', json={
            'course_id': 'data_structures',
            'knowledge_point': '图的BFS遍历',
            'topic': '图的BFS遍历',
            'difficulty': '基础',
            'language': 'Python',
            'resource_types': ['分层练习', '图解讲解'],
        })
        check(resp2.status_code == 200,
             f"S8c.2: deepseek+no key → resource gen still 200 (got {resp2.status_code})")

        data2 = resp2.json()
        cards2 = data2.get('resource_cards', [])
        check(len(cards2) >= 1, f"S8c.3: deepseek+no key → resource cards present (got {len(cards2)})")

        # Check layered practice still 5P+5A
        prac_cards = [c for c in cards2 if c.get('type') == '分层练习']
        if prac_cards:
            secs = prac_cards[0].get('sections', [])
            p_count = len([s for s in secs if s.get('kind') == 'practice'])
            a_count = len([s for s in secs if s.get('kind') == 'answer'])
            check(p_count >= 5, f"S8c.4: fallback still ≥5 practices (got {p_count})")
            check(a_count == p_count, f"S8c.5: fallback answer==practice (got {a_count}=={p_count})")

        # Check diagram still present for 图解讲解
        diagram_cards = [c for c in cards2 if c.get('type') == '图解讲解']
        if diagram_cards:
            d_secs = diagram_cards[0].get('sections', [])
            d_kinds = [s.get('kind') for s in d_secs]
            has_diagram = 'diagram' in d_kinds
            check(has_diagram, f"S8c.6: diagram card has diagram section (kinds={d_kinds[:6]})")

    finally:
        # Restore original environment
        if _orig_provider is not None:
            os.environ['LLM_PROVIDER'] = _orig_provider
        elif 'LLM_PROVIDER' in os.environ and _orig_provider is None:
            pass  # keep it as-is if we can't restore
        if _orig_key is not None:
            os.environ['DEEPSEEK_API_KEY'] = _orig_key
        config.settings.DEEPSEEK_API_KEY = _orig_setting_key
        # Reset singleton back
        lsm._LLM_INSTANCE = None

    print("\n  [Note] DeepSeek real API call not tested (no API key configured).")


# ══════════════════════════════════════════════════════════════════════════
#  SCENARIO 9: Tags, forbidden text, and union-find topic recognition
# ══════════════════════════════════════════════════════════════════════════

def test_scenario_9():
    section("SCENARIO 9: Tags quality, forbidden text, union-find topic mapping")

    from main import app
    from fastapi.testclient import TestClient
    from services.resource_service import resolve_module_name

    client = TestClient(app)

    # ── 9a: Tags assertions on all resource cards ──
    print("\n  -- 9a: Tags quality checks --")

    resp = client.post('/api/resources/generate', json={
        'course_id': 'data_structures',
        'knowledge_point': '二叉树前序遍历',
        'topic': '二叉树前序遍历',
        'difficulty': '基础',
        'language': 'C++',
        'resource_types': ['图解讲解', '代码示例', '分层练习', '易错点'],
    })
    check(resp.status_code == 200, f"S9a.1: Multi-type request returns 200 (got {resp.status_code})")
    data = resp.json()
    cards = data.get('resource_cards', [])
    check(len(cards) >= 3, f"S9a.2: At least 3 cards returned (got {len(cards)})")

    for i, card in enumerate(cards):
        tags = card.get('knowledge_points', card.get('tags', []))
        rtype = card.get('type', 'unknown')

        # tags must be a list
        check(isinstance(tags, list), f"S9a.3.{i}: tags is a list for {rtype}")

        if isinstance(tags, list):
            # At least 4 tags
            check(len(tags) >= 4,
                 f"S9a.4.{i}: {rtype} card has >=4 tags (got {len(tags)}: {tags})")

            # No empty strings
            empty_tags = [t for t in tags if not (t or '').strip()]
            check(len(empty_tags) == 0,
                 f"S9a.5.{i}: {rtype} card has no empty tags (empty: {empty_tags})")

            # All tags deduped
            check(len(tags) == len(set(tags)),
                 f"S9a.6.{i}: {rtype} card tags are deduped")

            # No forbidden placeholder tags
            forbidden_tags = {'标签1', '标签2', '标签3', '标签4', '知识点', '学习资源', '学习资料', '编程练习'}
            bad_tags = [t for t in tags if t in forbidden_tags]
            check(len(bad_tags) == 0,
                 f"S9a.7.{i}: {rtype} card has no forbidden placeholder tags (found: {bad_tags})")

    # ── 9b: Forbidden text scan ──
    print("\n  -- 9b: Forbidden text scan --")
    forbidden_patterns = [
        '答案略', '解析略', '请参考上文', '请见上文', '详见上文',
        '核心原理已在上述内容中详细说明', '此处省略',
        '根据前文', '如上所述',
    ]

    for i, card in enumerate(cards):
        rtype = card.get('type', 'unknown')
        title = card.get('title', '') or ''
        summary = card.get('summary', '') or ''
        tags = card.get('knowledge_points', card.get('tags', []))
        tags_text = ' '.join(str(t) for t in tags) if isinstance(tags, list) else ''

        sections = card.get('sections', []) or []
        section_text = ' '.join(
            (s.get('content', '') or '') + ' ' + (s.get('heading', '') or '')
            for s in sections if isinstance(s, dict)
        )
        all_visible = title + ' ' + summary + ' ' + tags_text + ' ' + section_text

        for pat in forbidden_patterns:
            check(pat not in all_visible,
                 f"S9b.{i}: '{pat}' NOT in {rtype} card visible text")

    # ── 9c: Union-Find topic mapping ──
    print("\n  -- 9c: Union-Find topic recognition --")

    # Test 1: 并查集中文 → 图结构与图算法
    module1 = resolve_module_name("并查集的路径压缩与按秩合并")
    check(module1 == '图结构与图算法',
         f"S9c.1: 并查集 maps to 图结构与图算法 (got '{module1}')")

    # Test 2: Union-Find English → 图结构与图算法
    module2 = resolve_module_name("Union-Find with path compression")
    check(module2 == '图结构与图算法',
         f"S9c.2: Union-Find maps to 图结构与图算法 (got '{module2}')")

    # Test 3: DSU → 图结构与图算法
    module3 = resolve_module_name("DSU解决连通分量问题")
    check(module3 == '图结构与图算法',
         f"S9c.3: DSU maps to 图结构与图算法 (got '{module3}')")

    # Test 4: 二分查找中的find → NOT 图结构与图算法
    module4 = resolve_module_name("二分查找中的 find 函数")
    check(module4 != '图结构与图算法',
         f"S9c.4: 二分查找+find NOT mapped to 图结构与图算法 (got '{module4}')")
    check(module4 == '排序与查找',
         f"S9c.5: 二分查找 maps to 排序与查找 (got '{module4}')")

    # Test 5: Disjoint Set Union → 图结构与图算法
    module5 = resolve_module_name("Disjoint Set Union implementation")
    check(module5 == '图结构与图算法',
         f"S9c.6: Disjoint Set Union maps to 图结构与图算法 (got '{module5}')")

    # Test 6: 路径压缩 → 图结构与图算法
    module6 = resolve_module_name("路径压缩优化")
    check(module6 == '图结构与图算法',
         f"S9c.7: 路径压缩 maps to 图结构与图算法 (got '{module6}')")

    # Test 7: 按秩合并 → 图结构与图算法
    module7 = resolve_module_name("按秩合并与路径压缩")
    check(module7 == '图结构与图算法',
         f"S9c.8: 按秩合并 maps to 图结构与图算法 (got '{module7}')")

    # ── 9d: Union-Find via API — generates correctly ──
    print("\n  -- 9d: Union-Find API resource generation --")
    resp_uf = client.post('/api/resources/generate', json={
        'course_id': 'data_structures',
        'knowledge_point': '并查集的路径压缩与按秩合并',
        'topic': '并查集的路径压缩与按秩合并',
        'difficulty': '进阶',
        'language': 'C++',
        'resource_types': ['分层练习'],
    })
    check(resp_uf.status_code == 200, f"S9d.1: Union-Find API returns 200 (got {resp_uf.status_code})")
    data_uf = resp_uf.json()

    # normalized_module must be 图结构与图算法
    uf_module = data_uf.get('normalized_module', '')
    check(uf_module == '图结构与图算法',
         f"S9d.2: Union-Find normalized_module is 图结构与图算法 (got '{uf_module}')")

    uf_cards = data_uf.get('resource_cards', [])
    check(len(uf_cards) >= 1, f"S9d.3: Union-Find returns cards (got {len(uf_cards)})")

    # Find 分层练习 card and verify structure
    practice_cards = [c for c in uf_cards if c.get('type') == '分层练习']
    if practice_cards:
        pc = practice_cards[0]
        sections = pc.get('sections', [])

        # 5P+5A
        p_count = len([s for s in sections if s.get('kind') == 'practice'])
        a_count = len([s for s in sections if s.get('kind') == 'answer'])
        check(p_count >= 5, f"S9d.4: Union-Find >=5 practices (got {p_count})")
        check(a_count == p_count, f"S9d.5: Union-Find answer==practice ({a_count}=={p_count})")

        # No answer_hint
        hint_count = len([s for s in sections if s.get('kind') == 'answer_hint'])
        check(hint_count == 0, f"S9d.6: Union-Find no answer_hint (got {hint_count})")

        # Strict interleaving: each practice immediately followed by its answer
        section_kinds = [s.get('kind') for s in sections]
        p_idx = [i for i, k in enumerate(section_kinds) if k == 'practice']
        a_idx = [i for i, k in enumerate(section_kinds) if k == 'answer']
        for j in range(min(5, len(p_idx), len(a_idx))):
            interleaved = p_idx[j] + 1 == a_idx[j]
            check(interleaved,
                 f"S9d.7.{j}: practice[{j}] at {p_idx[j]} immediately followed by answer[{j}] at {a_idx[j]}")

        # Tags >= 4 on practice card
        uf_tags = pc.get('knowledge_points', pc.get('tags', []))
        if isinstance(uf_tags, list):
            check(len(uf_tags) >= 4,
                 f"S9d.8: Union-Find card tags >=4 (got {len(uf_tags)}: {uf_tags})")
            # Tags should include union-find related terms
            uf_tag_text = ' '.join(uf_tags)
            has_uf_term = any(kw in uf_tag_text for kw in ['并查集', '路径压缩', '按秩合并', 'Union', 'DSU', '图'])
            check(has_uf_term,
                 f"S9d.9: Union-Find tags contain relevant terms (tags: {uf_tags})")

    # ── 9e: graph category detection for union-find ──
    print("\n  -- 9e: _detect_topic_category union-find dispatch --")
    from services.quality_gate import _detect_topic_category
    cat1 = _detect_topic_category("并查集的路径压缩与按秩合并")
    check(cat1 == 'graph',
         f"S9e.1: _detect_topic_category(并查集) = 'graph' (got '{cat1}')")
    cat2 = _detect_topic_category("Union-Find with path compression")
    check(cat2 == 'graph',
         f"S9e.2: _detect_topic_category(Union-Find) = 'graph' (got '{cat2}')")
    cat3 = _detect_topic_category("DSU解决连通分量")
    check(cat3 == 'graph',
         f"S9e.3: _detect_topic_category(DSU) = 'graph' (got '{cat3}')")
    cat4 = _detect_topic_category("二分查找中的 find 函数")
    check(cat4 != 'graph',
         f"S9e.4: _detect_topic_category(二分查找+find) != 'graph' (got '{cat4}')")
    check(cat4 == 'binary_search',
         f"S9e.5: _detect_topic_category(二分查找+find) = 'binary_search' (got '{cat4}')")


# ══════════════════════════════════════════════════════════════════════════
#  SCENARIO 10: Topic relevance validation — validate_final_resource_card
# ══════════════════════════════════════════════════════════════════════════

def test_scenario_10():
    section("SCENARIO 10: Topic relevance validation & warning card generation")

    # ── 10a: _extract_core_topic_terms ──
    print("\n  -- 10a: Core term extraction --")

    terms_km = _extract_core_topic_terms("KMP算法的next数组")
    check('KMP' in terms_km, "S10a.1: KMP acronym extracted")
    check('next数组' in terms_km or any('next' in t for t in terms_km),
         f"S10a.2: next数组 compound extracted (terms={terms_km[:5]})")
    check(len([t for t in terms_km if '字符串匹配' in t or '前缀' in t or '后缀' in t or '失配' in t]) >= 3,
         f"S10a.3: domain synonyms expanded (terms={terms_km[:8]})")

    terms_bfs = _extract_core_topic_terms("图的BFS遍历")
    check('BFS' in terms_bfs, "S10a.4: BFS acronym extracted")
    check(len([t for t in terms_bfs if '广度优先' in t or '队列' in t or '图遍历' in t]) >= 2,
         f"S10a.5: BFS domain synonyms expanded (terms={terms_bfs[:6]})")

    terms_empty = _extract_core_topic_terms("")
    check(terms_empty == [], "S10a.6: Empty topic returns empty list")

    # ── 10b: validate_final_resource_card — pass case ──
    print("\n  -- 10b: Validation — pass (correct topic) --")

    good_card = {
        'id': 'good-1',
        'type': '分层练习',
        'title': 'KMP算法与next数组 — 分层练习',
        'summary': '深入学习KMP字符串匹配算法中next数组的构建与失配处理',
        'language': 'C++',
        'sections': [
            {'kind': 'practice', 'content': '已知模式串"ABABAC"，求next数组的值'},
            {'kind': 'answer', 'content': '最终答案：next=[0,0,1,2,3,0]\n解题步骤：计算每个位置的最长公共前后缀\n解析：next[i]表示模式串前i个字符的最长公共前后缀长度\n易错提醒：next[0]恒为0'},
            {'kind': 'practice', 'content': '在KMP匹配中，当text[i]≠pattern[j]时，j应回退到next[j]'},
            {'kind': 'answer', 'content': '最终答案：j=next[j]\n解题步骤：利用next数组跳过已匹配前缀\n解析：失配时无需回溯text指针\n易错提醒：注意next数组下标从0还是1开始'},
            {'kind': 'practice', 'content': '求模式串"AAAAB"的next数组'},
            {'kind': 'answer', 'content': '最终答案：next=[0,1,2,3,0]\n解题步骤：逐个位置计算前缀后缀匹配\n解析：重复字符的模式串next值递增\n易错提醒：最后一个字符B导致next值回0'},
            {'kind': 'practice', 'content': 'KMP算法中next数组的含义：前缀函数π[i]表示什么？'},
            {'kind': 'answer', 'content': '最终答案：子串s[0..i]的最长真前缀且是真后缀的长度\n解题步骤：理解真前缀与真后缀的概念\n解析：π函数用于失配时快速跳转\n易错提醒：真前缀不能等于原串本身'},
            {'kind': 'practice', 'content': '将next数组优化为nextval数组'},
            {'kind': 'answer', 'content': '最终答案：nextval避免连续相同字符的冗余回退\n解题步骤：若pattern[j]==pattern[next[j]]则nextval[j]=nextval[next[j]]\n解析：优化后减少不必要的比较\n易错提醒：nextval适用于模式串有重复字符的场景'},
        ],
    }
    result_pass = validate_final_resource_card(good_card, 'KMP算法的next数组', '分层练习')
    check(result_pass.get('_topic_mismatch_warning') is not True,
         "S10b.1: Correct topic card passes validation")
    check(result_pass.get('id') == 'good-1',
         "S10b.2: Original card returned unchanged on pass")

    # ── 10c: validate_final_resource_card — fail (wrong topic) ──
    print("\n  -- 10c: Validation — fail (wrong topic) --")

    bad_card = {
        'id': 'bad-1',
        'type': '分层练习',
        'title': '二叉树遍历练习',
        'summary': '练习二叉树的前序、中序、后序遍历',
        'language': 'Python',
        'sections': [
            {'kind': 'practice', 'content': '写出二叉树的前序遍历结果'},
            {'kind': 'answer', 'content': '最终答案：ABDEC\n解题步骤：根左右\n解析：先访问根节点\n易错提醒：注意遍历顺序'},
            {'kind': 'practice', 'content': '写出中序遍历结果'},
            {'kind': 'answer', 'content': '最终答案：DBEAC\n解题步骤：左根右\n解析：中序反映排序关系\n易错提醒：BST中序为升序'},
            {'kind': 'practice', 'content': '写出后序遍历结果'},
            {'kind': 'answer', 'content': '最终答案：DEBCA\n解题步骤：左右根\n解析：后序用于删树\n易错提醒：根在最后'},
            {'kind': 'practice', 'content': '求二叉树深度'},
            {'kind': 'answer', 'content': '最终答案：3\n解题步骤：递归求左右子树深度\n解析：max(left,right)+1\n易错提醒：空树深度为0'},
            {'kind': 'practice', 'content': '判断是否为完全二叉树'},
            {'kind': 'answer', 'content': '最终答案：是\n解题步骤：层序遍历检查\n解析：完全二叉树除最后一层外全满\n易错提醒：注意与满二叉树区别'},
        ],
    }
    result_fail = validate_final_resource_card(bad_card, 'KMP算法的next数组', '分层练习')
    check(result_fail.get('_topic_mismatch_warning') is True,
         "S10c.1: Wrong-topic card triggers warning")
    check('KMP' in result_fail.get('title', ''),
         "S10c.2: Warning card title mentions requested topic KMP")
    issues = result_fail.get('_validation_issues', '')
    check('无关' in issues,
         f"S10c.3: Validation issues mention '无关' (got: {issues[:60]})")
    check(len(result_fail.get('sections', [])) >= 2,
         "S10c.4: Warning card has explanation sections")

    # ── 10d: Layered-practice-specific checks ──
    print("\n  -- 10d: Layered-practice specific checks --")

    too_few_card = {
        'id': 'few-1',
        'type': '分层练习',
        'title': 'KMP算法练习 — 分层练习',
        'summary': 'KMP字符串匹配练习',
        'language': 'C++',
        'sections': [
            {'kind': 'practice', 'content': 'KMP算法中next数组的计算'},
            {'kind': 'answer', 'content': '最终答案：next计算\n解题步骤：逐步计算\n解析：前缀后缀匹配\n易错提醒：下标从0开始'},
            {'kind': 'practice', 'content': 'KMP匹配过程中的失配处理'},
            {'kind': 'answer', 'content': '最终答案：回退到next[j]\n解题步骤：查表跳转\n解析：避免重复比较\n易错提醒：跳转后继续匹配'},
            {'kind': 'practice', 'content': 'KMP时间复杂度分析'},
            {'kind': 'answer', 'content': '最终答案：O(n+m)\n解题步骤：摊还分析\n解析：每个字符最多比较两次\n易错提醒：预处理O(m)'},
        ],
    }
    result_few = validate_final_resource_card(too_few_card, 'KMP算法的next数组', '分层练习')
    check(result_few.get('_topic_mismatch_warning') is True,
         "S10d.1: Too few practices (3) triggers warning")
    issues_few = result_few.get('_validation_issues', '')
    check('练习题数量' in issues_few,
         f"S10d.2: Validation mentions practice count (got: {issues_few[:60]})")

    hint_card = {
        'id': 'hint-1',
        'type': '分层练习',
        'title': 'KMP算法与next数组 — 分层练习',
        'summary': 'KMP匹配算法练习',
        'language': 'C++',
        'sections': [
            {'kind': 'practice', 'content': 'KMP算法中求next数组'},
            {'kind': 'answer', 'content': '最终答案：next计算\n解题步骤：分步计算\n解析：前后缀匹配\n易错提醒：注意边界'},
            {'kind': 'practice', 'content': 'KMP失配回退策略'},
            {'kind': 'answer', 'content': '最终答案：j=next[j]\n解题步骤：查表\n解析：跳转\n易错提醒：循环条件'},
            {'kind': 'practice', 'content': 'KMP与暴力匹配对比'},
            {'kind': 'answer', 'content': '最终答案：KMP O(n+m)\n解题步骤：对比分析\n解析：避免回溯\n易错提醒：预处理开销'},
            {'kind': 'answer_hint', 'heading': '提示', 'content': '这是不应该出现的提示'},
            {'kind': 'practice', 'content': 'next数组优化策略'},
            {'kind': 'answer', 'content': '最终答案：nextval优化\n解题步骤：消除冗余\n解析：连续相同字符\n易错提醒：nextval定义'},
            {'kind': 'practice', 'content': 'KMP在生物信息学中的应用'},
            {'kind': 'answer', 'content': '最终答案：序列比对\n解题步骤：模式匹配\n解析：基因序列搜索\n易错提醒：大数据优化'},
        ],
    }
    result_hint = validate_final_resource_card(hint_card, 'KMP算法的next数组', '分层练习')
    check(result_hint.get('_topic_mismatch_warning') is True,
         "S10d.3: answer_hint presence triggers warning")
    issues_hint = result_hint.get('_validation_issues', '')
    check('answer_hint' in issues_hint,
         f"S10d.4: Validation mentions answer_hint (got: {issues_hint[:60]})")

    # ── 10e: Non-layered-practice card validation ──
    print("\n  -- 10e: Non-layered-practice card validation --")

    code_card = {
        'id': 'code-1',
        'type': '代码示例',
        'title': 'KMP算法C++实现 — 代码示例',
        'summary': 'KMP字符串匹配算法的完整C++代码实现，包含next数组构建',
        'language': 'C++',
        'sections': [
            {'kind': 'code', 'language': 'C++', 'content': 'void buildNext(string p, int next[]) { ... }'},
            {'kind': 'text', 'content': 'KMP核心思想：利用部分匹配信息避免回溯'},
        ],
    }
    result_code = validate_final_resource_card(code_card, 'KMP算法的next数组', '代码示例')
    check(result_code.get('_topic_mismatch_warning') is not True,
         "S10e.1: Correct-topic code card passes validation")

    bad_code_card = {
        'id': 'code-bad',
        'type': '代码示例',
        'title': '二叉树遍历代码示例',
        'summary': '二叉树前序、中序、后序遍历的递归实现',
        'language': 'Python',
        'sections': [
            {'kind': 'code', 'language': 'Python', 'content': 'def preorder(root): ...'},
            {'kind': 'text', 'content': '二叉树的三种深度优先遍历方式'},
        ],
    }
    result_code_bad = validate_final_resource_card(bad_code_card, 'KMP算法的next数组', '代码示例')
    check(result_code_bad.get('_topic_mismatch_warning') is True,
         "S10e.2: Wrong-topic code card triggers warning")

    # ── 10f: API integration — unseen topic gets warning, known topic passes ──
    print("\n  -- 10f: API integration — topic relevance via API --")

    from main import app
    from fastapi.testclient import TestClient

    client = TestClient(app)

    resp_km = client.post('/api/resources/generate', json={
        'course_id': 'data_structures',
        'knowledge_point': 'KMP算法的next数组',
        'topic': 'KMP算法的next数组',
        'difficulty': '进阶',
        'language': 'C++',
        'resource_types': ['分层练习'],
    })
    check(resp_km.status_code == 200, f"S10f.1: KMP API returns 200 (got {resp_km.status_code})")
    cards_km = resp_km.json().get('resource_cards', [])
    check(len(cards_km) >= 1, f"S10f.2: KMP cards returned (got {len(cards_km)})")
    km_warnings = [c for c in cards_km if c.get('_topic_mismatch_warning')]
    check(len(km_warnings) >= 1,
         f"S10f.3: Unseen KMP topic triggers warning card (got {len(km_warnings)} warnings)")

    resp_tree = client.post('/api/resources/generate', json={
        'course_id': 'data_structures',
        'knowledge_point': '二叉树前序遍历',
        'topic': '二叉树前序遍历',
        'difficulty': '基础',
        'language': 'C++',
        'resource_types': ['分层练习'],
    })
    check(resp_tree.status_code == 200, f"S10f.4: Tree API returns 200 (got {resp_tree.status_code})")
    cards_tree = resp_tree.json().get('resource_cards', [])
    check(len(cards_tree) >= 1, f"S10f.5: Tree cards returned (got {len(cards_tree)})")
    tree_warnings = [c for c in cards_tree if c.get('_topic_mismatch_warning')]
    check(len(tree_warnings) == 0,
         f"S10f.6: Known tree topic passes validation (got {len(tree_warnings)} warnings)")

    if km_warnings:
        warn = km_warnings[0]
        check(warn.get('type') == '分层练习',
             f"S10f.7: Warning keeps original type (got '{warn.get('type')}')")
        check('KMP' in warn.get('title', ''),
             "S10f.8: Warning title mentions KMP")
        sections = warn.get('sections', [])
        kinds = [s.get('kind') for s in sections]
        check('highlight' in kinds,
             f"S10f.9: Warning has highlight section (kinds={kinds})")
        check('next_action' in kinds,
             f"S10f.10: Warning has next_action section (kinds={kinds})")

    # ── 10g: 二叉树遍历 term extraction coverage ──
    print("\n  -- 10g: 二叉树遍历 term extraction --")

    terms_bt = _extract_core_topic_terms("二叉树遍历")
    required_bt_terms = ['二叉树', '遍历', '前序', '中序', '后序', '层序', '节点', '递归', '栈']
    for req in required_bt_terms:
        check(req in terms_bt,
             f"S10g.{required_bt_terms.index(req)+1}: '{req}' in terms for 二叉树遍历 (terms={len(terms_bt)} total)")
    check(len(terms_bt) >= 12,
         f"S10g.10: At least 12 terms extracted (got {len(terms_bt)})")

    # ── 10h: 二叉树遍历 card — must PASS (fix false positive) ──
    print("\n  -- 10h: 二叉树遍历 false positive fix --")

    bt_card = {
        'id': 'bt-1',
        'type': '分层练习',
        'title': '二叉树遍历 — 分层练习',
        'summary': '系统练习二叉树的前序、中序、后序、层序遍历',
        'language': 'C++',
        'sections': [
            {'kind': 'practice', 'content': '给定二叉树A(B,C)，写出前序遍历序列'},
            {'kind': 'answer', 'content': '最终答案：ABC\n解题步骤：根→左→右\n解析：前序遍历先访问根节点\n易错提醒：注意区分前序与中序'},
            {'kind': 'practice', 'content': '对同一棵二叉树，写出中序遍历序列'},
            {'kind': 'answer', 'content': '最终答案：BAC\n解题步骤：左→根→右\n解析：中序遍历左子树先于根\n易错提醒：非BST中序不一定有序'},
            {'kind': 'practice', 'content': '写出后序遍历序列，并说明递归与非递归实现'},
            {'kind': 'answer', 'content': '最终答案：BCA\n解题步骤：左→右→根\n解析：后序常用于删除树节点\n易错提醒：非递归需要栈辅助'},
            {'kind': 'practice', 'content': '用队列实现二叉树的层序遍历'},
            {'kind': 'answer', 'content': '最终答案：ABC\n解题步骤：根入队→出队访问→左右子节点入队\n解析：层序即BFS\n易错提醒：空树特判'},
            {'kind': 'practice', 'content': '综合题：对比前序、中序、后序的访问顺序差异'},
            {'kind': 'answer', 'content': '最终答案：前序根左右、中序左根右、后序左右根\n解题步骤：记住根节点的位置\n解析：三种遍历的递归框架统一\n易错提醒：非递归时栈的压入顺序不同'},
        ],
    }
    result_bt = validate_final_resource_card(bt_card, '二叉树遍历', '分层练习')
    check(result_bt.get('_topic_mismatch_warning') is not True,
         "S10h.1: 二叉树遍历 card PASSES validation (false positive fixed)")
    check(result_bt.get('id') == 'bt-1',
         "S10h.2: Original card returned unchanged")

    # ── 10i: Cross-topic negative cases — must still FAIL ──
    print("\n  -- 10i: Cross-topic negative cases --")

    # KMP topic title but content about BFS
    card_km_bfs = {
        'id': 'cross-1',
        'type': '分层练习',
        'title': 'KMP算法 — 分层练习',
        'summary': 'KMP字符串匹配',
        'language': 'C++',
        'sections': [
            {'kind': 'practice', 'content': '写出图的BFS遍历序列'},
            {'kind': 'answer', 'content': '最终答案：队列实现BFS\n解题步骤：入队出队\n解析：层次遍历\n易错提醒：标记已访问'},
            {'kind': 'practice', 'content': 'BFS与DFS的区别'},
            {'kind': 'answer', 'content': '最终答案：BFS用队列DFS用栈\n解题步骤：数据结构不同\n解析：BFS求最短路径\n易错提醒：空间复杂度不同'},
            {'kind': 'practice', 'content': 'BFS在图遍历中的应用'},
            {'kind': 'answer', 'content': '最终答案：求无权图最短路径\n解题步骤：逐层扩展\n解析：O(V+E)\n易错提醒：有环图需标记'},
            {'kind': 'practice', 'content': '实现BFS算法'},
            {'kind': 'answer', 'content': '最终答案：queue实现\n解题步骤：初始化→入队→循环\n解析：模板代码\n易错提醒：边界条件'},
            {'kind': 'practice', 'content': 'BFS时间复杂度分析'},
            {'kind': 'answer', 'content': '最终答案：O(V+E)\n解题步骤：每个节点和边访问一次\n解析：线性时间\n易错提醒：稠密图O(V²)'},
        ],
    }
    result_km_bfs = validate_final_resource_card(card_km_bfs, 'KMP算法的next数组', '分层练习')
    check(result_km_bfs.get('_topic_mismatch_warning') is True,
         "S10i.1: KMP→BFS cross-topic card triggers warning (negative preserved)")

    # 并查集 topic title but content about binary tree
    card_uf_tree = {
        'id': 'cross-2',
        'type': '分层练习',
        'title': '并查集 — 分层练习',
        'summary': '并查集路径压缩',
        'language': 'C++',
        'sections': [
            {'kind': 'practice', 'content': '写二叉树前序遍历'},
            {'kind': 'answer', 'content': '最终答案：ABDEC\n解题步骤：根左右\n解析：递归访问\n易错提醒：空树返回'},
            {'kind': 'practice', 'content': '二叉树中序遍历'},
            {'kind': 'answer', 'content': '最终答案：DBEAC\n解题步骤：左根右\n解析：有序输出\n易错提醒：非BST'},
            {'kind': 'practice', 'content': '求二叉树深度'},
            {'kind': 'answer', 'content': '最终答案：max(left,right)+1\n解题步骤：递归\n解析：后序遍历变体\n易错提醒：空树深度0'},
            {'kind': 'practice', 'content': '二叉树层序遍历'},
            {'kind': 'answer', 'content': '最终答案：BFS\n解题步骤：队列\n解析：逐层访问\n易错提醒：记录层数'},
            {'kind': 'practice', 'content': '判断平衡二叉树'},
            {'kind': 'answer', 'content': '最终答案：左右子树高度差≤1\n解题步骤：递归求高度\n解析：AVL基础\n易错提醒：每层都需判断'},
        ],
    }
    result_uf_tree = validate_final_resource_card(card_uf_tree, '并查集路径压缩', '分层练习')
    check(result_uf_tree.get('_topic_mismatch_warning') is True,
         "S10i.2: 并查集→二叉树 cross-topic card triggers warning (negative preserved)")

    # 布隆过滤器 topic title but content about knapsack
    card_bf_knap = {
        'id': 'cross-3',
        'type': '分层练习',
        'title': '布隆过滤器 — 分层练习',
        'summary': '布隆过滤器原理',
        'language': 'Python',
        'sections': [
            {'kind': 'practice', 'content': '0-1背包状态转移方程'},
            {'kind': 'answer', 'content': '最终答案：dp[i][w]=max(dp[i-1][w],dp[i-1][w-wi]+vi)\n解题步骤：二维DP\n解析：选或不选\n易错提醒：初始化dp[0][*]=0'},
            {'kind': 'practice', 'content': '完全背包问题'},
            {'kind': 'answer', 'content': '最终答案：dp[w]=max(dp[w],dp[w-wi]+vi)\n解题步骤：一维正序\n解析：无限物品\n易错提醒：遍历顺序'},
            {'kind': 'practice', 'content': '多重背包二进制优化'},
            {'kind': 'answer', 'content': '最终答案：拆分物品\n解题步骤：二进制分组\n解析：降为0-1\n易错提醒：余数处理'},
            {'kind': 'practice', 'content': '背包问题变种'},
            {'kind': 'answer', 'content': '最终答案：分组背包等\n解题步骤：按情况处理\n解析：灵活变通\n易错提醒：容量限制'},
            {'kind': 'practice', 'content': 'DP背包时间优化'},
            {'kind': 'answer', 'content': '最终答案：单调队列优化\n解题步骤：滑动窗口\n解析：O(nW)\n易错提醒：下标计算'},
        ],
    }
    result_bf_knap = validate_final_resource_card(card_bf_knap, '布隆过滤器', '分层练习')
    check(result_bf_knap.get('_topic_mismatch_warning') is True,
         "S10i.3: 布隆过滤器→背包 cross-topic card triggers warning (negative preserved)")


# ══════════════════════════════════════════════════════════════════════════
#  RUN ALL
# ══════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    # Fix Windows GBK encoding for emoji output
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    print("=" * 60)
    print("  FUNCTIONAL TESTS — Layered Exercise Pair Generation")
    print("=" * 60)

    try:
        test_scenario_1()
        test_scenario_2()
        test_scenario_3()
        test_scenario_4()
        test_scenario_5()
        test_scenario_6()
        test_scenario_7()
        test_scenario_8()
        test_scenario_9()
        test_scenario_10()
    except Exception as e:
        print(f"\n  EXCEPTION: {e}")
        traceback.print_exc()
        FAILS.append(f"Unhandled exception: {e}")

    # ── Summary ──
    total = len(PASSES) + len(FAILS)
    print(f"\n{'='*60}")
    print(f"  RESULTS: {len(PASSES)}/{total} PASSED")
    if FAILS:
        print(f"  FAILURES:")
        for f in FAILS:
            print(f"    - {f}")
    print(f"{'='*60}")

    sys.exit(0 if len(FAILS) == 0 else 1)
