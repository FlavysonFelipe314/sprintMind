import json
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_ollama import ChatOllama

from src.utils import ensure_dir, safe_filename

load_dotenv()


class CommentedDocumenter:
    def __init__(self, output_dir="output/commented"):
        self.output_dir = output_dir
        ensure_dir(output_dir)

        self.chat_model = os.getenv(
            "OLLAMA_CHAT_MODEL",
            "gpt-oss:120b-cloud"
        )

    def simplify_analysis(self, analysis: dict):
        return {
            "entry_name": analysis.get("entry_name"),
            "entry_file": analysis.get("entry_file"),
            "total_files": analysis.get("total_files"),
            "visited_files": analysis.get("visited_files"),
            "graph": analysis.get("graph"),
        }

    def generate(self, analysis: dict) -> str:
        simplified = self.simplify_analysis(analysis)

        prompt = f"""
Você é um arquiteto de software sênior especializado em PHP, Laravel, CodeIgniter, HTML, CSS, JavaScript, jQuery, documentação técnica e refatoração.

Gere uma documentação no estilo de documentação oficial do Laravel:
clara, comentada, navegável, didática, útil para manutenção e sem parecer Swagger.

Não invente fatos.
Quando algo não estiver claro, use "aparentemente", "provavelmente" ou "não foi possível confirmar".

Formato obrigatório:

# Visão geral

# Quando usar esta documentação

# Entrada do fluxo

# Caminho da requisição

# Responsabilidade do controller

# Mapa Front x Back

# Arquivos importantes

# Fluxos principais encontrados

# Dependências e integrações

# Pontos de atenção

# Melhorias recomendadas

# Cenários de teste sugeridos

# Plano de refatoração sugerido

# Possíveis cards Jira

CONTEXTO:
{json.dumps(simplified, ensure_ascii=False, indent=2)}
"""

        llm = ChatOllama(model=self.chat_model, temperature=0.2)
        response = llm.invoke(prompt)

        return response.content

    def save(self, analysis: dict) -> str:
        content = self.generate(analysis)

        filename = safe_filename(analysis["entry_name"]) + "-comentado.md"
        path = Path(self.output_dir) / filename

        path.write_text(content, encoding="utf-8")
        return str(path)