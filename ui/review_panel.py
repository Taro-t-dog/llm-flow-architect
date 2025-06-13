import streamlit as st

# --- データ整合性を保つためのヘルパー関数群 ---

# ui/review_panel.py のヘルパー関数 (これを適用してほしい)

def handle_task_rename(old_name: str, new_name: str):
    """タスク名変更時に、分析結果データも追従"""
    # エイリアスで短くする
    res = st.session_state.analysis_result
    
    # 1. キーの名前を変更
    if old_name in res:
        # popで古いキーのデータを取得し、新しいキーで設定
        res[new_name] = res.pop(old_name)
    
    # 2. 他のタスクの依存先リスト内の名前も変更
    for task_key in res:
        # 修正: 正しく "dependencies" キーの中のリストを参照する
        if old_name in res[task_key].get("dependencies", []):
            # 修正: リスト内包表記で新しいリストを作成し、"dependencies" に再設定
            res[task_key]["dependencies"] = [
                new_name if dep == old_name else dep 
                for dep in res[task_key]["dependencies"]
            ]

def handle_task_delete(task_to_delete: str):
    """タスク削除時に、分析結果データからも削除"""
    # エイリアスで短くする
    res = st.session_state.analysis_result
    
    # 1. キーを削除
    if task_to_delete in res:
        del res[task_to_delete]
        
    # 2. 他のタスクの依存先リストからも削除
    for task_key in res:
        # 修正: 正しく "dependencies" キーの中のリストを参照し、存在確認
        if task_to_delete in res[task_key].get("dependencies", []):
            # 修正: リストから要素を削除
            res[task_key]["dependencies"].remove(task_to_delete)

# ----------------------------------------------------

def render_review_panel() -> bool:
    """
    手動レビューUIをレンダリングする。YAML生成ボタンが押されたかをbool値で返す。
    """
    analysis_result = st.session_state.get('analysis_result')
    if not analysis_result:
        st.info("ステップ2「依存関係を分析」を実行すると、ここにレビューパネルが表示されます。")
        return False

    st.markdown("##### タスクリストと依存関係の編集")
    st.caption("タスク名、タスクの要約、依存先を自由に編集できます。")
    
    tasks_copy = list(analysis_result.keys())
    task_to_delete = None

    # --- 編集UI ---
    for task_name in tasks_copy:
        with st.container(border=True):
            col1, col2 = st.columns([0.85, 0.15])
            with col1:
                new_task_name = st.text_input(
                    "タスク名", value=task_name, key=f"task_edit_{task_name}", label_visibility="collapsed"
                )
                if new_task_name != task_name and new_task_name: # 空の名前への変更は無視
                    handle_task_rename(task_name, new_task_name)
                    st.rerun()

            with col2:
                if st.button("🗑️", key=f"delete_task_{task_name}", help="このタスクを削除", use_container_width=True):
                    task_to_delete = task_name
            
            # タスク要約の編集
            current_summary = analysis_result[task_name].get("summary", "")
            new_summary = st.text_area(
                "タスクの要約（プロンプトの元）",
                value=current_summary,
                key=f"summary_edit_{task_name}",
                height=100
            )
            if new_summary != current_summary:
                analysis_result[task_name]["summary"] = new_summary
            
            # 依存関係の編集
            available_deps = [t for t in tasks_copy if t != task_name]
            current_deps = analysis_result[task_name].get("dependencies", [])
            selected_deps = st.multiselect(
                "依存先:",
                options=available_deps,
                default=current_deps,
                key=f"deps_edit_{task_name}",
                help=f"`{task_name}`を実行する前に完了している必要があるタスクを選択"
            )
            analysis_result[task_name]["dependencies"] = selected_deps

    if task_to_delete:
        handle_task_delete(task_to_delete)
        st.rerun()

    if st.button("➕ 新しいタスクを追加", use_container_width=True, key="add_new_task_button"):
        new_task_name = f"new_task_{len(tasks_copy) + 1}"
        analysis_result[new_task_name] = {"summary": "新しいタスクの説明をここに入力します。", "dependencies": []}
        st.rerun()
    
    st.markdown("---")

    return st.button(
        "▶️ ワークフローYAMLを生成",
        type="primary",
        use_container_width=True,
        key="generate_yaml_button"
    )