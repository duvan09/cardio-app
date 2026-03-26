from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response # Cirugía CQR: Se agregó make_response
from bd.conexion import obtener_conexion 
import random

app = Flask(__name__)

# --- TUS RUTAS ORIGINALES (SIN CAMBIOS) ---

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
        # Traemos todos los datos necesarios para FlexFit
        cursor.execute("SELECT nombre, ritmo_reposo, ritmo_ejercicio FROM usuarios")
        usuarios = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Esto devuelve los datos en formato JSON puro
        return jsonify(usuarios)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- CIRUGÍA CQR: RUTA DE TELEMETRÍA DIRECTA PARA FLEXFIT ---
@app.route('/api/solicitar_telemetria', methods=['POST', 'OPTIONS'])
def solicitar_telemetria():
    # Manejo religioso de CORS usando make_response()
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response

    try:
        data = request.get_json()
        nombre_usuario = data.get('nombre', 'Usuario_FlexFit') # Captura el nombre enviado por JS
        
        reposo = random.randint(60, 85)
        ejercicio = random.randint(125, 175)

        # Guardamos en la BD de Cardio App para mantener el registro
        conn = obtener_conexion()
        cursor = conn.cursor()
        sql = "INSERT INTO usuarios (nombre, ritmo_reposo, ritmo_ejercicio) VALUES (%s, %s, %s)"
        cursor.execute(sql, (nombre_usuario, reposo, ejercicio))
        conn.commit()
        cursor.close()
        conn.close()

        # Devolvemos los datos directamente al JS de FlexFit
        resp = jsonify({
            "status": "success", 
            "min": reposo, 
            "max": ejercicio,
            "mensaje": "Telemetría generada y guardada"
        })
        resp.headers.add('Access-Control-Allow-Origin', '*')
        return resp

    except Exception as e:
        resp = jsonify({"status": "error", "error": str(e)})
        resp.headers.add('Access-Control-Allow-Origin', '*')
        return resp, 500

# AJUSTE PARA VERCEL
if __name__ == '__main__':
    app.run()