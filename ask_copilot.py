import sys

sys.path.append("src")

from src.rag_chain import get_rag_chain


def main():
    """
    Main function to run the interactive Q&A loop.
    """
    print("--- Breeze AI Copilot: CRM Q&A Mode ---")
    print("Initializing RAG chain... (This may take a moment)")

    try:
        rag_chain = get_rag_chain()
        print("✅ Chain ready. You can now ask questions about your CRM deals.")
        print("   (Type 'exit' to quit)")
    except Exception as e:
        print(f"❌ Failed to initialize RAG chain: {e}")
        return

    while True:
        # Get user input
        question = input("\nYour Question: ")

        if question.lower().strip() == "exit":
            print("Exiting Copilot. Goodbye!")
            break

        if not question:
            continue

        # Invoke the RAG chain and stream the output
        print("Copilot is thinking...")
        answer = rag_chain.invoke(question)
        print("\nCopilot's Answer:")
        print(answer)


if __name__ == "__main__":
    main()
