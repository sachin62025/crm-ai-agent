import sys

sys.path.append("src")

from langchain.docstore.document import Document

# LOOK HERE: This line is different from the old version
from langchain_pinecone import PineconeVectorStore
from langchain.text_splitter import RecursiveCharacterTextSplitter

from src.crm_connector import get_recent_deals
from src.vector_store_connector import get_pinecone_client, get_pinecone_index
from src.embedding_client import get_embedding_model
from src.config import PINECONE_INDEX_NAME


# The function below is unchanged
def format_deal_to_document(deal: dict) -> Document:
    content = (
        f"Information about the CRM deal titled '{deal.get('title', 'N/A')}' "
        f"with Deal ID: {deal.get('id', 0)}. "  # <-- ADD THIS LINE
        f"The current status of this deal is '{deal.get('status', 'N/A')}'. "
        f"It has a value of {deal.get('value', 0)} {deal.get('currency', '')}. "
        f"The deal is owned by {deal.get('owner_name', 'N/A')}. "
        f"The main contact person is {deal.get('person_name', 'N/A')} "
        f"at the organization {deal.get('org_name', 'N/A')}."
    )

    metadata = {
        "source": "pipedrive",
        "deal_id": deal.get("id", 0),
        "status": deal.get("status", "N/A"),
        "value": deal.get("value", 0),
    }
    return Document(page_content=content, metadata=metadata)


def main():
    """Main function to run the data ingestion pipeline."""
    print("--- Starting CRM Data Ingestion and Vectorization ---")

    print("Step 1: Initializing clients...")
    pc_client = get_pinecone_client()
    embedding_model = get_embedding_model()

    if not all([pc_client, embedding_model]):
        print("❌ Client initialization failed. Aborting.")
        return

    print("Step 2: Fetching deals from Pipedrive...")
    deals = get_recent_deals(limit=100)
    if not deals:
        print("⚠️ No deals found in Pipedrive. Nothing to ingest.")
        return
    print(f"   Found {len(deals)} deals.")

    print("Step 3: Formatting deals into LangChain Documents...")
    documents = [format_deal_to_document(deal) for deal in deals]

    print("Step 4: Splitting documents into smaller chunks...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs_to_ingest = text_splitter.split_documents(documents)
    print(f"   Split into {len(docs_to_ingest)} chunks.")

    print("Step 5: Ingesting data into Pinecone...")
    get_pinecone_index(pc_client, PINECONE_INDEX_NAME)

    # LOOK HERE: This line is also different. It uses PineconeVectorStore.
    PineconeVectorStore.from_documents(
        documents=docs_to_ingest,
        embedding=embedding_model,
        index_name=PINECONE_INDEX_NAME,
    )

    print("\n--- ✅ Ingestion Complete! ---")
    print(
        f"Successfully vectorized and stored {len(docs_to_ingest)} document chunks in Pinecone."
    )


if __name__ == "__main__":
    main()
