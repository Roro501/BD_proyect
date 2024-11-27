from neo4j import GraphDatabase

# Configuración para la base de datos Neo4j
NEO4J_URI = "bolt://3.94.59.126:7687"  # URL de conexión
NEO4J_AUTH = ("neo4j", "detents-commander-enclosures")   # Credenciales de Neo4j

# Clase para manejar la conexión con Neo4j
class Neo4jConnection:
    def __init__(self, uri, user, password):
        """
        Inicializa la conexión al servidor de Neo4j.
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        """
        Cierra la conexión al servidor de Neo4j.
        """
        self.driver.close()

    def execute_query(self, query, parameters=None):
        """
        Ejecuta una consulta en Neo4j y devuelve los resultados.
        """
        with self.driver.session() as session:
            result = session.run(query, parameters)
            return [record.data() for record in result]

# Instancia de la conexión a Neo4j
neo4j_connection = Neo4jConnection(NEO4J_URI, *NEO4J_AUTH)

