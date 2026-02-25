from services.embedding_service import EmbeddingService
from db.neo4j_driver import Neo4jConnection

embedding_service = EmbeddingService()


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

            embedding = embedding_service.embed(text)

            session.run("""
            MATCH (d:Device {device_id:$id})
            SET d.embedding = $embedding
            """, id=device_id, embedding=embedding)

            print(f"Updated {device_id}")

    print("✅ Embeddings created!")


if __name__ == "__main__":
    update_embeddings()