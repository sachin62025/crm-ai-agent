from pinecone import Pinecone, ServerlessSpec
# We need to import the config module from the same directory
import config

# It's good practice to define the embedding dimensions here.
EMBEDDING_DIMENSION = 4096

def get_pinecone_client():
    """Initializes and returns the Pinecone client."""
    try:
        pc = Pinecone(api_key=config.PINECONE_API_KEY)
        return pc
    except Exception as e:
        print(f"Failed to initialize Pinecone client: {e}")
        return None

def get_pinecone_index(client: Pinecone, index_name: str):
    """
    Gets a Pinecone index, creating it if it doesn't exist.
    """
    if not client:
        return None
    
    if index_name not in client.list_indexes().names():
        print(f"Index '{index_name}' not found. Creating a new one...")
        try:
            client.create_index(
                name=index_name,
                dimension=EMBEDDING_DIMENSION,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1" 
                )
            )
            print(f"Index '{index_name}' created successfully.")
        except Exception as e:
            print(f"Failed to create index '{index_name}': {e}")
            return None
    else:
        print(f"Found existing index '{index_name}'.")

    return client.Index(index_name)

# This __main__ block for direct testing is fine and does not cause issues.
if __name__ == '__main__':
    print("--- Running a direct test of the Vector Store Connector ---")
    
    pc_client = get_pinecone_client()
    
    if pc_client:
        print("Pinecone client initialized successfully.")
        index = get_pinecone_index(pc_client, config.PINECONE_INDEX_NAME)
        
        if index:
            stats = index.describe_index_stats()
            print(f"\nSuccessfully connected to index '{config.PINECONE_INDEX_NAME}'.")
            print(f"Index Stats: {stats}")
            print("\n✅ Vector Store connection test successful.")
        else:
            print("\n❌ Failed to get or create the Pinecone index.")
    else:
        print("\n❌ Vector Store connection failed. Check your API key.")