import os
from pathlib import Path
from dotenv import load_dotenv

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_chroma import Chroma

load_dotenv()


class CodeRag:
    def __init__(
        self,
        docs_dirs=None,
        persist_dir: str = "output/vectorstore",
        chunk_size: int = 2500,
        chunk_overlap: int = 400,
        search_k: int = 6
    ):
        if docs_dirs is None:
            docs_dirs = [
                "output/docs",
                "output/commented"
            ]

        self.docs_dirs = docs_dirs
        self.persist_dir = persist_dir
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.search_k = search_k

        self.embedding_model = os.getenv(
            "OLLAMA_EMBEDDING_MODEL",
            "nomic-embed-text"
        )

        self.chat_model = os.getenv(
            "OLLAMA_CHAT_MODEL",
            "gpt-oss:120b-cloud"
        )

    def load_markdown_documents(self):
        documents = []

        for docs_dir in self.docs_dirs:
            path = Path(docs_dir)

            if not path.exists():
                continue

            for file in path.rglob("*.md"):
                content = file.read_text(encoding="utf-8", errors="ignore")

                documents.append(
                    Document(
                        page_content=content,
                        metadata={
                            "source": str(file),
                            "filename": file.name
                        }
                    )
                )

        return documents

    def build_index(self):
        documents = self.load_markdown_documents()

        if not documents:
            return {
                "documents": 0,
                "chunks": 0,
                "persist_dir": self.persist_dir
            }

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )

        chunks = splitter.split_documents(documents)

        embeddings = OllamaEmbeddings(model=self.embedding_model)

        Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=self.persist_dir
        )

        return {
            "documents": len(documents),
            "chunks": len(chunks),
            "persist_dir": self.persist_dir
        }

    def get_relevant_context(self, question: str):
        embeddings = OllamaEmbeddings(model=self.embedding_model)

        db = Chroma(
            persist_directory=self.persist_dir,
            embedding_function=embeddings
        )

        docs = db.similarity_search(question, k=self.search_k)

        context = "\n\n".join([
            f"Fonte: {doc.metadata.get('source', 'desconhecida')}\n{doc.page_content}"
            for doc in docs
        ])

        return context, docs

    def build_prompt(self, question: str, context: str):
        return f"""
Você é o Agente OmniFlow, especialista em arquitetura de software, PHP, Laravel, CodeIgniter, HTML, CSS, JavaScript, jQuery, documentação técnica, refatoração, QA e planejamento de desenvolvimento.

Use APENAS o contexto abaixo para responder.
Se não houver informação suficiente, diga claramente que não foi possível confirmar.

IMPORTANTE:
- Você pode conversar sobre fluxos, melhorias, mapeamentos, testes e desenvolvimento.
- Você pode sugerir cards Jira apenas se o usuário pedir.
- Você nunca deve dizer que criou card Jira se a ação não foi confirmada por botão ou endpoint.
- Não use tabelas.
- Não use Markdown complexo.
- Use títulos curtos e listas simples.
- Diferencie fato encontrado de hipótese.

CONTEXTO:
{context}

PERGUNTA:
{question}

Responda em português, de forma clara, técnica e comentada.
"""

    def ask(self, question: str):
        context, docs = self.get_relevant_context(question)
        prompt = self.build_prompt(question, context)

        llm = ChatOllama(model=self.chat_model, temperature=0.2)
        response = llm.invoke(prompt)

        return {
            "result": response.content,
            "sources": docs
        }

    def ask_stream(self, question: str):
        context, docs = self.get_relevant_context(question)
        prompt = self.build_prompt(question, context)

        llm = ChatOllama(model=self.chat_model, temperature=0.2)

        for chunk in llm.stream(prompt):
            print(chunk.content, end="", flush=True)