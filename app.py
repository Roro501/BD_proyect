from flask import Flask, render_template
from sorteo import sorteo_bp
from dueño import dueño_bp
from ticket import ticket_bp
from ganador import ganador_bp
from config import neo4j_connection
import os
# Crear la aplicación Flask
app = Flask(__name__)

# Registrar los Blueprints
app.register_blueprint(sorteo_bp)
app.register_blueprint(dueño_bp)
app.register_blueprint(ticket_bp)
app.register_blueprint(ganador_bp)

# ------------------------------------------
# Cierre de conexión a Neo4j
# ------------------------------------------
@app.teardown_appcontext
def close_neo4j_connection(exception=None):
    """
    Cierra la conexión a Neo4j al finalizar el contexto de la aplicación.
    """
    try:
        if 'neo4j_connection' in globals() and neo4j_connection:
            neo4j_connection.close()
    except Exception as e:
        print(f"Error al cerrar la conexión de Neo4j: {e}")


# ------------------------------------------
# Ruta para servir el HTML (Inicio de Sesión)
# ------------------------------------------
@app.route('/')
def index():
    return render_template('inicio.html')  # Asegúrate de que inicio.html esté en la carpeta /static o /templates

@app.route('/registro.html')
def registro():
    return render_template('registro.html')

@app.route('/ticket.html')
def ticket():
    return render_template('ticket.html')

@app.route('/sorteo.html')
def sorteo_page():
    return render_template('sorteo.html')

# ------------------------------------------
# Inicialización del servidor
# ------------------------------------------
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Usa el puerto 5000 por defecto
    app.run(host='0.0.0.0', port=port)


