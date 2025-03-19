def community_detection(similarity_matrix, resolution):
    import gc
    import logging
    import time
    import igraph as ig
    import numpy as np

    # 获取矩阵索引信息
    n = similarity_matrix.shape[0]
    rows, cols = np.triu_indices(n, k=1)  # 上三角索引（k=1 表示不包括对角线）
    values = similarity_matrix[rows, cols]

    start_time = time.time()
    logging.info("---Constructing weighted graph...")

    # 使用 igraph 构建加权图
    G = ig.Graph()
    G.add_vertices(n)  # 添加节点
    G.add_edges(zip(rows, cols))  # 添加边
    G.es['weight'] = values  # 设置权重

    del rows, cols, values
    gc.collect()




    logging.info(f"---Performing Leiden community detection...")

    # 使用 Leiden 算法进行社区检测
    partition = G.community_leiden(objective_function='modularity', weights="weight", resolution=resolution)

    end_time = time.time()


    logging.info(f"---Number of clusters: {len(partition)}")
    logging.info("Clustering time consumption: {:.2f} seconds.".format(end_time - start_time))

    return partition