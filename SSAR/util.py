import json
import re
from collections import Counter
from pathlib import Path


# Get the list of files from ground-truth
def read_gt_file(gt_file_path):
    if gt_file_path is None:
        return None
    # Store all filenames
    gt_file = []
    # Read JSON data
    with open(gt_file_path, 'r') as json_file:
        json_data = json.load(json_file)
        # Traverse the first-level structure
        for group in json_data["structure"]:
            for item in group["nested"]:
                if item["@type"] == "item":
                    gt_file.append(item["name"])

    return gt_file

# Programming languages and their file extensions
LANGUAGE_EXTENSIONS = {
    "Java": {".java"},
    "C/C++": {".c", ".cc", ".h", ".cpp", ".cxx", ".hxx", ".hpp"},
    "Python": {".py"}
}

# Detect programming language
def detect_language(project_path):
    project_path = Path(project_path)
    extension_count = Counter()

    for file in project_path.rglob("*"):
        if file.is_file():
            extension_count[file.suffix] += 1

    # Count the most frequent language
    language_stats = {lang: sum(extension_count[ext] for ext in exts)
                      for lang, exts in LANGUAGE_EXTENSIONS.items()}

    detected_languages = [lang for lang, count in sorted(language_stats.items(), key=lambda x: -x[1]) if count > 0]

    return detected_languages if detected_languages else ["Unknown"]


# Read code file
def read_code_file(file_path):
    encoding_list = ['utf-8', 'gbk', 'windows-1252', 'ISO-8859-1', 'GB18030', 'GB2312']
    # If the file does not exist or is inaccessible, skip it directly
    if not Path(file_path).exists():
        print(f"File does not exist or is inaccessible: {file_path}")
        return None, ""  # Return empty string

    for encoding in encoding_list:
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                return encoding, file.read()
        except (UnicodeDecodeError, OSError) as e:
            continue

    print(f"Unable to read file: {file_path}")
    return None, ""  # Return None on failure


# Extract package path from Java file
def get_package_name(file_path):
    encoding_list = ['utf-8', 'gbk', 'windows-1252', 'ISO-8859-1', 'GB18030', 'GB2312']
    # If the file does not exist or is inaccessible, skip it directly
    if not Path(file_path).exists():
        print(f"File does not exist or is inaccessible: {file_path}")
        return None  # Return None

    for encoding in encoding_list:
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                for line in file:
                    match = re.match(r'^\s*package\s+([\w.]+)\s*;', line)
                    if match:
                        package_name = match.group(1) + '.' + Path(file_path).stem if match else None
                        return package_name
        except (UnicodeDecodeError, OSError) as e:
            print(f"Failed to read ({encoding}): {e}")
            continue

    return None  # Return None on failure