import os
import sys
import yaml

def check_yaml_safe_markdown(value):
    if isinstance(value, str):
        if "```" in value:
            return False
    elif isinstance(value, dict):
        for v in value.values():
            if not check_yaml_safe_markdown(v):
                return False
    elif isinstance(value, list):
        for item in value:
            if not check_yaml_safe_markdown(item):
                return False
    return True

def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    skill_en_path = os.path.join(root, "SKILL.md")
    skill_zh_path = os.path.join(root, "SKILL.zh-TW.md")

    def get_frontmatter(path):
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        if content.startswith("---"):
            end = content.find("---", 3)
            if end != -1:
                return yaml.safe_load(content[3:end])
        return {}

    en_fm = get_frontmatter(skill_en_path)
    zh_fm = get_frontmatter(skill_zh_path)

    if "name" not in en_fm or "schema_version" not in en_fm:
        print("Error: SKILL.md missing name or schema_version in frontmatter.")
        sys.exit(1)
    if "name" not in zh_fm or "schema_version" not in zh_fm:
        print("Error: SKILL.zh-TW.md missing name or schema_version in frontmatter.")
        sys.exit(1)

    if en_fm["name"] != zh_fm["name"]:
        print("Error: name mismatch between SKILL.md and SKILL.zh-TW.md")
        sys.exit(1)
    if en_fm["schema_version"] != zh_fm["schema_version"]:
        print("Error: schema_version mismatch between SKILL.md and SKILL.zh-TW.md")
        sys.exit(1)

    canon_version = en_fm["schema_version"]

    outputs_dir = os.path.join(root, "examples", "02-intermediate", "steps")
    if not os.path.exists(outputs_dir):
        print("Error: examples/02-intermediate/steps directory missing")
        sys.exit(1)

    for i in range(6):
        step_file = os.path.join(outputs_dir, f"step{i}.yaml")
        if not os.path.exists(step_file):
            print(f"Error: {step_file} missing")
            sys.exit(1)
        with open(step_file, "r", encoding="utf-8") as f:
            try:
                data = yaml.safe_load(f)
            except Exception as e:
                print(f"Error parsing {step_file}: {e}")
                sys.exit(1)

        if str(data.get("step")) != str(i):
            print(f"Error: {step_file} missing or mismatched step: expected {i}, got {data.get('step')}")
            sys.exit(1)
        
        if str(data.get("schema_version")) != str(canon_version):
            print(f"Error: {step_file} schema_version mismatch. Expected {canon_version}, got {data.get('schema_version')}")
            sys.exit(1)
        
        if not check_yaml_safe_markdown(data):
            print(f"Error: {step_file} contains fenced code blocks (```) inside YAML string. This violates the YAML-safe profile.")
            sys.exit(1)

    print("Success: Repository validation passed.")

if __name__ == "__main__":
    main()
