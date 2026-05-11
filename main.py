import argparse

from src.analyzer import PhpControllerAnalyzer
from src.documenter import MarkdownDocumenter
from src.commented_documenter import CommentedDocumenter
from src.site_generator import HtmlSiteGenerator
from src.rag import CodeRag
from src.cards_site_generator import CardsSiteGenerator

def log(msg):
    print(f"[OmniFlow] {msg}", flush=True)


def main():
    parser = argparse.ArgumentParser(
        description="OmniFlow - Analisa fluxo de código PHP/Laravel"
    )

    parser.add_argument("--project", required=True)
    parser.add_argument(
        "--controller",
        required=False,
        default=None
    )
    parser.add_argument("--depth", type=int, default=5)
    parser.add_argument("--build-rag", action="store_true")
    parser.add_argument(
        "--mode",
        choices=["flow", "project"],
        default="flow"
    )
    
    args = parser.parse_args()

    log("Iniciando análise...")
    log(f"Projeto: {args.project}")
    if args.controller:
        log(f"Arquivo inicial: {args.controller}")
        
    log(f"Profundidade: {args.depth}")

    analyzer = PhpControllerAnalyzer(
        project_path=args.project,
        max_depth=args.depth
    )

    log("Mapeando arquivos e dependências...")
    
    if args.mode == "project":
        log("Executando análise completa do projeto...")
        analysis = analyzer.analyze_project()

    else:
        if not args.controller:
            raise ValueError(
                "No modo flow é obrigatório informar --controller"
            )

        log("Executando análise por fluxo...")
        analysis = analyzer.analyze(args.controller)
        
        
    log(f"Arquivos analisados: {analysis['total_files']}")

    log("Gerando documentação técnica bruta...")
    documenter = MarkdownDocumenter()
    doc_path = documenter.save(analysis)
    log(f"Documentação técnica gerada: {doc_path}")

    log("Gerando documentação comentada com IA...")
    commented = CommentedDocumenter()
    commented_path = commented.save(analysis)
    log(f"Documentação comentada gerada: {commented_path}")

    log("Gerando site HTML...")
    site = HtmlSiteGenerator()
    site_path = site.save(analysis)
    log(f"Site HTML gerado: {site_path}")

    log("Gerando tela Cards Lab...")
    cards_site = CardsSiteGenerator()
    cards_path = cards_site.save()
    log(f"Cards Lab gerado: {cards_path}")

    if args.build_rag:
        log("Iniciando criação da base RAG...")
        log("Gerando chunks e embeddings...")
        rag = CodeRag()
        result = rag.build_index()

        log(f"Documentos indexados: {result['documents']}")
        log(f"Chunks gerados: {result['chunks']}")
        log(f"Vectorstore: {result['persist_dir']}")

    log("Processo finalizado.")


if __name__ == "__main__":
    main()