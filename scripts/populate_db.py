from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
)

def run_query(query, params=None):
    with driver.session() as session:
        session.run(query, params or {})

def create_devices():
    query = """
    CREATE
    (t:Device {device_id:'thermostat_1', device_type:'thermostat', location:'Living Room'}),
    (l1:Device {device_id:'light_1', device_type:'light', location:'Bedroom'}),
    (l2:Device {device_id:'light_2', device_type:'light', location:'Living Room'}),
    (m1:Device {device_id:'motion_1', device_type:'sensor', location:'Hallway'}),
    (m2:Device {device_id:'motion_2', device_type:'sensor', location:'Garage'}),
    (sp:Device {device_id:'speaker_1', device_type:'speaker', location:'Kitchen'}),
    (temp:Device {device_id:'temp_1', device_type:'sensor', location:'Bedroom'}),
    (plug:Device {device_id:'plug_1', device_type:'plug', location:'Kitchen'})
    """
    run_query(query)

def create_relationships():
    queries = [
        """
        MATCH (m:Device {device_id:'motion_1'}), (l:Device {device_id:'light_1'})
        CREATE (m)-[:TRIGGERS]->(l)
        """,
        """
        MATCH (sp:Device {device_id:'speaker_1'}), (l:Device {device_id:'light_2'})
        CREATE (sp)-[:CONTROLS]->(l)
        """,
        """
        MATCH (temp:Device {device_id:'temp_1'}), (t:Device {device_id:'thermostat_1'})
        CREATE (temp)-[:FEEDS_DATA_TO]->(t)
        """
    ]

    for q in queries:
        run_query(q)

if __name__ == "__main__":
    create_devices()
    create_relationships()
    print("Data inserted successfully!")
