from flask import Blueprint, request, jsonify
from config import neo4j_connection
import random

# Crear Blueprint para Ganador
ganador_bp = Blueprint('ganador', __name__)

# POST - Registrar ganadores basados en coincidencias de Ticket y Sorteo
@ganador_bp.route('/neo4j/ganadores', methods=['POST'])
def registrar_ganadores():
    import time
    start_time = time.time()
    try:
        # Obtener el nombre del usuario desde la solicitud
        data = request.json
        dueño_nombre = data.get('dueño_nombre')

        if not dueño_nombre:
            return jsonify({'status': 'error', 'message': 'Nombre del usuario no proporcionado'}), 400

        # Obtener el último sorteo generado
        sorteo_query = "MATCH (s:Sorteo) RETURN s ORDER BY s.id DESC LIMIT 1"
        sorteo_result = neo4j_connection.execute_query(sorteo_query)

        if not sorteo_result:
            return jsonify({'status': 'error', 'message': 'No hay sorteos disponibles'}), 400

        sorteo = sorteo_result[0]['s']
        numeros_sorteo = sorteo['numeros']
        sorteo_id = sorteo['id']

        # Buscar tickets del usuario actual cuyos números coincidan con el sorteo
        ticket_query = """
        MATCH (t:Ticket)<-[:COMPRA]-(d:Dueño {nombre: $dueño_nombre})
        WHERE any(num IN t.numeros WHERE num IN $numeros_sorteo)
        RETURN t, d
        """
        tickets = neo4j_connection.execute_query(ticket_query, {
            'dueño_nombre': dueño_nombre,
            'numeros_sorteo': numeros_sorteo
        })

        if not tickets:
            return jsonify({'status': 'error', 'message': 'No hay ganadores para este sorteo'}), 200

        # Procesar cada ticket ganador
        ganadores = []
        for ticket in tickets:
            dueño = ticket['d']  # Nodo Dueño
            ticket_nodo = ticket['t']  # Nodo Ticket

            # Generar datos para el nodo Ganador
            dinero_ganado = random.randint(1000, 10000)  # Premio aleatorio
            ganador_id = int(random.uniform(1, 100000))  # ID único

            # Crear un nodo Ganador y establecer relaciones
            ganador_query = """
            MATCH (s:Sorteo {id: $sorteo_id})
            MATCH (d:Dueño {nombre: $dueño_nombre})
            CREATE (g:Ganador {id: $ganador_id, dineroGanado: $dinero_ganado}),
                   (d)-[:GANADOR_DE]->(g),
                   (g)-[:EN]->(s)
            RETURN g
            """
            ganador_result = neo4j_connection.execute_query(ganador_query, {
                'sorteo_id': sorteo_id,
                'dueño_nombre': dueño_nombre,
                'ganador_id': ganador_id,
                'dinero_ganado': dinero_ganado
            })

            if ganador_result:
                ganadores.append({
                    'dueño': {
                        'nombre': dueño['nombre'],
                        'apellido': dueño.get('apellido'),  # Incluye el apellido
                        'dni': dueño.get('dni')  # Incluye el DNI
                    },
                    'ticket': ticket_nodo,
                    'sorteo': sorteo,
                    'dinero_ganado': dinero_ganado
                })

        end_time = time.time()
        elapsed_time_ms = (end_time - start_time) * 1000

        return jsonify({
            'status': 'success',
            'message': 'Ganadores registrados correctamente',
            'ganadores': ganadores
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


