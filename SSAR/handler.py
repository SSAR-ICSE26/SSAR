from pathlib import Path

from util import LANGUAGE_EXTENSIONS, read_gt_file, get_package_name


def handle_java(gt_file_path, directory_path):
    file_paths = []
    package_paths = []
    suffix = LANGUAGE_EXTENSIONS["Java"]
    gt_file = read_gt_file(gt_file_path)

    for path in Path(directory_path).rglob("*"):
        if path.is_file() and path.suffix in suffix:  # 只处理对应后缀名的文件
            package_name = get_package_name(path)  # 读取java文件中的package信息，如果package内容在gtfile中，则将这个文件的绝对路径加入列表
            if gt_file is None or package_name in gt_file:
                absolute_path = path.resolve()
                file_paths.append(absolute_path)  # 存储绝对路径
                package_paths.append(package_name)  # 存储包路径 把包名存入列表，就不用再对rsf文件进行处理

    return file_paths, package_paths


def handle_cpp(gt_file_path, directory_path):
    file_paths = []
    relative_paths = []
    suffix = LANGUAGE_EXTENSIONS["C/C++"]
    gt_file = read_gt_file(gt_file_path)

    for path in Path(directory_path).rglob("*"):
        if path.is_file() and path.suffix in suffix:  # 只处理对应后缀名的文件
            relative_path = path.relative_to(directory_path).as_posix()
            if gt_file is None or relative_path in gt_file:  # 设置为linux风格的相对路径
                file_paths.append(path.resolve())  # 存储绝对路径
                relative_paths.append(relative_path)  # 存储相对路径

    return file_paths, relative_paths
