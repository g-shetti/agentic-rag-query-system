from db.neo4j_driver import Neo4jConnection

def get_devices(tx):
    result = tx.run("MATCH (d:Device) RETURN d.device_id AS id")
    return [record["id"] for record in result]

driver = Neo4jConnection.get_driver()

with driver.session() as session:
    devices = session.execute_read(get_devices)
    print(devices)
