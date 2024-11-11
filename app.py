from flask import Flask, render_template, request, redirect, url_for, flash,session, jsonify
import pyodbc
from datetime import datetime, timedelta
import time

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Connection to SQL Server
def get_db_connection():
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 18 for SQL Server};'
        'SERVER=mssql-180519-0.cloudclusters.net,10034;'
        'DATABASE=Base_de_datos;'
        'UID=Admin;'
        'PWD=Db12345678;'
        'Encrypt=no;'  # Disable SSL only for testing
        'TrustServerCertificate=yes;'  # Trust the server's certificate
    )
    return conn

@app.route('/')
def form():
    return render_template('Login.html')

@app.route('/login')
def login():
    return render_template('Login.html')

@app.route('/principal')
def principal():
    return render_template('Principal.html')

@app.route('/cuentas')
def cuentas():
    return render_template('Cuentas.html')

@app.route('/movimientos')
def movimientos():
    return render_template('Movimientos.html')

@app.route('/estados_cuenta')
def estados_cuenta():
    return render_template('EstadosCuenta.html')

if __name__ == '__main__':
    app.run(debug=True)
