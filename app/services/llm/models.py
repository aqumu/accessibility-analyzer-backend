from tensorflow import keras
from tensorflow.keras import layers
import os
from app.services.llm.input_layers import create_model_inputs
from app.services.llm.embedding_layers import create_embeddings
from app.services.llm.transformer_block import create_transformer_block
from app.services.llm.config import FEATURE_MAPPING

TEXT_VECTOR_SIZE = 512
NUMERIC_VECTOR_SIZE = len(FEATURE_MAPPING["numeric_scalar"]) + 1
COLOR_VECTOR_SIZE = len(FEATURE_MAPPING["color"]) * 3


def create_usability_model(transformer_num_heads=8, transformer_key_dim=64, transformer_ffn_dim=128):
    all_inputs = create_model_inputs(
        text_vector_size=TEXT_VECTOR_SIZE,
        numeric_vector_size=NUMERIC_VECTOR_SIZE,
        color_vector_size=COLOR_VECTOR_SIZE
    )

    categorical_inputs = {k: v for k, v in all_inputs.items() if k not in ["text", "numeric", "color"]}
    embedding_vectors = create_embeddings(categorical_inputs)

    element_feature_tensors = [
                                  all_inputs["text"],
                                  all_inputs["numeric"],
                                  all_inputs["color"]
                              ] + embedding_vectors

    mega_vector = layers.Concatenate(axis=-1, name="mega_vector_concat")(element_feature_tensors)

    masked_vector = layers.Masking(mask_value=0.0)(mega_vector)

    transformer_output = create_transformer_block(
        inputs=masked_vector,
        num_heads=transformer_num_heads,
        key_dim=transformer_key_dim,
        ffn_dim=transformer_ffn_dim
    )

    page_vector = layers.GlobalAveragePooling1D(name="page_vector")(transformer_output)

    x = layers.Dense(64, activation='relu')(page_vector)
    x = layers.Dropout(0.3)(x)

    output_score = layers.Dense(1, activation='linear', name='usability_score')(x)

    model = keras.Model(
        inputs=list(all_inputs.values()),
        outputs=output_score,
        name="UI_UX_Evaluator"
    )

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=1e-4),
        loss="mean_squared_error",
        metrics=["mean_absolute_error"]
    )

    return model


if __name__ == "__main__":
    model = create_usability_model()
    model.summary()

    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    try:
        model_plot_path = os.path.join(PROJECT_ROOT, 'model_architecture.png')
        keras.utils.plot_model(model, to_file=model_plot_path, show_shapes=True, expand_nested=True)
    except Exception as e:
        pass
