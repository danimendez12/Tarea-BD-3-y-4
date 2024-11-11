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
        'DATABASE=Tarea3;'
        'UID=Admin;'
        'PWD=Db12345678;'
        'Encrypt=no;'  # Disable SSL only for testing
        'TrustServerCertificate=yes;'  # Trust the server's certificate
    )
    return conn

@app.route('/')
def form():
    return render_template('Login.html')


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                DECLARE @OutResult INT;
                EXEC dbo.ValidarUsuario @Username=?, @Password=?, @OutResult=@OutResult OUTPUT;
                SELECT @OutResult AS OutResult;
            """, (username, password))

            row = cursor.fetchone()
            out_result = row.OutResult

            if out_result == 0:

                session['username'] = username
                print("se ha iniciado sesión: ", username, password)

                return redirect(url_for('inicio'))

            else:
                print("Error, inténtelo de nuevo")

        except Exception as e:
            print("Error en la base de datos:", {str(e)})

        finally:
            cursor.close()
            conn.close()

    return render_template('Login.html')

@app.route('/inicio')
def inicio():

    if 'username' not in session:
        print("Por favor, inicia sesión primero.")
        return redirect(url_for('login'))

    return render_template('Inicio.html')


@app.route('/cuentas')
def cuentas():

    if 'username' not in session:
        flash("Por favor, inicia sesión primero.", "error")
        return redirect(url_for('login'))

    username = session['username']

    conn = get_db_connection()
    cursor = conn.cursor()

    cuentas_list = []
    out_result = None

    try:

        # Ejecuta el procedimiento almacenado
        cursor.execute("""
            DECLARE @OutResult INT;
            EXEC dbo.ListarCuentas @NombreUsuario = ?, @outResult = @OutResult OUTPUT;
            SELECT @OutResult AS outResult;
        """, (username,))

        cuentas_list = cursor.fetchall()

        cursor.nextset()
        out_result = cursor.fetchone()[0]

        print(f"Valor de out_result: {out_result}")
        print("Cuentas obtenidas:", cuentas_list)

        if out_result != 0:
            print("No se pudieron obtener las cuentas del tarjetahabiente.")

    except Exception as e:
        print("Error al obtener cuentas:", {str(e)})

    finally:
        cursor.close()
        conn.close()

    return render_template('Cuentas.html', cuentas=cuentas_list)


@app.route('/movimientos')
def movimientos():
    return render_template('Movimientos.html')

@app.route('/estados_cuenta')
def estados_cuenta():
    return render_template('EstadosCuenta.html')

#*****************************ADMINISTRADOR*************************************

@app.route('/admin')
def admin():
    return render_template('AdminInicio.html')

if __name__ == '__main__':
    app.run(debug=True)
