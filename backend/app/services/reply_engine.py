"""Reply engine using DeepSeek API"""
import json
import asyncio
from typing import Optional
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from app.config import get_settings

settings = get_settings()


class ReplyEngine:
    """AI-powered reply suggestion engine"""

    def __init__(self):
        self.llm = None
        if settings.deepseek_api_key:
            self.llm = ChatOpenAI(
                model="deepseek-chat",
                temperature=0.7,
                openai_api_key=settings.deepseek_api_key,
                openai_api_base="https://api.deepseek.com/v1"
            )

    def _call_llm(self, prompt: str) -> str:
        """Synchronous LLM call"""
        if not self.llm:
            return ""
        return self.llm([HumanMessage(content=prompt)]).content

    def _parse_json_response(self, content: str) -> Optional[dict]:
        """Parse JSON from LLM response"""
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            start = content.find('{')
            end = content.rfind('}') + 1
            if start >= 0 and end > start:
                try:
                    return json.loads(content[start:end])
                except json.JSONDecodeError:
                    pass
        return None

    async def smart_context_reply(
        self,
        draft: str,
        context: str,
        style: str = "concise"
    ) -> dict:
        """智能语境模式 - 基于对话背景优化回复"""
        style_prompts = {
            "formal": "用正式、商务的语气",
            "playful": "用俏皮、轻松的语气",
            "concise": "简洁明了",
            "warm": "热情友好",
            "tactful": "委婉含蓄"
        }

        prompt = f"""你是一个聊天助手，帮助用户优化回复。

当前对话背景：
{context}

用户的回复草稿：
{draft}

请用 {style_prompts.get(style, '简洁')} 的方式进行优化。

请返回JSON格式：
{{"context_analysis": "对方说这句话可能的情绪和意图分析",
  "suggestions": [
    {{"content": "回复建议1", "style": "风格", "reason": "为什么这样建议"}},
    {{"content": "回复建议2", "style": "风格", "reason": "为什么这样建议"}},
    {{"content": "回复建议3", "style": "风格", "reason": "为什么这样建议"}}
  ],
  "improved_reply": "优化后的完整回复"}}
"""
        if not self.llm:
            return self._fallback_response(draft, context, style)

        try:
            loop = asyncio.get_event_loop()
            content = await loop.run_in_executor(None, self._call_llm, prompt)
            result = self._parse_json_response(content)
            if result:
                return result
            return self._fallback_response(draft, context, style)
        except Exception:
            return self._fallback_response(draft, context, style)

    async def quick_question_reply(
        self,
        scenario: str,
        style: str = "concise"
    ) -> dict:
        """快速问答模式 - 直接给出回复建议"""
        style_prompts = {
            "formal": "正式、商务",
            "playful": "俏皮、轻松",
            "concise": "简洁",
            "warm": "热情",
            "tactful": "委婉"
        }

        prompt = f"""你是一个聊天助手，给出回复建议。

场景：{scenario}

请用 {style_prompts.get(style, '简洁')} 的风格给出3-5个回复建议。

请返回JSON格式：
{{"scenario_analysis": "对这个场景的分析",
  "suggestions": [
    {{"content": "建议1", "style": "风格", "reason": "原因"}},
    {{"content": "建议2", "style": "风格", "reason": "原因"}},
    {{"content": "建议3", "style": "风格", "reason": "原因"}}
  ]}}
"""
        if not self.llm:
            return self._fallback_quick(scenario, style)

        try:
            loop = asyncio.get_event_loop()
            content = await loop.run_in_executor(None, self._call_llm, prompt)
            result = self._parse_json_response(content)
            if result:
                return result
            return self._fallback_quick(scenario, style)
        except Exception:
            return self._fallback_quick(scenario, style)

    async def improve_draft(
        self,
        draft: str,
        target_style: str = "concise"
    ) -> dict:
        """优化用户草稿"""
        style_prompts = {
            "formal": "正式、商务",
            "playful": "俏皮、轻松",
            "concise": "简洁有力",
            "warm": "热情温暖",
            "tactful": "委婉含蓄"
        }

        prompt = f"""请优化以下回复，使其更加{style_prompts.get(target_style, '简洁')}：

原始回复：
{draft}

请返回JSON格式：
{{"original": "原始回复",
  "improved": "优化后的回复",
  "suggestions": ["建议1", "建议2", "建议3"]}}
"""
        if not self.llm:
            return {"original": draft, "improved": draft, "suggestions": []}

        try:
            loop = asyncio.get_event_loop()
            content = await loop.run_in_executor(None, self._call_llm, prompt)
            result = self._parse_json_response(content)
            if result:
                return result
            return {"original": draft, "improved": draft, "suggestions": []}
        except Exception:
            return {"original": draft, "improved": draft, "suggestions": []}

    def _fallback_response(self, draft, context, style) -> dict:
        """Fallback when API fails"""
        return {
            "context_analysis": "无法分析，请稍后重试",
            "suggestions": [
                {"content": draft, "style": style, "reason": "使用原始草稿"}
            ],
            "improved_reply": draft
        }

    def _fallback_quick(self, scenario, style) -> dict:
        return {
            "scenario_analysis": "无法分析，请稍后重试",
            "suggestions": []
        }