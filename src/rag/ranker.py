"""LLM-based ranker for VR app recommendations.

Uses OpenRouter API to re-rank applications and generate explanations.
"""

import os
import json
from typing import List, Dict

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


class LLMRanker:
    """Rank and explain VR app recommendations using LLM."""

    def __init__(self):
        """Initialize the LLM ranker with OpenRouter configuration."""
        if OpenAI is None:
            raise ImportError("openai package required. Install with: pip install openai")

        self.client = OpenAI(
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1"
        )
        self.model = os.getenv("OPENROUTER_MODEL", "qwen/qwen3-30b-a3b")

    def rank_and_explain(self, query: str, apps: List[Dict]) -> List[Dict]:
        """
        Rank applications and generate reasoning for each.

        Args:
            query: User query string
            apps: List of candidate VR applications

        Returns:
            List of applications with reasoning added
        """
        if not apps:
            return []

        # Build prompt
        app_items = []
        for app in apps:
            info = f"- {app['name']} ({app['category']}): matches {', '.join(app['matched_skills'])}"
            if app.get("retrieval_source") == "semantic_bridge":
                info += f" [Note: {app.get('bridge_explanation', 'Indirect match')}]"
            app_items.append(info)
            
        app_list = "\n".join(app_items)

        prompt = f"""用户查询: "{query}"

候选 VR 应用:
{app_list}

请为每个应用生成一句简短的推荐理由（说明为什么这个应用适合用户的学习需求）。
如果应用有 [Note: ...]，请在推荐理由中结合该信息解释（例如："虽然没有直接匹配，但因为它涉及..."）。

返回 JSON 格式:
{{
    "rankings": [
        {{"name": "App Name", "reasoning": "推荐理由"}},
        ...
    ]
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个 VR 学习应用推荐专家。只返回 JSON。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1024
            )

            return self._parse_rankings(response.choices[0].message.content, apps)
        except Exception as e:
            print(f"LLM ranking error: {e}")
            # Return apps with default reasoning
            for app in apps:
                app["reasoning"] = "Matches your learning interests"
            return apps

    def _parse_rankings(self, content: str, apps: List[Dict]) -> List[Dict]:
        """
        Parse LLM response and extract rankings.

        Args:
            content: LLM response text
            apps: Original apps list

        Returns:
            Apps with reasoning added
        """
        try:
            content = content.strip()
            if "```" in content:
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]

            data = json.loads(content)
            rankings = {r["name"]: r["reasoning"] for r in data.get("rankings", [])}
        except Exception as e:
            print(f"Parse error: {e}")
            rankings = {}

        # Add reasoning to each app
        for app in apps:
            app["reasoning"] = rankings.get(app["name"], "Matches your learning interests")

        return apps

    def understand_query(self, query: str) -> str:
        """
        Understand user query intent using LLM.

        Args:
            query: User query string

        Returns:
            One-sentence understanding of the query
        """
        prompt = f"""分析以下学习查询，用一句话总结用户想要学习什么:

"{query}"

直接返回总结，不要其他内容。"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=100
            )

            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Query understanding error: {e}")
            return f"Learning interest: {query}"
