from .llm_client import LLMClient, load_prompt_template
from typing import List

class TaskExtractor:
    def __init__(self, llm_client: LLMClient):
        self.client = llm_client
        self.prompt_template = load_prompt_template("extract_tasks.prompt")

    def extract(self, document_text: str) -> List[str]:
        """ドキュメントからタスクリストを抽出する"""
        if not document_text.strip():
            return []

        # プロンプトテンプレートにドキュメントを埋め込む
        final_prompt = self.prompt_template.format(document_text=document_text)

        # LLMにプロンプトを実行させる
        try:
            raw_response = self.client.execute_prompt(final_prompt)
        except (ConnectionError, RuntimeError) as e:
            # UI側でエラーを表示するため、ここでは再raiseする
            raise
            
        # LLMの応答を解析してリストに変換する
        tasks = [line.strip() for line in raw_response.split('\n') if line.strip()]
        
        # 簡単なバリデーション（空行や不要な文字を取り除く）
        # TODO: より堅牢なバリデーションを utils/validators.py に実装する
        cleaned_tasks = [task for task in tasks if self._is_valid_task_name(task)]
        
        return cleaned_tasks

    def _is_valid_task_name(self, task_name: str) -> bool:
        """タスク名が基本的な命名規則に従っているかチェックする"""
        # 今は単純に空でないことだけをチェック
        return bool(task_name)