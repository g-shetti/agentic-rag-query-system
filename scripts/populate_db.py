from db.neo4j_driver import Neo4jConnection

def run_query(query, params=None):
    driver = Neo4jConnection.get_driver()

    with driver.session() as session:
        session.run(query, params or {})

def create_constraints():
    queries = [
        """
        CREATE CONSTRAINT device_id_unique IF NOT EXISTS
        FOR (d:Device)
        REQUIRE d.device_id IS UNIQUE
        """,
        """
        CREATE CONSTRAINT location_name_unique IF NOT EXISTS
        FOR (l:Location)
        REQUIRE l.name IS UNIQUE
        """
    ]

    for q in queries:
        run_query(q)

def create_devices():
    query = """
    MERGE (t1:Device {device_id:'thermostat_1'})
    SET t1.device_type = 'thermostat',
        t1.location = 'Living Room',
        t1.state = '22C',
        t1.manufacturer = 'Nest'

    MERGE (l1:Device {device_id:'light_1'})
    SET l1.device_type = 'light',
        l1.location = 'Bedroom',
        l1.state = 'off',
        l1.manufacturer = 'Philips'

    MERGE (l2:Device {device_id:'light_2'})
    SET l2.device_type = 'light',
        l2.location = 'Living Room',
        l2.state = 'on',
        l2.manufacturer = 'Philips'

    MERGE (l3:Device {device_id:'light_3'})
    SET l3.device_type = 'light',
        l3.location = 'Kitchen',
        l3.state = 'off',
        l3.manufacturer = 'Philips'

    MERGE (m1:Device {device_id:'motion_1'})
    SET m1.device_type = 'motion_sensor',
        m1.location = 'Hallway',
        m1.state = 'inactive',
        m1.manufacturer = 'Aqara'

    MERGE (m2:Device {device_id:'motion_2'})
    SET m2.device_type = 'motion_sensor',
        m2.location = 'Garage',
        m2.state = 'inactive',
        m2.manufacturer = 'Aqara'

    MERGE (dl1:Device {device_id:'doorlock_1'})
    SET dl1.device_type = 'door_lock',
        dl1.location = 'Front Door',
        dl1.state = 'locked',
        dl1.manufacturer = 'Yale'

    MERGE (c1:Device {device_id:'camera_1'})
    SET c1.device_type = 'camera',
        c1.location = 'Front Door',
        c1.state = 'active',
        c1.manufacturer = 'Ring'

    MERGE (c2:Device {device_id:'camera_2'})
    SET c2.device_type = 'camera',
        c2.location = 'Backyard',
        c2.state = 'active',
        c2.manufacturer = 'Ring'

    MERGE (sp1:Device {device_id:'speaker_1'})
    SET sp1.device_type = 'speaker',
        sp1.location = 'Kitchen',
        sp1.state = 'idle',
        sp1.manufacturer = 'Amazon'

    MERGE (ts1:Device {device_id:'temp_1'})
    SET ts1.device_type = 'temperature_sensor',
        ts1.location = 'Bedroom',
        ts1.state = '24C',
        ts1.manufacturer = 'Nest'

    MERGE (ts2:Device {device_id:'temp_2'})
    SET ts2.device_type = 'temperature_sensor',
        ts2.location = 'Living Room',
        ts2.state = '22C',
        ts2.manufacturer = 'Nest'

    MERGE (p1:Device {device_id:'plug_1'})
    SET p1.device_type = 'plug',
        p1.location = 'Kitchen',
        p1.state = 'on',
        p1.manufacturer = 'TP-Link'

    MERGE (p2:Device {device_id:'plug_2'})
    SET p2.device_type = 'plug',
        p2.location = 'Bedroom',
        p2.state = 'off',
        p2.manufacturer = 'TP-Link'

    MERGE (h1:Device {device_id:'humidity_1'})
    SET h1.device_type = 'humidity_sensor',
        h1.location = 'Bathroom',
        h1.state = '45%',
        h1.manufacturer = 'Xiaomi'

    MERGE (w1:Device {device_id:'window_1'})
    SET w1.device_type = 'window_sensor',
        w1.location = 'Bedroom',
        w1.state = 'closed',
        w1.manufacturer = 'Aqara'

    MERGE (w2:Device {device_id:'window_2'})
    SET w2.device_type = 'window_sensor',
        w2.location = 'Living Room',
        w2.state = 'open',
        w2.manufacturer = 'Aqara'
    """
    run_query(query)

def create_locations():
    query = """
    MERGE (lr:Location {name:'Living Room'})
    MERGE (br:Location {name:'Bedroom'})
    MERGE (kt:Location {name:'Kitchen'})
    MERGE (hw:Location {name:'Hallway'})
    MERGE (gr:Location {name:'Garage'})
    MERGE (fd:Location {name:'Front Door'})
    MERGE (by:Location {name:'Backyard'})
    MERGE (bt:Location {name:'Bathroom'})
    """
    run_query(query)

def create_relationships():
    queries = [

        # ---------------------------
        # TRIGGERS (Automation)
        # ---------------------------
        """
        MATCH (m:Device {device_id:'motion_1'}), (l:Device {device_id:'light_2'})
        MERGE (m)-[:TRIGGERS {strength:0.9, created_at:timestamp()}]->(l)
        """,
        """
        MATCH (m:Device {device_id:'motion_2'}), (l:Device {device_id:'light_3'})
        MERGE (m)-[:TRIGGERS {strength:0.9, created_at:timestamp()}]->(l)
        """,

        # ---------------------------
        # FEEDS DATA
        # ---------------------------
        """
        MATCH (t:Device {device_id:'temp_1'}), (th:Device {device_id:'thermostat_1'})
        MERGE (t)-[:FEEDS_DATA_TO {strength:0.8, created_at:timestamp()}]->(th)
        """,
        """
        MATCH (t:Device {device_id:'temp_2'}), (th:Device {device_id:'thermostat_1'})
        MERGE (t)-[:FEEDS_DATA_TO {strength:0.8, created_at:timestamp()}]->(th)
        """,

        # ---------------------------
        # CONTROLS
        # ---------------------------
        """
        MATCH (sp:Device {device_id:'speaker_1'}), (l:Device {device_id:'light_2'})
        MERGE (sp)-[:CONTROLS {strength:0.7, created_at:timestamp()}]->(l)
        """,
        """
        MATCH (sp:Device {device_id:'speaker_1'}), (l:Device {device_id:'light_3'})
        MERGE (sp)-[:CONTROLS {strength:0.7, created_at:timestamp()}]->(l)
        """,

        # ---------------------------
        # MONITORS
        # ---------------------------
        """
        MATCH (c:Device {device_id:'camera_1'}), (fd:Location {name:'Front Door'})
        MERGE (c)-[:MONITORS {strength:0.7, created_at:timestamp()}]->(fd)
        """,
        """
        MATCH (c:Device {device_id:'camera_2'}), (by:Location {name:'Backyard'})
        MERGE (c)-[:MONITORS {strength:0.7, created_at:timestamp()}]->(by)
        """,

        # ---------------------------
        # SECURES
        # ---------------------------
        """
        MATCH (dl:Device {device_id:'doorlock_1'}), (fd:Location {name:'Front Door'})
        MERGE (dl)-[:SECURES {strength:0.7, created_at:timestamp()}]->(fd)
        """,

        # ---------------------------
        # POWERS
        # ---------------------------
        """
        MATCH (p:Device {device_id:'plug_1'}), (sp:Device {device_id:'speaker_1'})
        MERGE (p)-[:POWERS {strength:0.6, created_at:timestamp()}]->(sp)
        """,

        # ---------------------------
        # LOCATED IN
        # ---------------------------
        """
        MATCH (m:Device {device_id:'motion_1'}), (hw:Location {name:'Hallway'})
        MERGE (m)-[:LOCATED_IN {strength:0.7, created_at:timestamp()}]->(hw)
        """,
        """
        MATCH (m:Device {device_id:'motion_2'}), (gr:Location {name:'Garage'})
        MERGE (m)-[:LOCATED_IN {strength:0.7, created_at:timestamp()}]->(gr)
        """,
        """
        MATCH (t:Device {device_id:'thermostat_1'}), (lr:Location {name:'Living Room'})
        MERGE (t)-[:LOCATED_IN {strength:0.7, created_at:timestamp()}]->(lr)
        """,
        # ---------------------------
        # REGULATES
        # ---------------------------
        """
        MATCH (t:Device {device_id:'thermostat_1'}), (lr:Location {name:'Living Room'})
        MERGE (t)-[:REGULATES {strength:0.7, created_at:timestamp()}]->(lr)
        """
    ]

    for q in queries:
        run_query(q)

DESCRIPTIONS = {
    "thermostat": "Controls temperature",
    "light": "Smart light for illumination",
    "motion_sensor": "Detects motion",
    "camera": "Monitors area",
    "door_lock": "Secures entry",
    "speaker": "Voice controlled smart speaker",
    "temperature_sensor": "Measures temperature",
    "humidity_sensor": "Measures humidity",
    "plug": "Controls power supply",
    "window_sensor": "Detects window state"
}

def update_device_descriptions():
    driver = Neo4jConnection.get_driver()
    with driver.session() as session:
        session.run("""
        MATCH (d:Device)
        SET d.description =
            d.device_type + " in " + d.location +
            " manufactured by " + coalesce(d.manufacturer, "unknown") +
            " currently " + coalesce(d.state, "unknown")
        """)

def setup_graph():
    try:
        print("Creating constraints...")
        create_constraints()

        print("Creating devices...")
        create_devices()

        print("Creating locations...")
        create_locations()

        print("Creating relationships...")
        create_relationships()

        print("Adding descriptions...")
        update_device_descriptions()

        print("✅ Data inserted successfully!")

    except Exception as e:
        print("❌ Error during graph setup:", str(e))

if __name__ == "__main__":
    setup_graph()
