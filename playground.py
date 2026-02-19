from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')
print('model = ', model)
embeddings = model.encode(["Hello world"])
print('embeddings = ', embeddings)
