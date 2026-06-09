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
    """填充课程数据"""
    print("填充课程数据...")
    
    courses_data = [
        {
            "course_code": "programming_basics",
            "name": "程序设计基础",
            "description": "学习程序设计的基础知识，包括变量、函数、控制流程等",
            "stage": "入门",
            "positioning": "重点演示",
            "keywords": '["程序设计", "基础", "编程"]',
        },
        {
            "course_code": "data_structures",
            "name": "数据结构与算法",
            "description": "学习常见数据结构和算法，提升编程能力",
            "stage": "进阶",
            "positioning": "课程群支撑",
            "keywords": '["数据结构", "算法", "复杂度"]',
        },
        {
            "course_code": "computer_organization",
            "name": "计算机组成原理",
            "description": "了解计算机硬件组成和工作原理",
            "stage": "进阶",
            "positioning": "课程群支撑",
            "keywords": '["计算机组成", "硬件", "CPU"]',
        },
        {
            "course_code": "operating_system",
            "name": "操作系统",
            "description": "学习操作系统的基本概念和原理",
            "stage": "高级",
            "positioning": "课程群支撑",
            "keywords": '["操作系统", "进程", "内存管理"]',
        },
        {
            "course_code": "computer_network",
            "name": "计算机网络",
            "description": "学习计算机网络的基本原理和协议",
            "stage": "高级",
            "positioning": "课程群支撑",
            "keywords": '["网络", "TCP/IP", "协议"]',
        },
        {
            "course_code": "database_system",
            "name": "数据库系统",
            "description": "学习数据库设计和SQL语言",
            "stage": "进阶",
            "positioning": "课程群支撑",
            "keywords": '["数据库", "SQL", "数据管理"]',
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
    """填充课程关系数据"""
    print("填充课程关系数据...")
    
    # 获取课程
    programming_basics = session.query(Course).filter_by(course_code="programming_basics").first()
    data_structures = session.query(Course).filter_by(course_code="data_structures").first()
    
    if not programming_basics or not data_structures:
        print("  警告：相关课程不存在，跳过课程关系填充")
        return
    
    relations_data = [
        {
            "from_course_id": programming_basics.id,
            "to_course_id": data_structures.id,
            "relation_type": "prerequisite",
            "description": "程序设计基础是数据结构的前置课程",
        },
    ]
    
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
    
    # 获取课程
    programming_basics = session.query(Course).filter_by(course_code="programming_basics").first()
    data_structures = session.query(Course).filter_by(course_code="data_structures").first()
    
    if not programming_basics or not data_structures:
        print("  警告：相关课程不存在，跳过知识点填充")
        return
    
    knowledge_points_data = [
        # 程序设计基础的知识点
        {
            "course_id": programming_basics.id,
            "name": "函数调用",
            "description": "学习函数的定义和调用方法",
            "difficulty": "基础",
            "tags": '["函数", "调用"]',
            "common_errors": '["参数错误", "返回值错误"]',
        },
        {
            "course_id": programming_basics.id,
            "name": "数组边界",
            "description": "理解数组的索引和边界问题",
            "difficulty": "基础",
            "tags": '["数组", "边界"]',
            "common_errors": '["越界访问", "索引错误"]',
        },
        {
            "course_id": programming_basics.id,
            "name": "递归调用栈",
            "description": "理解递归调用的执行过程和调用栈",
            "difficulty": "进阶",
            "tags": '["递归", "调用栈"]',
            "common_errors": '["栈溢出", "递归终止条件错误"]',
        },
        {
            "course_id": programming_basics.id,
            "name": "基础调试",
            "description": "学习基本的调试方法和技巧",
            "difficulty": "基础",
            "tags": '["调试", "错误排查"]',
            "common_errors": '[]',
        },
        # 数据结构与算法的知识点
        {
            "course_id": data_structures.id,
            "name": "二叉树结构",
            "description": "学习二叉树的基本结构和性质",
            "difficulty": "进阶",
            "tags": '["二叉树", "数据结构"]',
            "common_errors": '["空指针访问", "树的高度计算错误"]',
        },
        {
            "course_id": data_structures.id,
            "name": "二叉树遍历",
            "description": "掌握二叉树的前序、中序、后序遍历方法",
            "difficulty": "进阶",
            "tags": '["二叉树", "遍历"]',
            "common_errors": '["递归深度错误", "遍历顺序错误"]',
        },
        {
            "course_id": data_structures.id,
            "name": "递归思想",
            "description": "深入理解递归算法的设计思想",
            "difficulty": "进阶",
            "tags": '["递归", "算法"]',
            "common_errors": '["递归深度过大", "重复计算"]',
        },
        {
            "course_id": data_structures.id,
            "name": "排序算法基础",
            "description": "学习常见的排序算法",
            "difficulty": "进阶",
            "tags": '["排序", "算法"]',
            "common_errors": '["时间复杂度分析错误", "稳定性问题"]',
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
    
    # 获取知识点
    func_call = session.query(KnowledgePoint).filter_by(name="函数调用").first()
    recursion_stack = session.query(KnowledgePoint).filter_by(name="递归调用栈").first()
    binary_tree_traversal = session.query(KnowledgePoint).filter_by(name="二叉树遍历").first()
    
    if not func_call or not recursion_stack or not binary_tree_traversal:
        print("  警告：相关知识点不存在，跳过知识点关系填充")
        return
    
    relations_data = [
        {
            "from_kp_id": func_call.id,
            "to_kp_id": recursion_stack.id,
            "relation_type": "prerequisite",
            "description": "函数调用是理解递归调用栈的基础",
        },
        {
            "from_kp_id": recursion_stack.id,
            "to_kp_id": binary_tree_traversal.id,
            "relation_type": "prerequisite",
            "description": "递归调用栈是理解二叉树递归遍历的基础",
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
            "badge_code": "function_call_intro",
            "name": "函数调用入门",
            "description": "完成函数调用知识点的学习",
            "icon": "🔧",
            "condition_type": "knowledge_point_completed",
            "condition_value": "函数调用",
        },
        {
            "badge_code": "recursion_explorer",
            "name": "递归探索者",
            "description": "掌握递归调用的基本原理",
            "icon": "🔄",
            "condition_type": "knowledge_point_completed",
            "condition_value": "递归调用栈",
        },
        {
            "badge_code": "array_practitioner",
            "name": "数组练习达人",
            "description": "熟练掌握数组相关知识",
            "icon": "📊",
            "condition_type": "knowledge_point_completed",
            "condition_value": "数组边界",
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
            "badge_code": "code_practice_novice",
            "name": "代码实践新手",
            "description": "完成第一次代码练习",
            "icon": "💻",
            "condition_type": "practice_completed",
            "condition_value": "1",
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
