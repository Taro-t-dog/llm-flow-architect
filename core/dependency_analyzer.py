# core/dependency_analyzer.py (再々設計・修正後)

import json
import re
from .llm_client import LLMClient, load_prompt_template
from typing import List, Dict, Any

class DependencyAnalyzer:
    def __init__(self, llm_client: LLMClient):
        self.client = llm_client
        # 修正: プロンプトはそれぞれ個別に読み込む
        self.summary_prompt_template = load_prompt_template("generate_summaries.prompt")
        self.deps_prompt_template = load_prompt_template("analyze_dependencies_from_summaries.prompt")

    def analyze(self, document_text: str, tasks: List[str]) -> Dict[str, Dict[str, Any]]:
        if not tasks:
            return {}
        
        # --- ステップ1: 各タスクの要約を生成 ---
        try:
            summaries = self._generate_summaries(document_text, tasks)
        except (ConnectionError, RuntimeError, ValueError) as e:
            # エラーメッセージを具体的にする
            raise ValueError(f"タスク要約の生成中にエラーが発生しました: {e}")

        # --- ステップ2: 要約を基に依存関係を分析 ---
        try:
            dependencies = self._analyze_dependencies(summaries)
        except (ConnectionError, RuntimeError, ValueError) as e:
            raise ValueError(f"依存関係の分析中にエラーが発生しました: {e}")

        # --- 最終結果の結合 ---
        final_result = {}
        for task in tasks:
            final_result[task] = {
                "summary": summaries.get(task, "（要約なし）"),
                "dependencies": dependencies.get(task, [])
            }
        return final_result

    def _generate_summaries(self, document_text: str, tasks: List[str]) -> Dict[str, str]:
        """各タスクの要約を生成する"""
        prompt = self.summary_prompt_template.format(
            document_text=document_text,
            task_list_str="\n".join(tasks)
        )
        raw_response = self.client.execute_prompt(prompt)
        # ここではJSONパーサーをより堅牢にする
        return self._parse_json_response(raw_response)

    def _analyze_dependencies(self, summaries: Dict[str, str]) -> Dict[str, List[str]]:
        """要約情報を使って依存関係を分析する"""
        summaries_str = json.dumps(summaries, indent=2, ensure_ascii=False)
        prompt = self.deps_prompt_template.format(summaries_json_str=summaries_str)
        raw_response = self.client.execute_prompt(prompt)
        return self._parse_json_response(raw_response)

    def _parse_json_response(self, response: str) -> Dict:
        """LLMの応答からJSONを抽出しパースする共通関数"""
        # (この関数は前回と同じだが、デバッグ情報を強化)
        match = re.search(r'\{.*\}', response, re.DOTALL)
        if not match:
            match = re.search(r'```json\s*(\{.*?\})\s*```', response, re.DOTALL)
            if match:
                 json_string = match.group(1)
            else:
                 # 💥 デバッグ情報としてLLMの生応答をエラーメッセージに含める
                 raise ValueError(f"応答からJSONオブジェクトを見つけられませんでした。\n---LLMの応答---\n{response}")
        else:
            json_string = match.group(0)

        try:
            return json.loads(json_string)
        except json.JSONDecodeError as e:
            raise ValueError(f"抽出された文字列が不正なJSON形式です: {e}\n---抽出内容---\n{json_string}")