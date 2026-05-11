import os
import json
from dotenv import load_dotenv
from langchain_ollama import ChatOllama

from src.rag import CodeRag

load_dotenv()


class CardAgent:
    def __init__(self):
        self.rag = CodeRag()
        self.chat_model = os.getenv("OLLAMA_CHAT_MODEL", "gpt-oss:120b-cloud")

    def generate_cards(self, payload: dict):
        user_context = payload.get("context", "")
        analysis_type = payload.get("analysis_type", "fluxo")
        objective = payload.get("objective", "")
        amount_mode = payload.get("amount_mode", "auto")

        rag_question = f"""
Contexto do usuário:
{user_context}

Tipo de análise:
{analysis_type}

Objetivo:
{objective}

Gere cards técnicos relacionados ao contexto.
"""

        context, docs = self.rag.get_relevant_context(rag_question)

        prompt = f"""
Você é um analista de requisitos técnico e arquiteto de software.

Sua tarefa é gerar cards Jira a partir do contexto informado.

REGRAS:
- Não publique nada no Jira.
- Apenas gere rascunhos.
- Se houver vários endpoints, gere um card por endpoint quando fizer sentido.
- Se houver front e back, separe cards de front, back e QA quando fizer sentido.
- Não invente endpoints que não foram citados.
- Diferencie fato de hipótese.
- Gere quantos cards forem necessários se amount_mode for "auto".
- Retorne APENAS JSON válido.

FORMATO:
{{
  "cards": [
    {{
      "summary": "Título do card",
      "issue_type": "Task",
      "priority": "Medium",
      "story_points": 5,
      "area": "Backend",
      "description": "Descrição técnica detalhada",
      "acceptance_criteria": [
        "Critério 1",
        "Critério 2"
      ],
      "technical_notes": [
        "Nota técnica 1"
      ],
      "labels": ["omniflow"]
    }}
  ]
}}

CONTEXTO RAG:
{context}

CONTEXTO MANUAL DO USUÁRIO:
{user_context}

TIPO DE ANÁLISE:
{analysis_type}

OBJETIVO:
{objective}
"""

        llm = ChatOllama(model=self.chat_model, temperature=0.2)
        response = llm.invoke(prompt)

        raw = response.content.strip()

        try:
            start = raw.find("{")
            end = raw.rfind("}") + 1
            data = json.loads(raw[start:end])
        except Exception:
            data = {
                "cards": [
                    {
                        "summary": "Card técnico gerado pelo OmniFlow",
                        "issue_type": "Task",
                        "priority": "Medium",
                        "story_points": 5,
                        "area": "Geral",
                        "description": raw,
                        "acceptance_criteria": [],
                        "technical_notes": [],
                        "labels": ["omniflow"]
                    }
                ]
            }

        return data