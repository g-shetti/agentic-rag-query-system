from db.neo4j_driver import Neo4jConnection

def create_index():
    driver = Neo4jConnection.get_driver()

    with driver.session() as session:
        session.run("""
        CREATE VECTOR INDEX device_embeddings IF NOT EXISTS
        FOR (d:Device)
        ON d.embedding
        OPTIONS {
          indexConfig: {
            `vector.dimensions`: 384,
            `vector.similarity_function`: 'cosine'
          }
        }
        """)

        result = session.run("SHOW INDEXES YIELD name, type WHERE name = 'device_embeddings'")
        print("Indexes:", [r.data() for r in result])

        print("✅ Vector index created and verified")

if __name__ == "__main__":
    create_index()
