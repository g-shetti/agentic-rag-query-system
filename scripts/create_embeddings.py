from sentence_transformers import SentenceTransformer
from db.neo4j_driver import Neo4jConnection

# Load model
model = SentenceTransformer('all-MiniLM-L6-v2')

def create_embedding(text):
    if not text:
        text = "unknown device"   # fallback
    return model.encode(text).tolist()

def update_embeddings():
    driver = Neo4jConnection.get_driver()

    with driver.session() as session:

        result = session.run("""
        MATCH (d:Device)
        RETURN d.device_id AS id,
            d.description AS desc,
            d.device_type AS type,
            d.location AS location
        """)

        batch = []

        for record in result:
            device_id = record["id"]

            desc = record["desc"] or ""
            device_type = record["type"] or ""
            location = record["location"] or ""

            text = f"""
            Device: {device_type}
            Location: {location}
            Description: {desc}
            Use case: smart home automation
            """

            embedding = create_embedding(text)

            session.run("""
            MATCH (d:Device {device_id:$id})
            SET d.embedding = $embedding
            """, id=device_id, embedding=embedding)

            batch.append((device_id, embedding))

            print(f"Updated {device_id}")

        for device_id, embedding in batch:
            session.run("""
            MATCH (d:Device {device_id:$id})
            SET d.embedding = $embedding
            """, id=device_id, embedding=embedding)
            
if __name__ == "__main__":
    update_embeddings()
    print("Embeddings created!")
