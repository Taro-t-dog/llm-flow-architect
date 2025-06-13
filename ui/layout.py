import streamlit as st
import os
from core import LLMClient, TaskExtractor, DependencyAnalyzer, YamlGenerator
from .review_panel import render_review_panel

def load_css(file_name):
    """CSSファイルを読み込むヘルパー関数"""
    filepath = os.path.join("ui", file_name)
    try:
        with open(filepath) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"CSSファイルが見つかりません: {file_name}")

def render_main_layout():
    """アプリケーションのメインレイアウトをレンダリングする"""
    load_css("styles.css")
    
    st.title("🪄 Workflow Weaver")
    st.caption("マニュアルや手順書から、実行可能なワークフローを自動生成します。")

    # --- 状態管理とクライアント準備 ---
    provider_key = st.session_state.get("llm_provider", "Gemini").lower()
    session_model_key_name = f"selected_model_{provider_key}"
    selected_model_key = st.session_state.get(session_model_key_name)
    api_key_exists = bool(st.session_state.get(f"api_key_{provider_key}"))

    # --- UIレイアウト ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("1. ドキュメント入力")
        st.session_state.manual_text = st.text_area(
            "ここにマニュアルや手順書を貼り付け",
            height=600,
            key="manual_input",
            help="ここに解析したいテキストを入力してください。"
        )

    with col2:
        # --- ステップの可視化 (st.expander を利用) ---
        
        # ステップ1: タスク抽出
        with st.expander("ステップ1: タスクを抽出する", expanded=True):
            if st.button(
                "▶️ タスクを抽出",
                type="primary",
                use_container_width=True,
                disabled=not api_key_exists,
                key="extract_tasks_button"
            ):
                if not st.session_state.manual_text.strip():
                    st.warning("ドキュメントを入力してください。")
                else:
                    st.session_state.analysis_result = {}
                    st.session_state.generated_yaml = ""
                    with st.spinner("LLMがタスクを抽出中..."):
                        try:
                            client = LLMClient(provider=provider_key, model_key=selected_model_key)
                            extractor = TaskExtractor(client)
                            tasks = extractor.extract(st.session_state.manual_text)
                            st.session_state.extracted_tasks = tasks
                            st.success(f"{len(tasks)}個のタスクを抽出しました。")
                            st.rerun()
                        except Exception as e:
                            st.error(f"タスク抽出エラー: {e}")
            if not api_key_exists:
                st.error("APIキーが設定されていません。サイドバーを確認してください。")

        # ステップ2: 依存関係分析
        tasks_exist = bool(st.session_state.get('extracted_tasks'))
        with st.expander("ステップ2: 依存関係を分析する", expanded=tasks_exist):
            if st.button(
                "▶️ 依存関係を分析",
                use_container_width=True,
                disabled=not tasks_exist or not api_key_exists,
                key="analyze_deps_button"
            ):
                with st.spinner("LLMが要約と依存関係を分析中..."):
                    try:
                        client = LLMClient(provider=provider_key, model_key=selected_model_key)
                        analyzer = DependencyAnalyzer(client)
                        analysis_data = analyzer.analyze(st.session_state.manual_text, st.session_state.extracted_tasks)
                        st.session_state.analysis_result = analysis_data
                        st.success("分析が完了しました。")
                        st.rerun()
                    except Exception as e:
                        st.error(f"分析エラー: {e}")

        # ステップ3: レビューとYAML生成
        analysis_exist = bool(st.session_state.get('analysis_result'))
        with st.expander("ステップ3: レビュー & YAML生成", expanded=analysis_exist):
            generate_yaml_clicked = render_review_panel()

            if generate_yaml_clicked:
                with st.spinner("LLMが最終的なYAMLを生成中..."):
                    try:
                        client = LLMClient(provider=provider_key, model_key=selected_model_key)
                        generator = YamlGenerator(client)
                        tasks_from_analysis = list(st.session_state.analysis_result.keys())
                        yaml_content = generator.generate(
                            document_text=st.session_state.manual_text,
                            tasks=tasks_from_analysis,
                            analysis_result=st.session_state.analysis_result
                        )
                        st.session_state.generated_yaml = yaml_content
                        st.success("ワークフローYAMLの生成が完了しました。")
                        st.rerun()
                    except Exception as e:
                        st.error(f"YAML生成エラー: {e}")

            if st.session_state.get('generated_yaml'):
                st.code(st.session_state.generated_yaml, language="yaml")
                st.download_button(
                    label="📥 YAMLをダウンロード",
                    data=st.session_state.generated_yaml,
                    file_name="workflow.yaml",
                    mime="text/yaml",
                    use_container_width=True,
                    key="download_yaml_button"
                )