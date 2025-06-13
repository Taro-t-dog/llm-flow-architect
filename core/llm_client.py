import os
import streamlit as st
from openai import OpenAI
import google.generativeai as genai
from typing import Literal
from config.models import get_model_config

class LLMClient:
    # 修正: model_key を引数として正しく受け取る
    def __init__(self, provider: Literal['gemini', 'openai'], model_key: str):
        self.provider = provider
        
        # 修正: 属性を定義する順番を整理。設定情報を先に確定させる。
        self.model_config = get_model_config(model_key)
        if not self.model_config:
            raise ValueError(f"モデル '{model_key}' の設定が見つかりません。")
        
        self.model_id = self.model_config.get('model_id')
        if not self.model_id:
             raise ValueError(f"モデル '{model_key}' の設定に 'model_id' がありません。")

        # 最後にクライアントを初期化
        self.client = self._initialize_client()

    def _initialize_client(self):
        """APIキーを使って各LLMのクライアントを初期化する"""
        if self.provider == 'openai':
            api_key = st.session_state.get("api_key_openai")
            if not api_key:
                # エラーを発生させるのではなく、Noneを返して呼び出し元で処理させる
                return None
            return OpenAI(api_key=api_key)
        
        elif self.provider == 'gemini':
            api_key = st.session_state.get("api_key_gemini")
            if not api_key:
                return None
            try:
                genai.configure(api_key=api_key)
                return genai.GenerativeModel(self.model_id)
            except Exception as e:
                print(f"Error initializing Gemini client: {e}")
                return None
        return None

    def execute_prompt(self, prompt: str) -> str:
        """プロンプトを実行し、結果のテキストを返す"""
        if not self.client:
            raise ConnectionError("LLMクライアントが初期化されていません。サイドバーでAPIキーとモデルを正しく設定してください。")

        try:
            if self.provider == 'openai':
                response = self.client.chat.completions.create(
                    model=self.model_id,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.choices[0].message.content.strip()

            elif self.provider == 'gemini':
                response = self.client.generate_content(prompt)
                return response.text.strip()
                
        except Exception as e:
            raise RuntimeError(f"API実行エラー: {e}") from e
        return ""

# この関数は他の場所に移動しても良い
def load_prompt_template(filename: str) -> str:
    filepath = os.path.join("prompts", filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise