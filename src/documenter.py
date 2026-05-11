from pathlib import Path
from src.utils import ensure_dir, safe_filename


class MarkdownDocumenter:
    def __init__(self, output_dir: str = "output/docs"):
        self.output_dir = output_dir
        ensure_dir(output_dir)

    def save(self, analysis: dict) -> str:
        markdown = self.generate(analysis)

        filename = safe_filename(analysis["entry_name"]) + ".md"
        output_path = Path(self.output_dir) / filename

        output_path.write_text(markdown, encoding="utf-8")
        return str(output_path)

    def generate(self, analysis: dict) -> str:
        md = []

        md.append(f"# Documentação Técnica Bruta - {analysis['entry_name']}")
        md.append("")
        md.append(f"Arquivo inicial: `{analysis['entry_file']}`")
        md.append(f"Total de arquivos analisados: `{analysis['total_files']}`")
        md.append("")

        md.append("## Arquivos percorridos")
        for file in analysis["visited_files"]:
            md.append(f"- `{file}`")

        md.append("")
        md.append("## Mapa técnico do fluxo")
        self.render_node(md, analysis["graph"], level=0)

        return "\n".join(md)

    def render_node(self, md: list, node: dict, level: int):
        prefix = "#" * min(6, level + 2)

        file = node.get("file", "arquivo desconhecido")
        md.append("")
        md.append(f"{prefix} Arquivo: `{file}`")
        md.append("")

        if node.get("already_visited"):
            md.append("Arquivo já analisado anteriormente.")
            return

        if node.get("not_found"):
            md.append("Arquivo não encontrado.")
            return

        if node.get("max_depth_reached"):
            md.append("Limite de profundidade atingido.")
            return

        md.append(f"- Tipo: `{node.get('type')}`")
        md.append(f"- Classe: `{node.get('class')}`")
        md.append(f"- Namespace: `{node.get('namespace')}`")
        md.append(f"- Profundidade: `{node.get('depth')}`")

        if node.get("routes"):
            md.append("")
            md.append("### Rotas relacionadas")
            for route in node["routes"]:
                md.append(f"- `{route['route_file']}` → `{route['line']}`")

        if node.get("uses"):
            md.append("")
            md.append("### Imports")
            for use in node["uses"]:
                md.append(f"- `{use}`")

        if node.get("methods"):
            md.append("")
            md.append("### Métodos")
            for method in node["methods"]:
                md.append("")
                md.append(f"#### `{method['visibility']} function {method['name']}({method['params']})`")
                md.append(f"- Resumo: `{method['summary']}`")
                md.append(f"- Usa Request: `{method['uses_request']}`")
                md.append(f"- Retorna view: `{method['returns_view']}`")
                md.append(f"- Retorna JSON: `{method['returns_json']}`")
                md.append(f"- Dispara Job/Event: `{method['dispatches_job']}`")

        if node.get("ajax_calls"):
            md.append("")
            md.append("### AJAX / Fetch detectado")
            for call in node["ajax_calls"]:
                md.append(f"- `{call}`")

        if node.get("jquery_events"):
            md.append("")
            md.append("### Eventos jQuery")
            for event in node["jquery_events"]:
                md.append(f"- `{event['selector']}` → `{event['event']}`")

        if node.get("dependencies"):
            md.append("")
            md.append("### Dependências navegadas")
            for dep in node["dependencies"]:
                md.append(f"- `{dep}`")

        for child in node.get("children", []):
            self.render_node(md, child, level + 1)