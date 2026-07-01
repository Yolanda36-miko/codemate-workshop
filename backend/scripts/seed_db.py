"""
数据库种子数据填充脚本
用于向数据库填充基础数据，支持幂等操作
"""
import sys
import os

# 添加父目录到路径以便导入
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal, engine
from models import (
    User, Course, CourseRelation,
    KnowledgePoint, KnowledgePointRelation,
    Badge
)
from sqlalchemy import inspect


def seed_users(session):
    """填充用户数据"""
    print("填充用户数据...")
    
    users_data = [
        {
            "username": "demo_user",
            "display_name": "演示学生",
            "major": "计算机科学与技术",
            "grade": "大二",
            "avatar_text": "演",
            "mode": "demo",
        },
        {
            "username": "local_user",
            "display_name": None,
            "major": None,
            "grade": None,
            "avatar_text": "本",
            "mode": "local",
        },
    ]
    
    created_count = 0
    for user_data in users_data:
        existing_user = session.query(User).filter_by(username=user_data["username"]).first()
        if existing_user:
            print(f"  - 用户 '{user_data['username']}' 已存在，跳过")
            continue
        
        user = User(**user_data)
        session.add(user)
        created_count += 1
    
    if created_count > 0:
        session.commit()
        print(f"  ✓ 已创建 {created_count} 个用户")
    else:
        print("  无新用户需要创建")


def seed_courses(session):
    """填充课程数据 — 数据结构与算法内部模块"""
    print("填充课程数据...")

    courses_data = [
        {
            "course_code": "complexity",
            "name": "复杂度分析",
            "description": "理解算法效率的度量方式，掌握时间复杂度与空间复杂度的分析方法。",
            "stage": "基础模块",
            "positioning": "重点演示",
            "keywords": '["复杂度", "大O表示法", "渐进分析", "时间复杂度", "空间复杂度"]',
        },
        {
            "course_code": "linear-list",
            "name": "线性表",
            "description": "掌握顺序表与链式存储结构的原理、实现及适用场景。",
            "stage": "基础模块",
            "positioning": "重点演示",
            "keywords": '["线性表", "顺序表", "链表", "单链表", "双向链表"]',
        },
        {
            "course_code": "stack-queue",
            "name": "栈与队列",
            "description": "理解栈与队列的逻辑结构、存储实现及在算法中的经典应用。",
            "stage": "核心模块",
            "positioning": "重点演示",
            "keywords": '["栈", "队列", "LIFO", "FIFO", "表达式求值", "BFS"]',
        },
        {
            "course_code": "recursion-callstack",
            "name": "递归与调用栈",
            "description": "深入理解递归思想、调用栈机制，掌握递归算法的设计与调试。",
            "stage": "建议优先学习",
            "positioning": "重点演示",
            "keywords": '["递归", "调用栈", "栈帧", "基准情形", "尾递归", "分治"]',
        },
        {
            "course_code": "tree",
            "name": "树与二叉树",
            "description": "系统学习树结构，掌握二叉树遍历、二叉搜索树及平衡树的核心算法。",
            "stage": "核心模块",
            "positioning": "重点演示",
            "keywords": '["二叉树", "遍历", "BST", "AVL", "堆", "哈夫曼树"]',
        },
        {
            "course_code": "graph",
            "name": "图结构与图算法",
            "description": "学习图的存储结构与遍历算法，掌握最短路径、拓扑排序等经典图算法。",
            "stage": "进阶模块",
            "positioning": "重点演示",
            "keywords": '["图", "DFS", "BFS", "Dijkstra", "拓扑排序", "最小生成树"]',
        },
        {
            "course_code": "sort-search",
            "name": "排序与查找",
            "description": "掌握经典排序与查找算法的原理、实现及性能对比。",
            "stage": "核心模块",
            "positioning": "重点演示",
            "keywords": '["排序", "快速排序", "归并排序", "二分查找", "稳定性"]',
        },
        {
            "course_code": "hash",
            "name": "散列表",
            "description": "理解散列表的原理与实现，掌握哈希函数设计与冲突解决方法。",
            "stage": "进阶模块",
            "positioning": "重点演示",
            "keywords": '["散列表", "哈希函数", "链地址法", "开放定址", "rehash"]',
        },
        {
            "course_code": "dp",
            "name": "动态规划入门",
            "description": "入门动态规划思想，掌握状态定义、转移方程和经典DP问题的求解。",
            "stage": "进阶模块",
            "positioning": "重点演示",
            "keywords": '["动态规划", "最优子结构", "状态转移", "记忆化搜索", "背包问题"]',
        },
        {
            "course_code": "ds-project",
            "name": "综合项目实践",
            "description": "将所学数据结构与算法知识应用于综合项目，培养实际建模与编码能力。",
            "stage": "综合应用",
            "positioning": "重点演示",
            "keywords": '["项目", "综合", "数据结构选型", "实际建模", "测试调试"]',
        },
    ]
    
    created_count = 0
    for course_data in courses_data:
        existing_course = session.query(Course).filter_by(course_code=course_data["course_code"]).first()
        if existing_course:
            print(f"  - 课程 '{course_data['course_code']}' 已存在，跳过")
            continue
        
        course = Course(**course_data)
        session.add(course)
        created_count += 1
    
    if created_count > 0:
        session.commit()
        print(f"  ✓ 已创建 {created_count} 个课程")
    else:
        print("  无新课程需要创建")


def seed_course_relations(session):
    """填充课程关系数据（模块间依赖）"""
    print("填充课程关系数据...")

    complexity = session.query(Course).filter_by(course_code="complexity").first()
    linear_list = session.query(Course).filter_by(course_code="linear-list").first()
    stack_queue = session.query(Course).filter_by(course_code="stack-queue").first()
    recursion = session.query(Course).filter_by(course_code="recursion-callstack").first()
    tree = session.query(Course).filter_by(course_code="tree").first()

    if not complexity or not linear_list:
        print("  警告：基础模块不存在，跳过课程关系填充")
        return

    relations_data = []
    # 基础模块之间无强依赖
    if linear_list and stack_queue:
        relations_data.append({
            "from_course_id": linear_list.id,
            "to_course_id": stack_queue.id,
            "relation_type": "prerequisite",
            "description": "线性表是栈与队列实现的基础",
        })
    if stack_queue and recursion:
        relations_data.append({
            "from_course_id": stack_queue.id,
            "to_course_id": recursion.id,
            "relation_type": "prerequisite",
            "description": "栈的理解是递归调用栈学习的基础",
        })
    if recursion and tree:
        relations_data.append({
            "from_course_id": recursion.id,
            "to_course_id": tree.id,
            "relation_type": "prerequisite",
            "description": "递归思想是二叉树递归遍历的前置知识",
        })
    
    created_count = 0
    for relation_data in relations_data:
        existing_relation = session.query(CourseRelation).filter(
            CourseRelation.from_course_id == relation_data["from_course_id"],
            CourseRelation.to_course_id == relation_data["to_course_id"]
        ).first()
        if existing_relation:
            print("  - 课程关系已存在，跳过")
            continue
        
        relation = CourseRelation(**relation_data)
        session.add(relation)
        created_count += 1
    
    if created_count > 0:
        session.commit()
        print(f"  ✓ 已创建 {created_count} 个课程关系")
    else:
        print("  无新课程关系需要创建")


def seed_knowledge_points(session):
    """填充知识点数据"""
    print("填充知识点数据...")

    complexity = session.query(Course).filter_by(course_code="complexity").first()
    stack_queue = session.query(Course).filter_by(course_code="stack-queue").first()
    recursion = session.query(Course).filter_by(course_code="recursion-callstack").first()
    tree = session.query(Course).filter_by(course_code="tree").first()
    sort_search = session.query(Course).filter_by(course_code="sort-search").first()

    if not complexity or not recursion:
        print("  警告：基础模块不存在，跳过知识点填充")
        return

    knowledge_points_data = [
        {
            "course_id": complexity.id,
            "name": "时间复杂度分析",
            "description": "学习大O表示法，分析算法的时间复杂度",
            "difficulty": "基础",
            "tags": '["复杂度", "大O", "渐进分析"]',
            "common_errors": '["嵌套循环复杂度误判", "忽略递归复杂度"]',
        },
        {
            "course_id": stack_queue.id or complexity.id,
            "name": "栈的应用",
            "description": "理解栈在表达式求值、括号匹配中的应用",
            "difficulty": "基础",
            "tags": '["栈", "LIFO", "表达式求值"]',
            "common_errors": '["栈空/栈满判断", "出栈顺序理解错误"]',
        },
        {
            "course_id": recursion.id,
            "name": "递归三要素",
            "description": "掌握递归函数的基准情形、递归关系和递归调用",
            "difficulty": "进阶",
            "tags": '["递归", "基准情形", "调用栈"]',
            "common_errors": '["递归出口缺失", "栈溢出", "重复计算"]',
        },
        {
            "course_id": tree.id or recursion.id,
            "name": "二叉树遍历",
            "description": "掌握二叉树的前序、中序、后序和层序遍历方法",
            "difficulty": "进阶",
            "tags": '["二叉树", "遍历", "递归"]',
            "common_errors": '["遍历顺序混淆", "递归深度错误", "空指针访问"]',
        },
        {
            "course_id": sort_search.id or recursion.id,
            "name": "快速排序",
            "description": "理解快速排序的partition过程和分治思想",
            "difficulty": "进阶",
            "tags": '["排序", "快速排序", "分治"]',
            "common_errors": '["基准选择不当", "递归深度过大", "稳定性误判"]',
        },
    ]
    
    created_count = 0
    for kp_data in knowledge_points_data:
        existing_kp = session.query(KnowledgePoint).filter(
            KnowledgePoint.course_id == kp_data["course_id"],
            KnowledgePoint.name == kp_data["name"]
        ).first()
        if existing_kp:
            print(f"  - 知识点 '{kp_data['name']}' 已存在，跳过")
            continue
        
        kp = KnowledgePoint(**kp_data)
        session.add(kp)
        created_count += 1
    
    if created_count > 0:
        session.commit()
        print(f"  ✓ 已创建 {created_count} 个知识点")
    else:
        print("  无新知识点需要创建")


def seed_knowledge_point_relations(session):
    """填充知识点关系数据"""
    print("填充知识点关系数据...")

    time_complexity = session.query(KnowledgePoint).filter_by(name="时间复杂度分析").first()
    recursion = session.query(KnowledgePoint).filter_by(name="递归三要素").first()
    binary_tree_traversal = session.query(KnowledgePoint).filter_by(name="二叉树遍历").first()

    if not time_complexity or not recursion or not binary_tree_traversal:
        print("  警告：相关知识点不存在，跳过知识点关系填充")
        return

    relations_data = [
        {
            "from_kp_id": recursion.id,
            "to_kp_id": binary_tree_traversal.id,
            "relation_type": "prerequisite",
            "description": "递归思想是理解二叉树递归遍历的基础",
        },
    ]
    
    created_count = 0
    for relation_data in relations_data:
        existing_relation = session.query(KnowledgePointRelation).filter(
            KnowledgePointRelation.from_kp_id == relation_data["from_kp_id"],
            KnowledgePointRelation.to_kp_id == relation_data["to_kp_id"]
        ).first()
        if existing_relation:
            print("  - 知识点关系已存在，跳过")
            continue
        
        relation = KnowledgePointRelation(**relation_data)
        session.add(relation)
        created_count += 1
    
    if created_count > 0:
        session.commit()
        print(f"  ✓ 已创建 {created_count} 个知识点关系")
    else:
        print("  无新知识点关系需要创建")


def seed_badges(session):
    """填充徽章数据"""
    print("填充徽章数据...")
    
    badges_data = [
        {
            "badge_code": "complexity_master",
            "name": "复杂度分析入门",
            "description": "完成时间复杂度分析知识点的学习",
            "icon": "🔧",
            "condition_type": "knowledge_point_completed",
            "condition_value": "时间复杂度分析",
        },
        {
            "badge_code": "recursion_explorer",
            "name": "递归探索者",
            "description": "掌握递归三要素和调用栈基本原理",
            "icon": "🔄",
            "condition_type": "knowledge_point_completed",
            "condition_value": "递归三要素",
        },
        {
            "badge_code": "stack_practitioner",
            "name": "栈应用达人",
            "description": "熟练掌握栈在表达式求值等场景的应用",
            "icon": "📊",
            "condition_type": "knowledge_point_completed",
            "condition_value": "栈的应用",
        },
        {
            "badge_code": "binary_tree_explorer",
            "name": "二叉树探索者",
            "description": "掌握二叉树的基本结构和遍历方法",
            "icon": "🌲",
            "condition_type": "knowledge_point_completed",
            "condition_value": "二叉树遍历",
        },
        {
            "badge_code": "sorting_practitioner",
            "name": "排序算法练习达人",
            "description": "掌握快速排序等经典排序算法",
            "icon": "💻",
            "condition_type": "knowledge_point_completed",
            "condition_value": "快速排序",
        },
        {
            "badge_code": "path_persistent",
            "name": "学习路径坚持者",
            "description": "连续学习达到一定天数",
            "icon": "🚶",
            "condition_type": "consecutive_days",
            "condition_value": "7",
        },
    ]
    
    created_count = 0
    for badge_data in badges_data:
        existing_badge = session.query(Badge).filter_by(badge_code=badge_data["badge_code"]).first()
        if existing_badge:
            print(f"  - 徽章 '{badge_data['badge_code']}' 已存在，跳过")
            continue
        
        badge = Badge(**badge_data)
        session.add(badge)
        created_count += 1
    
    if created_count > 0:
        session.commit()
        print(f"  ✓ 已创建 {created_count} 个徽章")
    else:
        print("  无新徽章需要创建")


def main():
    """运行种子数据填充"""
    print("=" * 50)
    print("开始填充种子数据...")
    print("=" * 50)
    
    # 检查数据库是否已初始化
    inspector = inspect(engine)
    if not inspector.get_table_names():
        print("错误：数据库表尚未创建！请先运行 init_db.py")
        sys.exit(1)
    
    with SessionLocal() as session:
        try:
            seed_users(session)
            seed_courses(session)
            seed_course_relations(session)
            seed_knowledge_points(session)
            seed_knowledge_point_relations(session)
            seed_badges(session)
            
            print("\n" + "=" * 50)
            print("✓ 种子数据填充完成！")
            print("=" * 50)
        except Exception as e:
            session.rollback()
            print(f"\n✗ 种子数据填充失败：{e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    main()
