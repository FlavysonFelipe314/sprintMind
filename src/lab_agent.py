import os
import json
from dotenv import load_dotenv
from langchain_ollama import ChatOllama

from src.rag import CodeRag

load_dotenv()


class LabAgent:
    def __init__(self):
        self.rag = CodeRag()
        self.chat_model = os.getenv("OLLAMA_CHAT_MODEL", "gpt-oss:120b-cloud")

    def detect_intent(self, message: str):
        text = message.lower()

        if any(x in text for x in ["criar card", "card jira", "subir no jira", "publicar no jira"]):
            return "prepare_jira_card"

        if any(x in text for x in ["cenário de teste", "cenarios de teste", "teste", "qa"]):
            return "test_scenarios"

        if any(x in text for x in ["front", "back", "mapeamento", "mapear"]):
            return "front_back_mapping"

        if any(x in text for x in ["refatorar", "melhoria", "gargalo", "arquitetura"]):
            return "improvement"

        return "conversation"

    def ask(self, message: str):
        intent = self.detect_intent(message)

        if intent == "prepare_jira_card":
            return self.prepare_jira_card(message)

        if intent == "test_scenarios":
            return self.generate_test_scenarios(message)

        if intent == "front_back_mapping":
            return self.generate_front_back_mapping(message)

        if intent == "improvement":
            return self.generate_improvements(message)

        response = self.rag.ask(message)

        return {
            "type": "conversation",
            "answer": response["result"]
        }

    def generate_test_scenarios(self, message: str):
        question = f"""
Com base no fluxo analisado, gere cenários de teste funcionais, negativos e de regressão.
Pedido do usuário: {message}
"""
        response = self.rag.ask(question)

        return {
            "type": "test_scenarios",
            "answer": response["result"]
        }

    def generate_front_back_mapping(self, message: str):
        question = f"""
Com base no fluxo analisado, gere um mapeamento Front x Back:
- tela/view
- JS/jQuery
- eventos
- chamadas AJAX
- rotas
- controller
- services/models
- retorno esperado
Pedido do usuário: {message}
"""
        response = self.rag.ask(question)

        return {
            "type": "front_back_mapping",
            "answer": response["result"]
        }

    def generate_improvements(self, message: str):
        question = f"""
Com base no fluxo analisado, gere uma análise de melhorias:
- gargalos
- acoplamentos
- riscos
- refatorações sugeridas
- ordem segura de execução
Pedido do usuário: {message}
"""
        response = self.rag.ask(question)

        return {
            "type": "improvement",
            "answer": response["result"]
        }

    def prepare_jira_card(self, message: str):
        context, docs = self.rag.get_relevant_context(message)

        prompt = f"""
Você é um analista de requisitos técnico.

Com base no contexto, monte um RASCUNHO de card Jira.
Não diga que criou o card.
Apenas prepare o rascunho para o usuário revisar.

Retorne JSON válido com esta estrutura:
{{
  "summary": "Título curto do card",
  "issue_type": "Task",
  "priority": "Medium",
  "story_points": 5,
  "description": "Descrição técnica detalhada",
  "acceptance_criteria": [
    "Critério 1",
    "Critério 2"
  ],
  "labels": ["omniflow", "refatoracao"],
  "questions": [
    "Pergunta para o usuário caso falte informação"
  ]
}}

CONTEXTO:
{context}

PEDIDO:
{message}
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
                "summary": "Card técnico gerado pelo OmniFlow",
                "issue_type": "Task",
                "priority": "Medium",
                "story_points": 5,
                "description": raw,
                "acceptance_criteria": [],
                "labels": ["omniflow"],
                "questions": []
            }

        return {
            "type": "jira_draft",
            "answer": "Montei um rascunho de card Jira para revisão.",
            "draft": data
        }