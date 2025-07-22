import chromadb

def check_chromadb_connection(host: str, port: int):
    """Checks if a ChromaDB server is running at the given host and port."""
    try:
        client = chromadb.HttpClient(host=host, port=port)
        client.list_collections()
        print(f"Successfully connected to ChromaDB at {host}:{port}")
        return True
    except ConnectionError as e:
        print(f"Could not connect to ChromaDB at {host}:{port}. Error: {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred while connecting to ChromaDB: {e}")
        return False

# Example usage (ChromaDB host name & port)
check_chromadb_connection("localhost", 8000)

# Run this in terminal to quick check 
# curl http://localhost:8000/api/v2/heartbeat