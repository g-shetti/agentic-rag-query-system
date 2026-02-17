from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
)

def get_devices(tx):
    result = tx.run("MATCH (d:Device) RETURN d.device_id AS id")
    return [record["id"] for record in result]

with driver.session() as session:
    devices = session.execute_read(get_devices)
    print(devices)
