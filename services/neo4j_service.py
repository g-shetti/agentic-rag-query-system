from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

class Neo4jService:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            os.getenv("NEO4J_URI"),
            auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
        )

    def close(self):
        self.driver.close()

    def run_query(self, query):
        with self.driver.session() as session:
            result = session.run(query)
            return [record.data() for record in result]

    def vector_search(self, embedding, top_k=5):
        query = """
        CALL db.index.vector.queryNodes('device_embeddings', $top_k, $embedding)
        YIELD node, score
        RETURN node.device_id AS id,
            node.device_type AS type,
            node.location AS location,
            score
        """

        with self.driver.session() as session:
            result = session.run(query, {
                "embedding": embedding,
                "top_k": top_k
            })

            return [record.data() for record in result]