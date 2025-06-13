import streamlit as st
from config.models import get_available_models_by_provider, get_model_config, is_free_model

def render_sidebar():
    """APIキー設定などのサイドバーUIをレンダリングする"""
    with st.sidebar:
        st.header("⚙️ 設定")

        st.subheader("LLMプロバイダー")
        # 将来的にモデル選択機能を拡張できるように、まずはプロバイダー選択
        provider = st.selectbox(
            "使用するLLM",
            ("Gemini", "OpenAI"),
            key="llm_provider"
        )
        provider_key = provider.lower()

        st.subheader("🤖 モデル")
        available_models = get_available_models_by_provider(provider_key)
        
        if not available_models:
            st.warning(f"{provider}に対応するモデルが設定されていません。")
            return

        session_model_key = f"selected_model_{provider_key}"
        
        selected_model_key = st.selectbox(
            "使用するモデルを選択",
            options=list(available_models.keys()),
            format_func=lambda key: available_models[key],
            key=session_model_key
        )
        
        # --- 料金情報などを表示する機能を追加 ---
        if selected_model_key:
            config = get_model_config(selected_model_key)
            
            if is_free_model(selected_model_key):
                st.success("💰 無料または無料ティア対象モデルです。")
            else:
                input_cost = config.get('input_cost_per_token', 0) * 1_000_000
                output_cost = config.get('output_cost_per_token', 0) * 1_000_000
                st.info(f"料金: ${input_cost:.2f} / 1M入力トークン")
                st.info(f"料金: ${output_cost:.2f} / 1M出力トークン")

            if 'description' in config:
                st.caption(config['description'])
        
        st.subheader("🔑 APIキー")
        if provider_key == "gemini":
            st.text_input("Gemini API Key", type="password", key="api_key_gemini")
        elif provider_key == "openai":
            st.text_input("OpenAI API Key", type="password", key="api_key_openai")

        st.info("APIキーはセッション中のみ保存され、リロードすると消えます。")