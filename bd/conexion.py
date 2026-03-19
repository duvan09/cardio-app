import mysql.connector

def obtener_conexion():
    return mysql.connector.connect(
        host="gateway01.us-east-1.prod.aws.tidbcloud.com",
        port=4000,
        user="4S882MfCP4hD7vD.root", 
        password="BxJbsuH9aY5vXFNl",
        database="sistema_cardio",
        autocommit=True
    )