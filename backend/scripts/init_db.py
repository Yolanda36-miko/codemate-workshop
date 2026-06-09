#!/usr/bin/env python3
"""
数据库初始化脚本
"""
import os
import sys
import argparse
import subprocess

# 添加 backend 目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
sys.path.insert(0, backend_dir)

# 确保路径正确设置后再导入数据库模块
os.chdir(backend_dir)


def init_db(reset=False, seed=False):
    """
    初始化数据库
    :param reset: 是否删除现有数据库重新创建
    :param seed: 是否写入种子数据
    """
    db_path = os.path.join(backend_dir, "codemate.db")
    
    if reset:
        print("警告：即将删除现有数据库文件...")
        if os.path.exists(db_path):
            try:
                os.remove(db_path)
                print(f"已删除现有数据库文件: {db_path}")
            except Exception as e:
                print(f"删除数据库文件失败: {e}")
                sys.exit(1)
    
    # 导入模型和数据库配置
    from database import engine, Base
    from models import (
        User, StudentProfile, ProfileConversation,
        Course, CourseRelation,
        KnowledgePoint, KnowledgePointRelation,
        Resource, UserResourcePackage,
        LearningPath, LearningPathNode, PathNodeResource,
        Assessment, AssessmentAnswer,
        GrowthRecord, Badge, UserBadge
    )
    
    # 创建所有表
    print("创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成")
    
    # 如果需要写入种子数据
    if seed:
        print("写入种子数据...")
        try:
            # 调用 seed_db.py
            seed_script_path = os.path.join(current_dir, "seed_db.py")
            subprocess.run([sys.executable, seed_script_path], check=True)
            print("种子数据写入完成")
        except subprocess.CalledProcessError as e:
            print(f"写入种子数据失败: {e}")
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="数据库初始化脚本")
    parser.add_argument("--seed", action="store_true", help="创建表后写入种子数据")
    parser.add_argument("--reset", action="store_true", help="删除现有数据库后重新创建（危险操作）")
    
    args = parser.parse_args()
    
    init_db(reset=args.reset, seed=args.seed)


if __name__ == "__main__":
    main()
