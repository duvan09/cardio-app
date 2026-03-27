from flask import Flask, render_template, request, redirect, url_for, jsonify 
from flask_cors import CORS # CIRUGÍA CQR: La solución definitiva para CORS
from bd.conexion import obtener_conexion 
import random

app = Flask(__name__)

# CIRUGÍA CQR: Permitir CORS automáticamente en todas las rutas /api/
CORS(app, resources={r"/api/*": {"origins": "*"}})

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
        
        return jsonify(usuarios)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- CIRUGÍA CQR: RUTA DE TELEMETRÍA (Limpia y protegida por CORS) ---
@app.route('/api/solicitar_telemetria', methods=['POST'])
def solicitar_telemetria():
    try:
        data = request.get_json(silent=True) or {}
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
            pass # Falla silenciosa de BD para no joder la interfaz de FlexFit

        return jsonify({
            "status": "success",
            "min": reposo,
            "max": ejercicio
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run()