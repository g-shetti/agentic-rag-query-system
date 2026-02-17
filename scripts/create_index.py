import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
)

def create_index():
    with driver.session() as session:
        session.run("""
        CREATE VECTOR INDEX device_embeddings
        FOR (d:Device)
        ON d.embedding
        OPTIONS {
          indexConfig: {
            `vector.dimensions`: 384,
            `vector.similarity_function`: 'cosine'
          }
        }
        """)

        print("✅ Vector index created")

if __name__ == "__main__":
    create_index()
