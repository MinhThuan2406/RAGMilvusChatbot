import chromadb

client = chromadb.HttpClient(host="localhost", port=8000)

collections = client.list_collections()
print("Collections:", collections)
collection = client.get_collection("docs")
print("Number of embeddings:", collection.count())

results = collection.get(limit=5)
print("Results:", results)