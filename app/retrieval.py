from app.neo4j_db import run_cypher
from scripts.create_embeddings import create_embedding

def get_devices_by_location(location):
    return run_cypher("""
    MATCH (d:Device {location:$loc})
    RETURN d.device_id AS id, d.device_type AS type
    """, {"loc": location})

def get_triggered_devices():
    return run_cypher("""
    MATCH (s:Device {device_type:'sensor'})-[:TRIGGERS]->(d:Device)
    RETURN s.device_id AS sensor, d.device_id AS device
    """)

def get_controllers_of_lights():
    return run_cypher("""
    MATCH (c:Device)-[:CONTROLS]->(l:Device {device_type:'light'})
    RETURN c.device_id AS controller
    """)

def vector_search(question):
    embedding = create_embedding(question)

    return run_cypher("""
    CALL db.index.vector.queryNodes(
        'device_embeddings',
        5,
        $embedding
    )
    YIELD node, score
    RETURN node.device_id AS id, node.location AS location, score
    """, {"embedding": embedding})

def route_query(question):
    q = question.lower()

    if "similar" in q or "like" in q:
        return "vector"

    if "in" in q or "located" in q:
        return "hybrid"

    return "graph"


def vector_then_graph(session, embedding):
    result = session.run("""
    CALL db.index.vector.queryNodes('device_embeddings', 5, $embedding)
    YIELD node
    MATCH (node)-[r]->(related)
    RETURN node.device_id AS source, type(r) AS relation, related.device_id AS target
    """, embedding=embedding)

    return [r.data() for r in result]


def hybrid_search(question):
    embedding = create_embedding(question)

    return run_cypher("""
    CALL db.index.vector.queryNodes(
        'device_embeddings',
        5,
        $embedding
    )
    YIELD node AS d, score
    OPTIONAL MATCH (d)-[r]->(n)
    RETURN d.device_id AS device,
           d.location AS location,
           type(r) AS relation,
           n.device_id AS connected_device,
           score
    """, {"embedding": embedding})

def run_retrieval(session, question):
    route = route_query(question)
    embedding = create_embedding(question)

    if route == "vector":
        return vector_then_graph(session, embedding)

    elif route == "hybrid":
        return hybrid_search(session, "Bedroom", embedding)

    else:
        return run_cypher(session, question)
