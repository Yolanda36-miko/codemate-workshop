import json
import os
from pathlib import Path


def validate():
    base_dir = Path(__file__).parent.parent / "data" / "resource_library"
    index_path = base_dir / "index.json"
    
    # 检查 index.json 是否存在
    if not index_path.exists():
        print(f"错误：index.json 不存在于 {index_path}")
        return 1
    
    # 检查 index.json 是否能被 JSON 解析
    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"错误：index.json JSON 解析失败 - {e}")
        return 1
    
    # 检查 resources 字段是否存在
    if 'resources' not in data:
        print("错误：index.json 中缺少 resources 字段")
        return 1
    
    resources = data['resources']
    total_count = len(resources)
    missing_files = []
    missing_fields = []
    
    # 定义必填字段
    required_fields = [
        'id', 'title', 'course', 'courseCode', 'topic', 
        'topicCode', 'type', 'difficulty', 'contentPath', 
        'source', 'version', 'updatedAt'
    ]
    
    # 遍历资源，检查字段和文件存在
    for idx, resource in enumerate(resources, 1):
        # 检查必填字段
        missing = [field for field in required_fields if field not in resource]
        if missing:
            missing_fields.append((resource.get('id', f"资源 #{idx}"), missing))
        
        # 检查 contentPath 指向的文件是否存在
        content_path = base_dir / resource.get('contentPath', '')
        if 'contentPath' in resource and not content_path.exists():
            missing_files.append((resource.get('id', f"资源 #{idx}"), str(content_path)))
    
    # 输出统计结果
    print(f"资源总数: {total_count}")
    
    # 输出缺失字段的资源
    if missing_fields:
        print("\n缺失必填字段的资源:")
        for resource_id, fields in missing_fields:
            print(f"  - {resource_id}: 缺少字段 {', '.join(fields)}")
    
    # 输出缺失文件列表
    if missing_files:
        print("\n缺失文件列表:")
        for resource_id, file_path in missing_files:
            print(f"  - {resource_id}: {file_path}")
    
    # 判断是否验证通过
    if missing_fields or missing_files:
        print("\n验证失败")
        return 1
    else:
        print("\n验证通过")
        return 0


if __name__ == "__main__":
    exit(validate())