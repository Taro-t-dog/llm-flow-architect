# config/__init__.py (修正案)

"""
configパッケージの初期化ファイル。
外部からインポート可能なオブジェクトを定義する。
"""
# models.pyファイルから直接インポート
from .models import (
    MODEL_CONFIGS,
    get_model_config,
    get_available_models_by_provider,
    is_free_model
)

# このパッケージから何をインポートできるかを明示するリスト
__all__ = [
    "MODEL_CONFIGS",
    "get_model_config",
    "get_available_models_by_provider",
    "is_free_model"
]