from app.retrieval import run_retrieval
from db.neo4j_driver import Neo4jConnection

question = "devices in bedroom"

driver = Neo4jConnection.get_driver()

with driver.session() as session:
    result = run_retrieval(session, question)
    print(result)
