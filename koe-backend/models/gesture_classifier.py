import json
import os
import pickle
import tempfile
from pathlib import Path

import numpy as np

MODEL_DIR = Path(os.getenv("MODEL_DIR", Path(__file__).parent.parent.parent / "model" / "koe_models"))
MODEL_BUCKET = os.getenv("MODEL_BUCKET", "")

# Files to fetch from Cloud Storage when MODEL_BUCKET is set
_BUCKET_FILES = [
    "koe_mlp.tflite",
    "koe_model_config.json",
    "label_encoder.pkl",
    "X_mean.npy",
    "X_std.npy",
]


def _download_from_gcs(bucket_name: str, dest_dir: Path) -> None:
    """Download model assets from Cloud Storage if not already present locally."""
    from google.cloud import storage
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    dest_dir.mkdir(parents=True, exist_ok=True)
    for filename in _BUCKET_FILES:
        dest = dest_dir / filename
        if not dest.exists():
            blob = bucket.blob(f"koe_models/{filename}")
            blob.download_to_filename(str(dest))


def _ensure_model_dir() -> Path:
    """Return local model directory, downloading from GCS if needed."""
    if MODEL_BUCKET and not (MODEL_DIR / "koe_mlp.tflite").exists():
        cache_dir = Path(tempfile.gettempdir()) / "koe_models"
        _download_from_gcs(MODEL_BUCKET, cache_dir)
        return cache_dir
    return MODEL_DIR

_interpreter = None
_label_encoder = None
_x_mean = None
_x_std = None
_config = None


def _load_assets():
    global _interpreter, _label_encoder, _x_mean, _x_std, _config

    if _interpreter is not None:
        return

    model_dir = _ensure_model_dir()

    config_path = model_dir / "koe_model_config.json"
    with open(config_path) as f:
        _config = json.load(f)

    with open(model_dir / "label_encoder.pkl", "rb") as f:
        _label_encoder = pickle.load(f)

    _x_mean = np.load(model_dir / "X_mean.npy")
    _x_std = np.load(model_dir / "X_std.npy")

    tflite_path = model_dir / "koe_mlp.tflite"

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
