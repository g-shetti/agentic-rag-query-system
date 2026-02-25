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
- device_type (string)
- location (string)
- state (string)
- description (string)
- manufacturer (string)

Valid device_type values:
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
- TRIGGERS              (sensor → light)
- FEEDS_DATA_TO         (sensor → thermostat)
- CONTROLS              (controller → device)
- POWERS                (plug → device)

Between Device and Location:
- MONITORS              (device → location)
- SECURES               (device → location)
- LOCATED_IN            (device → location)
- REGULATES             (thermostat → location)

----------------------------------------
CRITICAL RULES (STRICT)
----------------------------------------

1. NEVER invent new node labels, properties, or relationships.
2. ONLY use device_type values listed above.
3. NEVER use device_type = 'sensor', 'actuator', or 'controller'.
4. DO NOT use description for filtering if device_type is available.
5. ALWAYS use case-insensitive location filtering:

   toLower(d.location) = toLower('<location_from_question>')

----------------------------------------
DEVICE TYPE FILTERING RULES
----------------------------------------

• Sensor queries:
  s.device_type ENDS WITH '_sensor'

• Light queries:
  d.device_type = 'light'

• Thermostat queries:
  d.device_type = 'thermostat'

----------------------------------------
RETURN RULES (DETERMINISTIC)
----------------------------------------

1. Device-only queries:
   RETURN
       d.device_id AS device_id,
       d.location AS location,
       coalesce(d.state, 'unknown') AS state

2. Relationship queries between two devices:
   - Return BOTH devices using role-based aliases.
   - Include source device location and state.

   Example format:
   RETURN
       s.device_id AS sensor_id,
       d.device_id AS light_id,
       s.location AS location,
       coalesce(s.state, 'unknown') AS state

3. Relationship queries between device and location:
   RETURN
       d.device_id AS device_id,
       l.name AS location

4. NEVER return entire nodes.
5. NEVER include explanation or comments.
6. RETURN ONLY valid Cypher.
7. For relationship queries:
   - Return attributes of the TARGET device unless the question explicitly asks about the source.
   - The entity being listed in the question determines which node’s location and state to return.

----------------------------------------
SEMANTIC MAPPING
----------------------------------------

If question mentions:
- "trigger" → use TRIGGERS
- "feed data" → use FEEDS_DATA_TO
- "control" → use CONTROLS
- "power" → use POWERS
- "monitor" → use MONITORS
- "secure" → use SECURES
- "located in" → use LOCATED_IN
- "regulate" → use REGULATES

----------------------------------------
TASK
----------------------------------------

Convert the following question into Cypher.

Question:
{question}

Cypher:
"""