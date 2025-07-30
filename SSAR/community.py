def community_detection(similarity_matrix, resolution):
    import gc
    import logging
    import time
    import igraph as ig
    import numpy as np

    # Get matrix index information
    n = similarity_matrix.shape[0]
    rows, cols = np.triu_indices(n, k=1)  # Upper-triangle indices (k=1 excludes diagonal)
    values = similarity_matrix[rows, cols]

    start_time = time.time()
    logging.info("---Constructing weighted graph...")

    # Build weighted graph using igraph
    G = ig.Graph()
    G.add_vertices(n)  # Add nodes
    G.add_edges(zip(rows, cols))  # Add edges
    G.es['weight'] = values  # Set weights

    del rows, cols, values
    gc.collect()

    logging.info("---Performing Leiden community detection...")

    # Perform community detection using the Leiden algorithm
    partition = G.community_leiden(objective_function='modularity', weights="weight", resolution=resolution)

    end_time = time.time()

    logging.info(f"---Number of clusters: {len(partition)}")
    logging.info("Clustering time consumption: {:.2f} seconds.".format(end_time - start_time))

    return partition