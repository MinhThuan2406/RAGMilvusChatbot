from pymilvus import connections

def check_milvus_connection(host: str, port: int):
    """Checks if a Milvus server is running at the given host and port."""
    try:
        connections.connect(host=host, port=port)
        print(f"Successfully connected to Milvus at {host}:{port}")
        return True
    except Exception as e:
        print(f"Could not connect to Milvus at {host}:{port}. Error: {e}")
        return False

# Example usage (Milvus host name & port)
import os
host = os.getenv("MILVUS_HOST", "milvus-db")
port = int(os.getenv("MILVUS_PORT", 19530))
check_milvus_connection(host, port)