from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_pinecone import PineconeVectorStore

from src.llm_connector import get_llm
from src.embedding_client import get_embedding_model
from src.config import PINECONE_INDEX_NAME

def get_rag_chain():
    """
    Initializes and returns a fully configured RAG chain for CRM Q&A.
    """
    vectorstore = PineconeVectorStore(
        index_name=PINECONE_INDEX_NAME, 
        embedding=get_embedding_model()
    )
    retriever = vectorstore.as_retriever()

    template = """
    You are an expert assistant for Breeze AI, a CRM Copilot.
    Use the following retrieved context from the CRM to answer the user's question.
    If you don't know the answer from the context, just say that you don't have enough information.
    Do not make up an answer. Keep the answer concise.

    CONTEXT:
    {context}

    QUESTION:
    {question}

    ANSWER:
    """
    prompt = ChatPromptTemplate.from_template(template)

    # --- THIS IS THE CRITICAL FIX ---
    # We force the LLM to be factual and not creative.
    llm = get_llm(temperature=0.0)

    # The rest of the chain is the same
    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain

# The direct test block remains the same
if __name__ == '__main__':
    print("--- Running a direct test of the RAG Chain ---")
    chain = get_rag_chain()
    print("✅ RAG chain created successfully.")
    test_question = "What is the value of the deal with EmpowerMove?"
    print(f"\nInvoking chain with question: '{test_question}'")
    answer = chain.invoke(test_question)
    print("\n--- RAG Chain Answer ---")
    print(answer)
    print("------------------------")