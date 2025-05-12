import os
import pytest
from app.predict import load_model
from dotenv import load_dotenv

load_dotenv()

MODEL_PATH = os.getenv("MODEL_PATH")
MODEL2_PATH = os.getenv("MODEL2_PATH")

def test_load_model_1():
    model = load_model(MODEL_PATH)
    assert model is not None
    assert hasattr(model, "predict")

def test_load_model_2():
    model = load_model(MODEL2_PATH)
    assert model is not None
    assert hasattr(model, "predict")

def test_load_model_invalid_path():
    with pytest.raises(Exception):
        load_model("invalid/path/to/model.pkl")
