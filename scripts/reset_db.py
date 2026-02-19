from db.neo4j_driver import Neo4jConnection

def run_query(query, params=None):
    driver = Neo4jConnection.get_driver()
    with driver.session() as session:
        session.run(query, params or {})

def reset_db():
    query = """
    MATCH (n)
    DETACH DELETE n
    """
    run_query(query)

    print("✅ Database cleared")

def drop_constraints():
    # query = "SHOW CONSTRAINTS"

    drop_query = """
    DROP CONSTRAINT device_id_unique
    DROP CONSTRAINT location_name_unique
    """

    run_query(drop_query)

    # constraints = run_query(query)

    # if not constraints:
    #     print("No constraints found")
    #     return

    # for c in constraints:
    #     name = c["name"]
    #     drop_query = f"DROP CONSTRAINT {name} IF EXISTS"
    #     run_query(drop_query)

    print("✅ Constraints dropped")

def drop_indexes():
    query = "SHOW INDEXES"
    indexes = run_query(query)

    if not indexes:
        print("No indexes found")
        return


    for idx in indexes:
        name = idx["name"]

        # Skip system indexes
        if name.startswith("index_") or name.startswith("constraint_"):
            continue

        drop_query = f"DROP INDEX {name} IF EXISTS"
        run_query(drop_query)

    print("✅ Indexes dropped")

def reset_db_full():
    try:
        print("🔄 Dropping constraints...")
        drop_constraints()

        print("🔄 Dropping indexes...")
        drop_indexes()

        print("🔄 Deleting nodes...")
        run_query("MATCH (n) DETACH DELETE n")

        print("✅ Full database reset complete")

    except Exception as e:
        print(f"❌ Reset failed: {e}")

if __name__ == "__main__":
    reset_db_full()
