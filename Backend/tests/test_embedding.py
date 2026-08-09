from clients.chroma_client import get_chroma_client

chroma_client = get_chroma_client()

collection = chroma_client.get_collection()

print("Count:", collection.count())

result = collection.peek(limit=3)

print(result)