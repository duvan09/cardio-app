from flask import Flask, render_template, request, redirect, url_for
from bd.conexion import obtener_conexion 
import random

app = Flask(__name__)

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
        # Esto te ayudará a ver qué pasa si falla la conexión en la nube
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

# AJUSTE PARA VERCEL: Sin debug=True para producción
if __name__ == '__main__':
    app.run()