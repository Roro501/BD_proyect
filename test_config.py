from config import neo4j_connection

# ------------------------------------------
# Prueba de conexión a Neo4j
# ------------------------------------------
try:
    query = "MATCH (n) RETURN n LIMIT 5"
    results = neo4j_connection.execute_query(query)
    print("Resultados de Neo4j:", results)
except Exception as e:
    print("Error al conectar a Neo4j:", e)
finally:
    neo4j_connection.close()


