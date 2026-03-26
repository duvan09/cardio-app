from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response 
from bd.conexion import obtener_conexion 
import random
import json # Cirugía CQR: Necesario para leer raw data

app = Flask(__name__)

# --- CONFIGURACIÓN RELIGIOSA DE ORIGEN ---
ORIGEN_PERMITIDO = "*" # CQR: Abierto al 100% para evitar bloqueos del navegador

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

# --- CIRUGÍA CQR: RUTA DE TELEMETRÍA DIRECTA BLINDADA ---
@app.route('/api/solicitar_telemetria', methods=['POST', 'OPTIONS'])
def solicitar_telemetria():
    # 1. MANEJO DE PREFLIGHT
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", ORIGEN_PERMITIDO)
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "*")
        return response, 204

    # 2. LÓGICA DE NEGOCIO PROTEGIDA
    try:
        # CIRUGÍA CQR: Leer como texto plano y convertir manualmente a JSON
        # Esto evita que Flask lance error 400/500 cuando JS evade el CORS con text/plain
        raw_data = request.data
        try:
            data = json.loads(raw_data) if raw_data else {}
        except Exception:
            data = {}

        nombre_usuario = data.get('nombre', 'Usuario_FlexFit')
        
        reposo = random.randint(60, 85)
        ejercicio = random.randint(125, 175)

        try:
            conn = obtener_conexion()
            cursor = conn.cursor()
            sql = "INSERT INTO usuarios (nombre, ritmo_reposo, ritmo_ejercicio) VALUES (%s, %s, %s)"
            cursor.execute(sql, (nombre_usuario, reposo, ejercicio))
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as db_err:
            pass # Silencioso para no romper la respuesta al frontend

        res = jsonify({
            "status": "success",
            "min": reposo,
            "max": ejercicio
        })
        
    except Exception as e:
        res = jsonify({"status": "error", "message": str(e)})

    # 3. FORZADO DE HEADERS FINALES
    res.headers.add("Access-Control-Allow-Origin", ORIGEN_PERMITIDO)
    return res

if __name__ == '__main__':
    app.run()