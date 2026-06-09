"""
数据库检查脚本
用于快速检查数据库中的关键数据量，用于验收
"""
import sys
import os

# 添加父目录到路径以便导入
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal, engine
from models import (
    User, Course, KnowledgePoint,
    CourseRelation, KnowledgePointRelation, Badge
)
from sqlalchemy import inspect


def check_db():
    """检查数据库数据"""
    print("数据库数据检查...")
    
    # 检查数据库文件是否存在
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "codemate.db")
    if not os.path.exists(db_path):
        print("错误：数据库文件不存在！请先运行 init_db.py")
        sys.exit(1)
    
    # 检查表是否已创建
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    if not tables:
        print("错误：数据库表尚未创建！请先运行 init_db.py")
        sys.exit(1)
    
    with SessionLocal() as session:
        try:
            # 统计各类数据
            users_count = session.query(User).count()
            courses_count = session.query(Course).count()
            knowledge_points_count = session.query(KnowledgePoint).count()
            course_relations_count = session.query(CourseRelation).count()
            knowledge_point_relations_count = session.query(KnowledgePointRelation).count()
            badges_count = session.query(Badge).count()
            
            # 输出结果
            print(f"users: {users_count}")
            print(f"courses: {courses_count}")
            print(f"knowledge_points: {knowledge_points_count}")
            print(f"course_relations: {course_relations_count}")
            print(f"knowledge_point_relations: {knowledge_point_relations_count}")
            print(f"badges: {badges_count}")
            
            # 验证是否满足要求
            print("\n验证结果：")
            checks = [
                ("users >= 1", users_count >= 1),
                ("courses >= 6", courses_count >= 6),
                ("knowledge_points >= 8", knowledge_points_count >= 8),
                ("course_relations >= 1", course_relations_count >= 1),
                ("knowledge_point_relations >= 1", knowledge_point_relations_count >= 1),
                ("badges >= 6", badges_count >= 6),
            ]
            
            all_passed = True
            for check, passed in checks:
                status = "✓ 通过" if passed else "✗ 未通过"
                print(f"  {check}: {status}")
                if not passed:
                    all_passed = False
            
            if all_passed:
                print("\n✓ 所有检查项均已通过！")
            else:
                print("\n✗ 部分检查项未通过，请检查数据填充情况")
                sys.exit(1)
                
        except Exception as e:
            print(f"错误：{e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    check_db()
