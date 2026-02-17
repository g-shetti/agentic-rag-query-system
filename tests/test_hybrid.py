from neo4j import GraphDatabase
from app.retrieval import run_retrieval
import os
from dotenv import load_dotenv

load_dotenv()

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
)

question = "devices in bedroom"

with driver.session() as session:
    result = run_retrieval(session, question)
    print(result)
