from flask import Blueprint, request, jsonify
from config import neo4j_connection
import random
import time 
# Crear Blueprint para Dueño
dueño_bp = Blueprint('dueño', __name__)

# POST - Registro de Dueño
@dueño_bp.route('/neo4j/registro', methods=['POST'])
def registrar_dueno():
    start_time = time.time()
    data = request.json
    if not data or 'nombre' not in data or 'dni' not in data or 'apellido' not in data or 'fechaNacimiento' not in data:
        elapsed_time = (time.time() - start_time) * 1000
        return jsonify({'status': 'error', 'message': 'Datos incompletos', 'tiempo_ms': elapsed_time}), 400

    try:
        query_check = """
        MATCH (d:Dueño {nombre: $nombre})
        RETURN d
        """
        result = neo4j_connection.execute_query(query_check, {'nombre': data['nombre']})
        if result:
            elapsed_time = (time.time() - start_time) * 1000
            return jsonify({'status': 'error', 'message': 'El nombre ya está registrado', 'tiempo_ms': elapsed_time}), 400

        dueño_id = random.randint(1, 100000)
        query = """
        CREATE (d:Dueño {
            id: $id,
            nombre: $nombre,
            dni: $dni,
            apellido: $apellido,
            fechaNacimiento: $fechaNacimiento
        })
        RETURN d
        """
        neo4j_connection.execute_query(query, {
            'id': dueño_id,
            'nombre': data['nombre'],
            'dni': data['dni'],
            'apellido': data['apellido'],
            'fechaNacimiento': data['fechaNacimiento']
        })
        elapsed_time = (time.time() - start_time) * 1000
        return jsonify({'status': 'success', 'message': 'Dueño registrado con éxito', 'tiempo_ms': elapsed_time}), 201
    except Exception as e:
        elapsed_time = (time.time() - start_time) * 1000
        return jsonify({'status': 'error', 'message': str(e), 'tiempo_ms': elapsed_time}), 500


# GET - Inicio de sesión
@dueño_bp.route('/neo4j/login', methods=['GET'])
def login_dueno():
    start_time = time.time()
    nombre = request.args.get('nombre')
    if not nombre:
        elapsed_time = (time.time() - start_time) * 1000
        return jsonify({'status': 'error', 'message': 'El nombre es obligatorio', 'tiempo_ms': elapsed_time}), 400

    try:
        query = """
        MATCH (d:Dueño {nombre: $nombre})
        RETURN d
        """
        result = neo4j_connection.execute_query(query, {'nombre': nombre})
        elapsed_time = (time.time() - start_time) * 1000
        if result:
            if nombre.lower() == "root":
                return jsonify({
                    'status': 'success',
                    'message': 'Bienvenido, root',
                    'redirect': 'admin_dashboard',
                    'tiempo_ms': elapsed_time
                }), 200
            else:
                return jsonify({
                    'status': 'success',
                    'message': 'Inicio de sesión exitoso',
                    'redirect': 'user_dashboard',
                    'tiempo_ms': elapsed_time
                }), 200
        else:
            return jsonify({'status': 'error', 'message': 'Nombre no registrado', 'tiempo_ms': elapsed_time}), 404
    except Exception as e:
        elapsed_time = (time.time() - start_time) * 1000
        return jsonify({'status': 'error', 'message': str(e), 'tiempo_ms': elapsed_time}), 500



@dueño_bp.route('/neo4j/dueño', methods=['PUT'])
def actualizar_dueño():
    start_time = time.time()
    try:
        data = request.json
        nombre_actual = data.get('nombre_actual')
        nuevo_nombre = data.get('nuevo_nombre')
        nuevo_apellido = data.get('nuevo_apellido')

        if not nombre_actual:
            elapsed_time = (time.time() - start_time) * 1000
            return jsonify({'status': 'error', 'message': 'El nombre actual es obligatorio', 'tiempo_ms': elapsed_time}), 400

        query = """
        MATCH (d:Dueño {nombre: $nombre_actual})
        SET d.nombre = COALESCE($nuevo_nombre, d.nombre),
            d.apellido = COALESCE($nuevo_apellido, d.apellido)
        RETURN d
        """
        result = neo4j_connection.execute_query(query, {
            'nombre_actual': nombre_actual,
            'nuevo_nombre': nuevo_nombre,
            'nuevo_apellido': nuevo_apellido
        })

        elapsed_time = (time.time() - start_time) * 1000
        if not result:
            return jsonify({'status': 'error', 'message': 'No se encontró el dueño.'}), 404

        return jsonify({'status': 'success', 'message': 'Información actualizada correctamente', 'data': result, 'time_elapsed_ms': elapsed_time}), 200
    except Exception as e:
        elapsed_time = (time.time() - start_time) * 1000
        return jsonify({'status': 'error', 'message': str(e), 'tiempo_ms': elapsed_time}), 500

    


# DELETE - Eliminar un Dueño por nombre
@dueño_bp.route('/neo4j/dueño', methods=['DELETE'])
def eliminar_dueno():
    start_time = time.time()
    try:
        data = request.json
        nombre = data.get('nombre')

        if not nombre:
            elapsed_time = (time.time() - start_time) * 1000
            return jsonify({'status': 'error', 'message': 'El nombre es obligatorio', 'time_elapsed_ms': elapsed_time}), 400

        query = "MATCH (d:Dueño {nombre: $nombre}) DETACH DELETE d"
        neo4j_connection.execute_query(query, {'nombre': nombre})

        elapsed_time = (time.time() - start_time) * 1000
        return jsonify({'status': 'success', 'message': f'Dueño {nombre} eliminado con éxito', 'time_elapsed_ms': elapsed_time}), 200
    except Exception as e:
        elapsed_time = (time.time() - start_time) * 1000
        return jsonify({'status': 'error', 'message': str(e), 'time_elapsed_ms': elapsed_time}), 500
