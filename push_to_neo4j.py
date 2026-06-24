import json
import os
from neo4j import GraphDatabase

# =====================================================================
# 1. CONFIGURE YOUR CREDENTIALS
# Replace these strings with the details from your downloaded text file
# =====================================================================
NEO4J_URI = "neo4j+ssc://503a041c.databases.neo4j.io" 
NEO4J_USERNAME = "503a041c"
NEO4J_PASSWORD = "1Si-0kQAFHDpXi0TM0lOadvCZgPsbMh1pBerhvN3K5I"


# 2. Establish connection to the cloud database instance
print("Connecting to Neo4j AuraDB...")
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

# 3. Read your automated pipeline output
print("Reading 'automated_graph_data.json'...")
try:
    with open('automated_graph_data.json', 'r') as file:
        graph_data = json.load(file)
except FileNotFoundError:
    print("Error: 'automated_graph_data.json' not found in this directory.")
    exit()

# 4. Define the Cypher Execution Blueprint
def insert_graph_data(tx, data_block):
    # Step A: Create or update the TextWitness (Source tracking/Provenance)
    tx.run("""
        MERGE (source:TextWitness {uri: $source_url})
        """, source_url=data_block["source_url"]
    )
    
    # Step B: Create an 'Assertion' node representing the action/relation
    # and map it directly back to its source text lineage
    tx.run("""
        MATCH (source:TextWitness {uri: $source_url})
        MERGE (event:Assertion {relation: $relation})
        MERGE (event)-[:SUPPORTED_BY]->(source)
        """, source_url=data_block["source_url"], relation=data_block["relation"]
    )
    
    # Step C: Iterate through entities and attach them using Paninian Karaka roles
    for entity in data_block.get("entities", []):
        tx.run("""
            MATCH (event:Assertion {relation: $relation})
            MERGE (e:Entity {name: $name})
            SET e.type = $type
            
            // Map grammatical case role relationship
            MERGE (e)-[r:ACTS_AS {karaka_role: $role}]->(event)
            """, 
            relation=data_block["relation"],
            name=entity["name"], 
            type=entity["type"], 
            role=entity["karaka_role"]
        )

# 5. Run the transaction loop across your dataset
print("Pushing data nodes and relationship edges to Neo4j...")
try:
    with driver.session() as session:
        for block in graph_data:
            session.execute_write(insert_graph_data, block)
    print("\nSuccessfully populated the Knowledge Graph!")
except Exception as e:
    print(f"\nDatabase Ingestion Failed: {e}")
finally:
    driver.close()
    print("Database driver connection closed safely.")