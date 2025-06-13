# core/yaml_generator.py (これを適用してほしい)

import json
import yaml
import re # ◀ re をインポート
from .llm_client import LLMClient, load_prompt_template
from typing import List, Dict

class YamlGenerator:
    def __init__(self, llm_client: LLMClient):
        self.client = llm_client
        self.prompt_template = load_prompt_template("generate_yaml.prompt")

    def generate(self, document_text: str, tasks: List[str], analysis_result: Dict[str, List[str]]) -> str:
        """
        ここまでの情報から、最終的なワークフローYAMLを生成する。
        """
        if not tasks or not analysis_result:
            return "# タスクまたは依存関係が不足しているため、YAMLを生成できません。"

        # プロンプトで使いやすいように、データを文字列に変換
        task_list_str = "\n".join(f"- {task}" for task in tasks)
        analysis_json_str = json.dumps(analysis_result, indent=2, ensure_ascii=False)

        # 💥💥💥 修正: この定義を追加する 💥💥💥
        # プロンプトテンプレートに情報を埋め込む
        final_prompt = self.prompt_template.format(
            document_text=document_text,
            task_list_str=task_list_str,
            analysis_json_str=analysis_json_str 
        )
        # 💥💥💥 ここまで 💥💥💥

        try:
            # LLMにプロンプトを実行させる
            raw_response = self.client.execute_prompt(final_prompt) # ◀ これで final_prompt が使える
            
            clean_yaml = self._extract_yaml_from_response(raw_response)
            self._validate_yaml(clean_yaml)

        except (ConnectionError, RuntimeError) as e:
            raise
        except ValueError as e:
            raise
        except yaml.YAMLError as e:
            raise ValueError(f"LLMが不正なYAMLを生成しました: {e}\n生成内容:\n{raw_response}")
            
        return clean_yaml

    def _extract_yaml_from_response(self, response: str) -> str:
        """LLMの応答からYAML部分だけを抽出する"""
        match = re.search(r'```yaml\s*(.*?)\s*```', response, re.DOTALL)
        if match:
            return match.group(1).strip()

        lines = response.split('\n')
        start_index = -1
        for i, line in enumerate(lines):
            if line.strip().startswith(('name:', 'nodes:', 'global_variables:')):
                start_index = i
                break
        
        if start_index != -1:
            return '\n'.join(lines[start_index:])
        
        raise ValueError(f"応答からYAMLの開始点を見つけられませんでした。\n応答内容:\n{response}")

    def _validate_yaml(self, yaml_string: str):
        """生成された文字列が妥当なYAMLか検証する。不正な場合は例外を発生させる。"""
        if not yaml_string.strip():
            raise ValueError("LLMが空の応答を返しました。")
        try:
            yaml.safe_load(yaml_string)
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"{e}\n---検証したYAML---\n{yaml_string}")