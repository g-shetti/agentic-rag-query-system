from db.neo4j_driver import Neo4jConnection

driver = Neo4jConnection.get_driver()

def run_cypher(query, params=None):
    with driver.session() as session:
        result = session.run(query, params or {})
        return [dict(r) for r in result]
