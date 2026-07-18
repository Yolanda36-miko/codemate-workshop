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
