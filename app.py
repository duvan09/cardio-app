from flask import Flask, render_template, request, redirect, url_for, jsonify # Se agregó jsonify
from bd.conexion import obtener_conexion 
import random
import requests # Cirugía CQR 1: Importación de la librería

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

# Cirugía CQR 2: Función puente para telemetría hacia FlexFit
def sincronizar_flexfit(min_fc, max_fc):
    url = "https://tu-dominio-flexfit.com/php_logic/telemetria_be.php"
    payload = {"fc_min": min_fc, "fc_max": max_fc}
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Fallo en enlace: {e}")

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
        
        # Cirugía CQR 3: Disparo de telemetría antes del redireccionamiento
        sincronizar_flexfit(reposo, ejercicio)
        
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

# AJUSTE PARA VERCEL
if __name__ == '__main__':
    app.run()