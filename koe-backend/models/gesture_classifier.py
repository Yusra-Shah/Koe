import json
import os
import pickle
from pathlib import Path

import numpy as np

MODEL_DIR = Path(os.getenv("MODEL_DIR", Path(__file__).parent.parent.parent / "model" / "koe_models"))

_interpreter = None
_label_encoder = None
_x_mean = None
_x_std = None
_config = None


def _load_assets():
    global _interpreter, _label_encoder, _x_mean, _x_std, _config

    if _interpreter is not None:
        return

    config_path = MODEL_DIR / "koe_model_config.json"
    with open(config_path) as f:
        _config = json.load(f)

    with open(MODEL_DIR / "label_encoder.pkl", "rb") as f:
        _label_encoder = pickle.load(f)

    _x_mean = np.load(MODEL_DIR / "X_mean.npy")
    _x_std = np.load(MODEL_DIR / "X_std.npy")

    tflite_path = MODEL_DIR / "koe_mlp.tflite"

    try:
        import tensorflow as tf
        _interpreter = tf.lite.Interpreter(model_path=str(tflite_path))
    except ImportError:
        from ai_edge_litert.interpreter import Interpreter
        _interpreter = Interpreter(model_path=str(tflite_path))

    _interpreter.allocate_tensors()


def _landmarks_to_features(landmarks: list[list[dict]]) -> np.ndarray:
    """Flatten first hand's 21 landmarks into a 63-feature vector."""
    hand = landmarks[0]
    features = []
    for point in hand[:21]:
        features.extend([point["x"], point["y"], point["z"]])
    arr = np.array(features, dtype=np.float32)
    if len(arr) < 63:
        arr = np.pad(arr, (0, 63 - len(arr)))
    return arr[:63]


def classify(landmarks: list[list[dict]]) -> tuple[str, float]:
    """
    Run TFLite MLP inference on MediaPipe landmarks.
    Returns (sign_label, confidence).
    """
    _load_assets()

    features = _landmarks_to_features(landmarks)
    features = np.nan_to_num(features, nan=0.0)
    normalized = (features - _x_mean) / (_x_std + 1e-8)
    inp = normalized.reshape(1, 63).astype(np.float32)

    input_details = _interpreter.get_input_details()
    output_details = _interpreter.get_output_details()

    _interpreter.set_tensor(input_details[0]["index"], inp)
    _interpreter.invoke()

    probs = _interpreter.get_tensor(output_details[0]["index"])[0]
    predicted_idx = int(np.argmax(probs))
    confidence = float(probs[predicted_idx])

    label = _label_encoder.classes_[predicted_idx]
    return label, confidence


def get_config() -> dict:
    _load_assets()
    return _config
