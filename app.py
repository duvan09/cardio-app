from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response 
from bd.conexion import obtener_conexion 
import random

app = Flask(__name__)

# --- CONFIGURACIÓN RELIGIOSA DE ORIGEN ---
# Definimos el origen exacto de FlexFit para máxima seguridad CQR
ORIGEN_PERMITIDO = "http://flexfit-tm.infinityfreeapp.com"

@app.route('/')
def index():
    try:
        conn = obtener_conexion()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, nombre FROM usuarios")
        usuarios = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('index.html', usuarios=usuarios)
    except Exception as e:
        return f"Error de base de datos: {e}"

@app.route('/generar', methods=['POST'])
def generar():
    try:
        nombre = request.form['nombre']
        reposo = random.randint(60, 85)
        ejercicio = random.randint(125, 175)
        
        conn = obtener_conexion()
        cursor = conn.cursor()
        sql = "INSERT INTO usuarios (nombre, ritmo_reposo, ritmo_ejercicio) VALUES (%s, %s, %s)"
        cursor.execute(sql, (nombre, reposo, ejercicio))
        nuevo_id = cursor.lastrowid 
        conn.commit()
        cursor.close()
        conn.close()
        
        return redirect(url_for('detalle', id=nuevo_id))
    except Exception as e:
        return f"Error al generar: {e}"

@app.route('/usuario/<int:id>')
def detalle(id):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE id = %s", (id,))
        usuario = cursor.fetchone()
        cursor.close()
        conn.close()
        return render_template('detalle.html', usuario=usuario)
    except Exception as e:
        return f"Error al cargar detalle: {e}"

# --- NUEVA RUTA API PARA FLEXFIT (FORMATO JSON) ---
@app.route('/api/datos')
def api_datos():
    try:
        conn = obtener_conexion()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT nombre, ritmo_reposo, ritmo_ejercicio FROM usuarios")
        usuarios = cursor.fetchall()
        cursor.close()
        conn.close()
        
        resp = jsonify(usuarios)
        resp.headers.add('Access-Control-Allow-Origin', ORIGEN_PERMITIDO)
        return resp
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- CIRUGÍA CQR: RUTA DE TELEMETRÍA DIRECTA CON HEADERS DE SEGURIDAD ---
@app.route('/api/solicitar_telemetria', methods=['POST', 'OPTIONS'])
def solicitar_telemetria():
    # 1. Manejo del Preflight (OPTIONS)
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", ORIGEN_PERMITIDO)
        response.headers.add('Access-Control-Allow-Headers', "Content-Type, Authorization")
        response.headers.add('Access-Control-Allow-Methods', "POST, OPTIONS")
        response.headers.add('Access-Control-Allow-Credentials', "true")
        return response

    # 2. Lógica de Negocio (POST)
    try:
        data = request.get_json()
        nombre_usuario = data.get('nombre', 'Usuario_FlexFit') if data else 'Usuario_FlexFit'
        
        reposo = random.randint(60, 85)
        ejercicio = random.randint(125, 175)

        # Registro en base de datos sistema_cardio
        conn = obtener_conexion()
        cursor = conn.cursor()
        sql = "INSERT INTO usuarios (nombre, ritmo_reposo, ritmo_ejercicio) VALUES (%s, %s, %s)"
        cursor.execute(sql, (nombre_usuario, reposo, ejercicio))
        conn.commit()
        cursor.close()
        conn.close()

        # Respuesta exitosa con Headers CQR
        resp = jsonify({
            "status": "success", 
            "min": reposo, 
            "max": ejercicio,
            "mensaje": "Telemetría generada y guardada"
        })
        resp.headers.add('Access-Control-Allow-Origin', ORIGEN_PERMITIDO)
        resp.headers.add('Access-Control-Allow-Credentials', "true")
        return resp

    except Exception as e:
        resp = jsonify({"status": "error", "error": str(e)})
        resp.headers.add('Access-Control-Allow-Origin', ORIGEN_PERMITIDO)
        return resp, 500

if __name__ == '__main__':
    app.run()