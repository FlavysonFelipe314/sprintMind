from src.rag import CodeRag


def main():
    rag = CodeRag()

    print("Chat OmniFlow")
    print("Digite 'sair' para encerrar.")
    print("")

    while True:
        question = input("Pergunta: ")

        if question.lower().strip() in ["sair", "exit", "quit"]:
            break

        print("")
        print("Resposta:")
        rag.ask_stream(question)
        print("")


if __name__ == "__main__":
    main()