"""
モデル設定と料金情報
"""

MODEL_CONFIGS = {
    # Gemini Models
    "gemini-2.0-flash-exp": {
        "name": "Gemini 2.0 Flash",
        "model_id": "gemini-2.0-flash-exp",
        "api_provider": "gemini", # プロバイダーを明記
        "input_cost_per_token": 0.0000001,
        "output_cost_per_token": 0.0000004,
        "description": "Fast, cost-efficient model with 1M context window",
        "context_window": 1000000,
        "free_tier": True
    },
    # OpenAI Models
    "gpt-4.1": {
        "name": "gpt-4.1 (OpenAI)",
        "model_id": "gpt-4.1",
        "api_provider": "openai",
        "input_cost_per_token": 0.000002,  # $2.00 / 1M tokens
        "output_cost_per_token": 0.000008, # $8.00 / 1M tokens
        "description": "OpenAI's GPT-4.1 model.",
        "context_window": 1000000,
        "free_tier": False
    },
    # 👈 [追加] 新しいモデル gpt-4.1-mini
    "gpt-4.1-mini": {
        "name": "gpt-4.1-mini (OpenAI)",
        "model_id": "gpt-4.1-mini",
        "api_provider": "openai",
        "input_cost_per_token": 0.0000004,  # $0.40 / 1M tokens
        "output_cost_per_token": 0.0000016, # $1.60 / 1M tokens
        "description": "OpenAI's cost-efficient GPT-4.1-mini model.",
        "context_window": 1047576, # 一般的なminiモデルのコンテキスト長に修正（必要に応じて変更してください）
        "free_tier": False
    },
}

def get_model_config(model_key: str) -> dict:
    """指定されたモデルキーの設定を返す。見つからない場合はデフォルトを返す。"""
    if model_key is None or model_key not in MODEL_CONFIGS:
        # デフォルトとして、リストの最初のモデルを返す
        return list(MODEL_CONFIGS.values())[0]
    return MODEL_CONFIGS[model_key]

def get_available_models_by_provider(provider: str) -> dict:
    """指定されたプロバイダーで利用可能なモデルの辞書 {key: display_name} を返す。"""
    return {
        key: config["name"]
        for key, config in MODEL_CONFIGS.items()
        if config["api_provider"] == provider
    }

def is_free_model(model_key: str) -> bool:
    """モデルが無料かどうかを判定"""
    config = get_model_config(model_key)
    if not config:
        return False
    if 'free_tier' in config:
        return config['free_tier']
    # コストが0の場合も無料と見なす
    return config.get('input_cost_per_token', 1.0) == 0 and config.get('output_cost_per_token', 1.0) == 0
