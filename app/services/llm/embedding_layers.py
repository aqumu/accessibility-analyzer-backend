from tensorflow.keras import layers
from app.services.llm.config import CATEGORICAL_VOCABULARIES

EMBEDDING_DIMS = {
    "tag": 16,
    "position": 4,
    "display": 4,
    "textAlign": 4
}


def create_embeddings(categorical_inputs):
    embedding_vectors = []

    for name, input_layer in categorical_inputs.items():
        vocab_size = len(CATEGORICAL_VOCABULARIES[name]) + 1
        embedding_dim = EMBEDDING_DIMS.get(name, 8)

        embedding = layers.Embedding(
            input_dim=vocab_size,
            output_dim=embedding_dim,
            name=f"{name}_embedding"
        )(input_layer)

        embedding_squeezed = layers.Reshape((-1, embedding_dim), name=f"{name}_squeeze")(embedding)

        embedding_vectors.append(embedding_squeezed)

    return embedding_vectors
