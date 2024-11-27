from flask import Blueprint, request, jsonify
from flask import Blueprint, request, jsonify
from config import neo4j_connection
from datetime import datetime
import random
import time
# Crear Blueprint para Ticket
ticket_bp = Blueprint('ticket', __name__)

# POST - Obtener ticket (Dueño)
@ticket_bp.route('/neo4j/ticket', methods=['POST'])
def create_ticket():
    start_time = time.time()
    data = request.json
    if not data or 'dueño_nombre' not in data:
        return jsonify({'status': 'error', 'message': 'Datos incompletos'}), 400

    try:
        # Generar información del ticket
        numeros = random.sample(range(0, 256), 8)
        fecha_compra = datetime.now().strftime("%Y-%m-%d")
        ticket_id = int(datetime.now().timestamp())

        # Crear ticket y conectarlo con el Dueño por nombre
        query = """
        MATCH (d:Dueño {nombre: $nombre})
        CREATE (t:Ticket {id: $id, numeros: $numeros, fechaCompra: $fecha}),
               (d)-[:COMPRA]->(t)
        RETURN t
        """
        result = neo4j_connection.execute_query(query, {
            'nombre': data['dueño_nombre'],
            'id': ticket_id,
            'numeros': numeros,
            'fecha': fecha_compra
        })
        
        end_time = time.time()
        elapsed_time_ms = (end_time - start_time) * 1000

        return jsonify({
            'status': 'success',
            'message': 'Ticket generado con éxito',
            'data': {'id': ticket_id, 'numeros': numeros, 'fechaCompra': fecha_compra},
            'time_elapsed_ms': elapsed_time_ms
        }), 201
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# DELETE - Eliminar el ticket más reciente del usuario actual
@ticket_bp.route('/neo4j/ticket/recent', methods=['DELETE'])
def eliminar_ticket_reciente():
    import time
    start_time = time.time()
    try:
        # Obtener el nombre del usuario desde la solicitud
        data = request.json
        dueño_nombre = data.get('dueño_nombre')

        if not dueño_nombre:
            return jsonify({'status': 'error', 'message': 'Nombre del usuario no proporcionado'}), 400

        # Buscar el ticket más reciente del usuario actual
        query_buscar_ticket = """
        MATCH (d:Dueño {nombre: $dueño_nombre})-[:COMPRA]->(t:Ticket)
        RETURN t ORDER BY t.fechaCompra DESC LIMIT 1
        """
        result = neo4j_connection.execute_query(query_buscar_ticket, {'dueño_nombre': dueño_nombre})

        if not result:
            return jsonify({'status': 'error', 'message': 'No se encontró el ticket más reciente'}), 404

        ticket_id = result[0]['t']['id']

        # Eliminar el ticket y la relación con el dueño
        query_eliminar_ticket = """
        MATCH (d:Dueño {nombre: $dueño_nombre})-[r:COMPRA]->(t:Ticket {id: $ticket_id})
        DELETE r, t
        """
        neo4j_connection.execute_query(query_eliminar_ticket, {'dueño_nombre': dueño_nombre, 'ticket_id': ticket_id})

        end_time = time.time()
        elapsed_time_ms = (end_time - start_time) * 1000

        return jsonify({
            'status': 'success',
            'message': f'Ticket con ID {ticket_id} eliminado correctamente',
            'time_elapsed_ms': elapsed_time_ms
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
