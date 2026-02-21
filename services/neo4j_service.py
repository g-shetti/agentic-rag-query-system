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

    def run_query(self, query, params=None):
        try:
            with self.driver.session() as session:
                result = session.run(query, params or {})
                return [record.data() for record in result]
        except Exception as e:
            raise Exception(f"Neo4j query failed: {str(e)}")

    def vector_search(self, embedding, top_k=5):
        query = """
        CALL db.index.vector.queryNodes('device_embeddings', $top_k, $embedding)
        YIELD node, score
        RETURN node.device_id AS device_id,
            node.device_type AS type,
            node.location AS location,
            node.description AS description,
            score
        """
        return self.run_query(query, {"embedding": embedding, "top_k": top_k})

    def get_device_state(self, device_id):
        query = """
        MATCH (d:Device {device_id:$id})
        RETURN d.device_id, d.state
        """
        return self.run_query(query, {"id": device_id})