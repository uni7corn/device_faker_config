import os
import sys

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # Fallback for older Python

REQUIRED_FIELDS = [
    "manufacturer",
    "brand",
    "model"
]

def check_toml_file(filepath, rel_path):
    errors = []
    
    # 1. 检查文件能否正确解析
    try:
        with open(filepath, "rb") as f:
            data = tomllib.load(f)
    except Exception as e:
        return [f"TOML 解析错误: {e}"]
        
    # 2. 检查基本结构：是否包含 [templates] 表
    if "templates" not in data or not isinstance(data["templates"], dict):
        return ["缺少 [templates] 顶级表，或其格式不正确。"]
        
    templates = data["templates"]
    
    # 3. 检查每一个模板实例
    for template_name, template_data in templates.items():
        if not isinstance(template_data, dict):
            errors.append(f"模板 '{template_name}' 的格式不正确，应该是一个表。")
            continue
            
        # 4. 检查必填字段
        for field in REQUIRED_FIELDS:
            if field not in template_data:
                errors.append(f"模板 '{template_name}' 缺少必填字段: '{field}'")
            elif not isinstance(template_data[field], str):
                errors.append(f"模板 '{template_name}' 的字段 '{field}' 必须是字符串类型")
        
        # 5. 检查品牌目录名与内容是否匹配（可选/警告）
        # 路径通常是: templates/<category>/<Brand>/<filename>.toml
        parts = filepath.split(os.sep)
        try:
            brand_folder = parts[-2]
            # 这里可以进行更严格的匹配，但由于有些是 "common/Xiaomi" 而里面是 "redmi"，只做参考
        except IndexError:
            pass

    return errors

def main():
    config_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    templates_dir = os.path.join(config_dir, "templates")
    
    if not os.path.exists(templates_dir):
        print(f"找不到 templates 目录: {templates_dir}")
        sys.exit(1)
        
    has_error = False
    checked_count = 0
    
    print("开始检查 TOML 模板文件...\n")
    
    for root, _, files in os.walk(templates_dir):
        for file in files:
            if file.endswith(".toml"):
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, config_dir)
                checked_count += 1
                
                errors = check_toml_file(filepath, rel_path)
                if errors:
                    has_error = True
                    print(f"❌ {rel_path}:")
                    for err in errors:
                        print(f"  - {err}")
                else:
                    print(f"✅ {rel_path} 验证通过")
                    
    print(f"\n检查完成，共检查了 {checked_count} 个文件。")
    if has_error:
        print("发现错误，请修正！")
        sys.exit(1)
    else:
        print("所有文件均符合要求！ 🎉")
        sys.exit(0)

if __name__ == "__main__":
    main()
