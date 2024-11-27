from flask import Blueprint, request, jsonify
from config import neo4j_connection
import random

# Crear Blueprint para Ganador
ganador_bp = Blueprint('ganador', __name__)

# POST - Registrar ganadores basados en coincidencias de Ticket y Sorteo
@ganador_bp.route('/neo4j/ganadores', methods=['POST'])
@ganador_bp.route('/neo4j/ganadores', methods=['POST'])
def registrar_ganadores():
    import time
    start_time = time.time()
    try:
        # Obtener el nombre del dueño desde la solicitud
        data = request.json
        dueño_nombre = data.get('dueño_nombre')

        if not dueño_nombre:
            return jsonify({'status': 'error', 'message': 'Nombre del usuario no proporcionado'}), 400

        # Obtener el ticket más reciente del dueño
        ticket_query = """
        MATCH (d:Dueño {nombre: $dueño_nombre})-[:COMPRA]->(t:Ticket)
        RETURN t ORDER BY t.fechaCompra DESC LIMIT 1
        """
        ticket_result = neo4j_connection.execute_query(ticket_query, {'dueño_nombre': dueño_nombre})

        if not ticket_result:
            return jsonify({'status': 'error', 'message': 'No se encontraron tickets para este dueño'}), 404

        ticket = ticket_result[0]['t']  # Último ticket
        numeros_ticket = ticket['numeros']

        # Obtener el último sorteo generado
        sorteo_query = "MATCH (s:Sorteo) RETURN s ORDER BY s.id DESC LIMIT 1"
        sorteo_result = neo4j_connection.execute_query(sorteo_query)

        if not sorteo_result:
            return jsonify({'status': 'error', 'message': 'No hay sorteos disponibles'}), 404

        sorteo = sorteo_result[0]['s']  # Último sorteo
        numeros_sorteo = sorteo['numeros']

        # Verificar coincidencias entre números del ticket y números del sorteo
        coincidencias = set(numeros_ticket).intersection(set(numeros_sorteo))

        if not coincidencias:
            return jsonify({
                'status': 'success',
                'message': 'No hay coincidencias entre el ticket y el sorteo más reciente'
            }), 200

        # Crear nodo Ganador y relaciones SOLO SI HAY COINCIDENCIAS
        dinero_ganado = random.randint(1000, 10000)  # Premio aleatorio
        ganador_id = int(random.uniform(1, 100000))  # ID único
        ganador_query = """
        MATCH (s:Sorteo {id: $sorteo_id})
        MATCH (d:Dueño {nombre: $dueño_nombre})
        CREATE (g:Ganador {id: $ganador_id, dineroGanado: $dinero_ganado}),
               (d)-[:GANADOR_DE]->(g),
               (g)-[:EN]->(s)
        RETURN g
        """
        ganador_result = neo4j_connection.execute_query(ganador_query, {
            'sorteo_id': sorteo['id'],
            'dueño_nombre': dueño_nombre,
            'ganador_id': ganador_id,
            'dinero_ganado': dinero_ganado
        })

        end_time = time.time()
        elapsed_time_ms = (end_time - start_time) * 1000

        return jsonify({
            'status': 'success',
            'message': f'¡Felicidades! {dueño_nombre} ha ganado.',
            'coincidencias': list(coincidencias),
            'dinero_ganado': dinero_ganado,
            'tiempo_ms': elapsed_time_ms
        }), 200
    except Exception as e:
        end_time = time.time()
        elapsed_time_ms = (end_time - start_time) * 1000
        return jsonify({'status': 'error', 'message': str(e), 'tiempo_ms': elapsed_time_ms}), 500


