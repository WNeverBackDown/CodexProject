import json
import os
import shutil


def ensure_runtime_files(root):
    data_dir = os.path.join(root, "data")
    config_dir = os.path.join(root, "config")
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(config_dir, exist_ok=True)

    inbox_path = os.path.join(data_dir, "inbox.txt")
    if not os.path.exists(inbox_path):
        open(inbox_path, "a", encoding="utf-8").close()

    rules_path = os.path.join(config_dir, "rules.json")
    default_rules_path = os.path.join(config_dir, "default_rules.json")
    if not os.path.exists(rules_path) and os.path.exists(default_rules_path):
        shutil.copyfile(default_rules_path, rules_path)


def read_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp_path = path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    os.replace(tmp_path, path)


def append_jsonl(path, item):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(item, ensure_ascii=False, sort_keys=True) + "\n")


def read_jsonl(path, limit=100):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as handle:
        lines = [line.strip() for line in handle if line.strip()]
    if limit:
        lines = lines[-limit:]
    result = []
    for line in lines:
        try:
            result.append(json.loads(line))
        except ValueError:
            continue
    return result


def truncate(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8").close()
