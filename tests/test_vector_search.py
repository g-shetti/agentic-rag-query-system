from sentence_transformers import SentenceTransformer
from db.neo4j_driver import Neo4jConnection

# Load model
model = SentenceTransformer('all-MiniLM-L6-v2')

def create_embedding(text):
    if not text:
        text = "unknown"
    return model.encode(text).tolist()

query_text = "devices in bedroom"
embedding = create_embedding(query_text)

print("len", len(embedding))
print("type", type(embedding))

driver = Neo4jConnection.get_driver()

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
