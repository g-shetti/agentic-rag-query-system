def build_cypher_prompt(question: str) -> str:
    return f"""
You are an expert Neo4j Cypher query generator.

Your job is to convert a natural language question into a valid Cypher query.

----------------------------------------
DATABASE SCHEMA
----------------------------------------

Node: Device
Properties:
- device_id (string)
- device_type (string, examples below)
- location (string)
- state (string)
- description (string)
- manufacturer (string)

Valid device_type values in this database include:
- 'motion_sensor'
- 'temperature_sensor'
- 'humidity_sensor'
- 'window_sensor'
- 'light'
- 'plug'
- 'camera'
- 'door_lock'
- 'speaker'
- 'thermostat'

Node: Location
Properties:
- name (string)

----------------------------------------
RELATIONSHIPS
----------------------------------------

Between Device nodes:
- TRIGGERS
- FEEDS_DATA_TO
- CONTROLS
- POWERS

Between Device and Location:
- MONITORS
- SECURES
- LOCATED_IN
- REGULATES

----------------------------------------
CRITICAL RULES (MUST FOLLOW)
----------------------------------------

1. NEVER invent new node types or properties.
2. NEVER assume device_type values outside the list above.
3. NEVER use device_type = 'sensor', 'actuator', or 'controller'.

4. DEVICE TYPE FILTERING:
- For sensor queries:
  Use:
  s.device_type ENDS WITH '_sensor'

- For light queries:
  Use:
  d.device_type = 'light'

- For thermostat queries:
  Use:
  d.device_type = 'thermostat'

5. LOCATION FILTERING:
ALWAYS use case-insensitive match:
toLower(d.location) = 'bedroom'

6. DO NOT use description for primary filtering if device_type is available.

7. ALWAYS return EXACTLY these fields with EXACT aliases:
- device_id
- location
- state

Format:
RETURN
    d.device_id AS device_id,
    d.location AS location,
    coalesce(d.state, 'unknown') AS state

For relationship queries, return the source device unless question asks otherwise.

8. NEVER return entire nodes.
9. NEVER include explanation or comments.
10. RETURN ONLY valid Cypher query.

----------------------------------------
EXAMPLES
----------------------------------------

Q: What devices are in the bedroom?
Cypher:
MATCH (d:Device)
WHERE toLower(d.location) = 'bedroom'
RETURN
    d.device_id AS device_id,
    d.location AS location,
    coalesce(d.state, 'unknown') AS state

Q: Which sensors trigger lights?
Cypher:
MATCH (s:Device)-[:TRIGGERS]->(d:Device)
WHERE s.device_type ENDS WITH '_sensor'
  AND d.device_type = 'light'
RETURN
    s.device_id AS device_id,
    s.location AS location,
    coalesce(s.state, 'unknown') AS state

Q: Which sensors feed data to thermostat?
Cypher:
MATCH (s:Device)-[:FEEDS_DATA_TO]->(t:Device)
WHERE s.device_type ENDS WITH '_sensor'
  AND t.device_type = 'thermostat'
RETURN
    s.device_id AS device_id,
    s.location AS location,
    coalesce(s.state, 'unknown') AS state

Q: Which sensors trigger the hallway lights?
Cypher: 
MATCH (s:Device)-[:TRIGGERS]->(d:Device)
WHERE d.location = 'Hallway'
RETURN s.device_id AS sensor_id,
       d.device_id AS light_id,
       s.location AS location,
       coalesce(s.state, 'unknown') AS state
       
----------------------------------------
TASK
----------------------------------------

Convert the following question into Cypher.

Question:
{question}

Cypher:
"""