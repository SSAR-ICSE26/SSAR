import json
import re
from collections import Counter
from pathlib import Path


# 获取ground-truth中的文件列表
def read_gt_file(gt_file_path):
    if gt_file_path is None:
        return None
    # 存储所有文件名
    gt_file = []
    # 读取 JSON 数据
    with open(gt_file_path, 'r') as json_file:
        json_data = json.load(json_file)
        # 遍历第一层结构
        for group in json_data["structure"]:
            for item in group["nested"]:
                if item["@type"] == "item":
                    gt_file.append(item["name"])

    return gt_file

# 编程语言及其文件后缀
LANGUAGE_EXTENSIONS = {
    "Java": {".java"},
    "C/C++": {".c", ".cc", ".h", ".cpp", ".cxx", ".hxx", ".hpp"},
    "Python": {".py"}
}

#  检测编程语言
def detect_language(project_path):
    project_path = Path(project_path)
    extension_count = Counter()

    for file in project_path.rglob("*"):
        if file.is_file():
            extension_count[file.suffix] += 1

    # 统计最多的语言
    language_stats = {lang: sum(extension_count[ext] for ext in exts)
                      for lang, exts in LANGUAGE_EXTENSIONS.items()}

    detected_languages = [lang for lang, count in sorted(language_stats.items(), key=lambda x: -x[1]) if count > 0]

    return detected_languages if detected_languages else ["Unknown"]


#  读取代码文件
def read_code_file(file_path):
    encoding_list = ['utf-8', 'gbk', 'windows-1252', 'ISO-8859-1', 'GB18030', 'GB2312']
    # 如果文件不存在或者无法访问，直接跳过
    if not Path(file_path).exists():
        print(f"文件不存在或无法访问: {file_path}")
        return None, "" # 返回空字符串

    for encoding in encoding_list:
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                return encoding, file.read()
        except (UnicodeDecodeError, OSError) as e:
            continue

    print(f"Unable to read file: {file_path}")
    return None, ""  # 读取失败，返回 None


# 提取Java文件中的package路径
def get_package_name(file_path):
    encoding_list = ['utf-8', 'gbk', 'windows-1252', 'ISO-8859-1', 'GB18030', 'GB2312']
    # 如果文件不存在或者无法访问，直接跳过
    if not Path(file_path).exists():
        print(f"文件不存在或无法访问: {file_path}")
        return None # 返回空字符串

    for encoding in encoding_list:
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                for line in file:
                    match = re.match(r'^\s*package\s+([\w.]+)\s*;', line)
                    if match:
                        package_name = match.group(1) + '.' + Path(file_path).stem if match else None
                        return package_name
        except (UnicodeDecodeError, OSError) as e:
            print(f"读取失败 ({encoding}): {e}")
            continue

    return None  # 读取失败，返回 None