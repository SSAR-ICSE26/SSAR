from pathlib import Path

from util import LANGUAGE_EXTENSIONS, read_gt_file, get_package_name


def handle_java(gt_file_path, directory_path):
    file_paths = []
    package_paths = []
    suffix = LANGUAGE_EXTENSIONS["Java"]
    gt_file = read_gt_file(gt_file_path)

    for path in Path(directory_path).rglob("*"):
        if path.is_file() and path.suffix in suffix:  # Only process files with the corresponding extension
            package_name = get_package_name(path)  # Read package info from the Java file; if the package is in gtfile, add the file's absolute path to the list
            if gt_file is None or package_name in gt_file:
                absolute_path = path.resolve()
                file_paths.append(absolute_path)  # Store absolute path
                package_paths.append(package_name)  # Store package path; save package name in the list so there's no need to process the rsf file later

    return file_paths, package_paths


def handle_cpp(gt_file_path, directory_path):
    file_paths = []
    relative_paths = []
    suffix = LANGUAGE_EXTENSIONS["C/C++"]
    gt_file = read_gt_file(gt_file_path)

    for path in Path(directory_path).rglob("*"):
        if path.is_file() and path.suffix in suffix:  # Only process files with the corresponding extension
            relative_path = path.relative_to(directory_path).as_posix()
            if gt_file is None or relative_path in gt_file:  # Use Linux-style relative path
                file_paths.append(path.resolve())  # Store absolute path
                relative_paths.append(relative_path)  # Store relative path

    return file_paths, relative_paths