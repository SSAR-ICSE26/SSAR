import warnings

warnings.filterwarnings("ignore", category=UserWarning)

import logging

logging.basicConfig(
    format='%(asctime)s.%(msecs)03d %(levelname)s [%(filename)s:%(lineno)4d] : %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO
)

import argparse
import csv
import sys
import numpy as np
import time
import torch

from handler import handle_cpp, handle_java
from util import detect_language
from community import community_detection
from pathlib import Path, PurePath
from encoder import encode_file


def arch_recovery(directory_path, dependency_file_path, gt_file_path, resolution):
    start_time = time.time()

    directory_path = Path(directory_path).resolve()
    project_name = directory_path.name  # 获取项目名
    project_language = detect_language(directory_path)[0]

    output_rsf_path = Path("result") / project_name / f"{project_name}.rsf"  # 聚类输出路径

    logging.info(f"Start Architecture Recovering for: {project_name} [language: {project_language}]")

    embeddings_list = []  # 文件编码
    file_paths_index = {}  # 文件字典 文件名：索引

    HANDLERS = {
        "Java": handle_java,
        "C/C++": handle_cpp
    }
    # 选择对应的语言处理器
    if project_language in HANDLERS:
        file_paths, final_paths = HANDLERS[project_language](gt_file_path, directory_path)
    else:
        logging.error(f"Project language {project_language} is not supported.")
        sys.exit(0)

    total_files = len(file_paths)
    if total_files == 0:
        logging.error("No files found to process.")
        sys.exit(0)


    logging.info("Encoding files:")
    for index, absolute_path in enumerate(file_paths):
        relative_path = absolute_path.relative_to(directory_path)
        file_paths_index[relative_path] = index
        embeddings_list.append(encode_file(absolute_path))  # 对文件编码
        # 输出进度
        progress = (index + 1) / total_files * 100

        print(f"\r{progress:.2f}% ({index + 1}/{total_files})", end="")

    print()
    end_time1 = time.time()
    logging.info("---Encoding time consumption: {:.2f} seconds.".format(end_time1 - start_time))



    logging.info("---Calculating similarity matrix...")
    embeddings_matrix = torch.stack(embeddings_list)  # 将嵌入转换为一个大矩阵，形状为 (num_files, embedding_dim)
    norm_embeddings = torch.nn.functional.normalize(embeddings_matrix, p=2, dim=1)  # 归一化嵌入矩阵

    similarity_matrix = (torch.mm(norm_embeddings, norm_embeddings.t()) + 1) / 2 * 0.5  # (1 + cos) / 2 * 0.5
    similarity_matrix = similarity_matrix.detach().cpu().numpy()  # 将相似度矩阵转换为 numpy 数组
    similarity_matrix = np.around(similarity_matrix, decimals=4)



    logging.info("---Processing dependency...")
    dependency_list = []
    with open(dependency_file_path, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # 跳过标题行
        for row in reader:
            dependency_list.append([Path(row[0]), Path(row[1])])

    file_count = len(file_paths_index)  # 文件数
    dependency_count = 0  # 依赖数

    # 遍历依赖列表
    for dependency in dependency_list:
        # 检查依赖的两个文件是否都在file_paths中
        i = file_paths_index.get(dependency[0])
        j = file_paths_index.get(dependency[1])

        if i is not None and j is not None:
            # 增加依赖计数并更新依赖矩阵
            dependency_count += 1
            similarity_matrix[i, j] += 0.5
            similarity_matrix[j, i] += 0.5


    logging.info(f"---Number of files: {file_count}, Number of dependencies: {dependency_count}")
    logging.info("Similarity matrix adjustment completed.")


    print()
    logging.info(f"Start community detecting [resolution: {resolution}]...")

    partition = community_detection(similarity_matrix, resolution)

    # 创建一个字典来存储按标签分组的文件
    grouped_files_by_label = {}
    # 处理文件所属的社区
    for node, community in enumerate(partition.membership):
        # print(f"File {node} is in community {community}")
        if community not in grouped_files_by_label:
            grouped_files_by_label[community] = []
        # 将文件路径添加到对应的标签列表中
        grouped_files_by_label[community].append(final_paths[node])

    # 创建result文件夹（如果不存在则递归创建）
    path = Path("result") / project_name
    path.mkdir(parents=True, exist_ok=True)

    # 写入rsf文件
    with open(output_rsf_path, 'w') as file:
        for label, files in grouped_files_by_label.items():
            for file_path in files:
                file.write(f"contain {label} {file_path}\n")

    print()
    logging.info(f"Writing result to RSF file: {output_rsf_path.resolve()}")

    end_time = time.time()
    logging.info("All done, total time: {:.2f} seconds.".format(end_time - start_time))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.description = "SSAR: A Novel Software Architecture Recovery Approach Enhancing Accuracy and Scalability"
    parser.add_argument(
        "-g",
        "--gt",
        metavar='',
        help="path to the ground_truth .json file (if not provided, all code files in the project will be analyzed)"
    )
    parser.add_argument(
        "-r",
        "--resolution",
        metavar='',
        help="resolution ( > 1 ) for community detection (if not provided, defaults to 1.05)",
        type=float,
        default=1.05
    )
    parser.add_argument(
        "projectpath",
        help="path to the project"
    )
    parser.add_argument(
        "dependency",
        help="path to the dependency .csv file"
    )
    args = parser.parse_args()

    if not Path(args.projectpath).exists():
        logging.error(f"{args.projectpath} is not a directory!")
        sys.exit(0)

    arch_recovery(args.projectpath, args.dependency, args.gt, args.resolution)
