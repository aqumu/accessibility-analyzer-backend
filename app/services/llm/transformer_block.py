from tensorflow.keras import layers


def create_transformer_block(inputs, num_heads, key_dim, ffn_dim, dropout_rate=0.1):
    attention_output = layers.MultiHeadAttention(
        num_heads=num_heads, key_dim=key_dim
    )(query=inputs, value=inputs, key=inputs)
    attention_output = layers.Dropout(dropout_rate)(attention_output)

    norm_output_1 = layers.LayerNormalization(epsilon=1e-6)(inputs + attention_output)

    ffn_output = layers.Dense(ffn_dim, activation="relu")(norm_output_1)
    ffn_output = layers.Dense(inputs.shape[-1])(ffn_output)
    ffn_output = layers.Dropout(dropout_rate)(ffn_output)

    norm_output_2 = layers.LayerNormalization(epsilon=1e-6)(norm_output_1 + ffn_output)

    return norm_output_2
