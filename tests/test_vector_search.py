from neo4j import GraphDatabase
from sentence_transformers import SentenceTransformer
import os
from dotenv import load_dotenv

load_dotenv()

# Load model
model = SentenceTransformer('all-MiniLM-L6-v2')

def create_embedding(text):
    if not text:
        text = "unknown"
    return model.encode(text).tolist()

# Neo4j connection
driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
)

query_text = "devices in bedroom"
embedding = create_embedding(query_text)

print("len", len(embedding))
print("type", type(embedding))

with driver.session() as session:
    result = session.run("""
    CALL db.index.vector.queryNodes(
        'device_embeddings',
        5,
        $embedding
    )
    YIELD node, score
    RETURN node.device_id AS id, score
    """, embedding=embedding)

    for r in result:
        print(r["id"], r["score"])
