from flask import Blueprint, request, jsonify
from datetime import datetime
import random
from config import neo4j_connection
import time 
# Crear el Blueprint para Sorteo
sorteo_bp = Blueprint('sorteo', __name__)

# ------------------------------------------
# Generar un sorteo automáticamente
# ------------------------------------------
@sorteo_bp.route('/neo4j/sorteo/auto', methods=['POST'])
def generate_sorteo_auto():
    start_time = time.time()
    """
    Genera un sorteo automáticamente con 8 números únicos aleatorios (0-255) y una fecha actual.
    """
    try:
        # Generar 8 números únicos aleatorios
        numeros = random.sample(range(0, 256), 8)

        # Usar la fecha actual
        fecha_actual = datetime.now().strftime("%Y-%m-%d")

        # Crear un ID único para el sorteo
        sorteo_id = int(datetime.now().timestamp())

        # Guardar el sorteo en Neo4j
        query = """
        CREATE (s:Sorteo {id: $id, numeros: $numeros, fecha: $fecha, frecuencia: "Semanal", name: "Sorteo Con Fe"})
        RETURN s
        """
        result = neo4j_connection.execute_query(query, {
            'id': sorteo_id,
            'numeros': numeros,
            'fecha': fecha_actual
        })
        end_time = time.time()
        elapsed_time_ms = (end_time - start_time) * 1000
        return jsonify({
            'status': 'success',
            'message': 'Sorteo generado automáticamente con éxito',
            'data': {
                'id': sorteo_id,
                'numeros': numeros,
                'fecha': fecha_actual
            },
            'time_elapsed_ms': elapsed_time_ms
        }), 201
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@sorteo_bp.route('/neo4j/sorteos', methods=['GET'])
def obtener_sorteos():
    start_time = time.time()
    try:
        query = "MATCH (s:Sorteo) RETURN s ORDER BY s.id DESC LIMIT 1"
        sorteos = neo4j_connection.execute_query(query)
        end_time = time.time()
        elapsed_time_ms = (end_time - start_time) * 1000
        print("Sorteos obtenidos desde Neo4j:", sorteos)  # Log para depuración

        return jsonify({
            'status': 'success',
            'sorteos': [
                {
                    'id': sorteo['s']['id'],
                    'numeros': sorteo['s']['numeros'],  # Verifica que esto sea una lista
                    'fecha': sorteo['s']['fecha']
                } for sorteo in sorteos
            ],
            'time_elapsed_ms': elapsed_time_ms
        }), 200
    except Exception as e:
        print("Error al obtener sorteos:", e)  # Log para depuración
        return jsonify({'status': 'error', 'message': str(e)}), 500
    

@sorteo_bp.route('/neo4j/sorteo/<int:sorteo_id>', methods=['PUT'])
def actualizar_sorteo(sorteo_id):
    start_time = time.time()
    """
    Actualiza los números o la fecha de un sorteo específico.
    """
    try:
        data = request.json
        nuevos_numeros = data.get('numeros')
        nueva_fecha = data.get('fecha')

        # Verificar si el sorteo existe
        query_verificar = "MATCH (s:Sorteo {id: $sorteo_id}) RETURN s"
        resultado = neo4j_connection.execute_query(query_verificar, {'sorteo_id': sorteo_id})

        if not resultado:
            return jsonify({'status': 'error', 'message': 'Sorteo no encontrado'}), 404

        # Actualizar el sorteo
        query_actualizar = """
        MATCH (s:Sorteo {id: $sorteo_id})
        SET s.numeros = $numeros, s.fecha = $fecha
        RETURN s
        """
        actualizado = neo4j_connection.execute_query(query_actualizar, {
            'sorteo_id': sorteo_id,
            'numeros': nuevos_numeros,
            'fecha': nueva_fecha
        })
        end_time = time.time()
        elapsed_time_ms = (end_time - start_time) * 1000
        return jsonify({'status': 'success', 'message': 'Sorteo actualizado correctamente', 'sorteo': actualizado,'time_elapsed_ms': elapsed_time_ms}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@sorteo_bp.route('/neo4j/sorteo/<int:sorteo_id>', methods=['DELETE'])
def eliminar_sorteo(sorteo_id):
    start_time = time.time()
    """
    Elimina un sorteo específico por su ID.
    """
    try:
        # Verificar si el sorteo existe
        query_verificar = "MATCH (s:Sorteo {id: $sorteo_id}) RETURN s"
        resultado = neo4j_connection.execute_query(query_verificar, {'sorteo_id': sorteo_id})

        if not resultado:
            return jsonify({'status': 'error', 'message': 'Sorteo no encontrado'}), 404

        # Eliminar el sorteo y todas sus relaciones
        query_eliminar = "MATCH (s:Sorteo {id: $sorteo_id}) DETACH DELETE s"
        neo4j_connection.execute_query(query_eliminar, {'sorteo_id': sorteo_id})

        end_time = time.time()
        elapsed_time_ms = (end_time - start_time) * 1000

        return jsonify({'status': 'success', 'message': f'Sorteo {sorteo_id} eliminado con éxito','time_elapsed_ms': elapsed_time_ms}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
