from util import read_code_file
from unixcoder import UniXcoder
import torch
import torch.nn as nn
import torch.nn.functional as F

# 初始化模型
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = UniXcoder("microsoft/unixcoder-base")
model.to(device)


# 编码代码文件
def encode_file(path):
    # 读取文件内容
    _, code = read_code_file(path)

    # Tokenize 文件内容
    tokens_ids = model.tokenize([code], mode="<encoder-only>")[0]  # 获取第一个结果

    # 设置参数
    max_length = 512
    overlap = 256

    # 分割文件为多个段
    segments = [tokens_ids[i:i + max_length] for i in range(0, len(tokens_ids), max_length - overlap)]

    # 将分割的段转化为 tensor 并移动到设备上
    segment_tensors = [torch.tensor([seg], device=device) for seg in segments if len(seg) > 0]

    # 获取每段的编码
    with torch.no_grad():  # 禁用梯度计算
        embeddings = [model(segment)[1].squeeze(0) for segment in segment_tensors]

    # 计算所有段编码的平均值
    mean_embedding = torch.mean(torch.stack(embeddings), dim=0)

    # 注意力池化逻辑
    embeddings_tensor = torch.stack(embeddings)  # Shape: (num_segments, embedding_dim)
    embedding_dim = embeddings_tensor.size(-1)
    attention_layer = nn.Linear(embedding_dim, 1, device=device)  # 定义注意力层
    scores = attention_layer(embeddings_tensor)  # Shape: (num_segments, 1)
    weights = F.softmax(scores, dim=0)  # 归一化权重 Shape: (num_segments, 1)

    # 加权池化
    final_embedding = torch.sum(embeddings_tensor * weights, dim=0)  # Shape: (embedding_dim)
    final_embedding += mean_embedding

    return final_embedding

