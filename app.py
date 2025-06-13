# app.py (修正後)
import streamlit as st
import sys # ◀ sysをインポート
import os  # ◀ osをインポート

# --- プロジェクトルートをPythonパスに追加 ---
# このファイルの絶対パスを取得
current_file_path = os.path.abspath(__file__)
project_root = os.path.dirname(current_file_path)
if project_root not in sys.path:
    sys.path.insert(0, project_root)
# -----------------------------------------

# ↓↓↓ この処理は、パス追加の後に行う ↓↓↓
from ui.layout import render_main_layout
from ui.sidebar import render_sidebar

st.set_page_config(page_title="LLM FLOW ARCHITECT", layout="wide")

# セッションステートの初期化
if 'api_key_gemini' not in st.session_state:
    st.session_state.api_key_gemini = ""
if 'api_key_openai' not in st.session_state:
    st.session_state.api_key_openai = ""
if 'llm_provider' not in st.session_state:
    st.session_state.llm_provider = "Gemini"
if 'manual_text' not in st.session_state:
    st.session_state.manual_text = ""
if 'extracted_tasks' not in st.session_state:
    st.session_state.extracted_tasks = []
if 'dependencies' not in st.session_state:
    st.session_state.dependencies = {} # ◀ エラーの原因だったキーを空の辞書で初期化
if 'generated_yaml' not in st.session_state:
    st.session_state.generated_yaml = ""

render_sidebar()
render_main_layout()