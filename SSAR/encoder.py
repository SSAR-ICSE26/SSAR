from util import read_code_file
from unixcoder import UniXcoder
import torch
import torch.nn as nn
import torch.nn.functional as F

# Initialize the model
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = UniXcoder("microsoft/unixcoder-base")
model.to(device)


# Encode a code file
def encode_file(path):
    # Read file content
    _, code = read_code_file(path)

    # Tokenize the file content
    tokens_ids = model.tokenize([code], mode="<encoder-only>")[0]  # Get the first result

    # Set parameters
    max_length = 512
    overlap = 256

    # Split the file into multiple segments
    segments = [tokens_ids[i:i + max_length] for i in range(0, len(tokens_ids), max_length - overlap)]

    # Convert segments into tensors and move to device
    segment_tensors = [torch.tensor([seg], device=device) for seg in segments if len(seg) > 0]

    # Get embeddings for each segment
    with torch.no_grad():  # Disable gradient computation
        embeddings = [model(segment)[1].squeeze(0) for segment in segment_tensors]

    # Compute the average of all segment embeddings
    mean_embedding = torch.mean(torch.stack(embeddings), dim=0)

    # Attention pooling logic
    embeddings_tensor = torch.stack(embeddings)  # Shape: (num_segments, embedding_dim)
    embedding_dim = embeddings_tensor.size(-1)
    attention_layer = nn.Linear(embedding_dim, 1, device=device)  # Define attention layer
    scores = attention_layer(embeddings_tensor)  # Shape: (num_segments, 1)
    weights = F.softmax(scores, dim=0)  # Normalize weights Shape: (num_segments, 1)

    # Weighted pooling
    final_embedding = torch.sum(embeddings_tensor * weights, dim=0)  # Shape: (embedding_dim)
    final_embedding += mean_embedding

    return final_embedding