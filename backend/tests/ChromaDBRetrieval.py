from pymilvus import connections, Collection

connections.connect(host="localhost", port=19530)
collection = Collection("docs")
print("Number of embeddings:", collection.num_entities)
results = collection.query(expr=None, limit=5)
print("Results:", results)