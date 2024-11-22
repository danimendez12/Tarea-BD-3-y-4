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

        out_result = 0
        user_type = ''

        try:
            cursor.execute("""
                DECLARE @OutResult INT, @UserType NVARCHAR(64);
                EXEC dbo.ValidarUsuario ?, ?, @OutResult OUTPUT, @UserType OUTPUT;
                SELECT @OutResult AS OutResult, @UserType AS UserType;
            """, (username, password))

            result = cursor.fetchone()
            out_result = result.OutResult
            user_type = result.UserType

            if out_result == 0:

                session['username'] = username
                session['user_type'] = user_type

                print("se ha iniciado sesión: ", username, password)

                return redirect(url_for('inicio'))

            else:
                print("Error, inténtelo de nuevo")
                return render_template('Login.html', error='Usuario o contraseña incorrectos.')

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

    nombre_usuario = session['username']
    user_type = session.get('user_type')
    conn = get_db_connection()
    cursor = conn.cursor()

    tarjetas = []

    try:

        if user_type == 'Admin':
            cursor.execute("EXEC dbo.ListarTFADMIN")
        elif user_type == 'TH':
            cursor.execute("EXEC dbo.ListarTF @NombreUsuario = ?", (nombre_usuario,))
        else:
            print("Tipo de usuario no válido")
            return redirect(url_for('login'))

        tarjetas = [
            {
                'numero': row.NumeroTarjeta,
                'estado': row.EstadoTarjeta,
                'tipo_cuenta': row.TipoCuenta,
                'fecha_venc': row.FechaVencimiento
            }
            for row in cursor.fetchall()
        ]

    except Exception as e:
        print("Error al obtener tarjetas:", {str(e)})

    finally:
        cursor.close()
        conn.close()

    return render_template('Inicio.html', tarjetas=tarjetas)

@app.route('/estados_cuenta/<int:codigo_tarjeta>/<string:tipo_cuenta>')
def estados_cuenta(codigo_tarjeta, tipo_cuenta):

    conn = get_db_connection()
    cursor = conn.cursor()

    estados = []
    cuenta_tipo = "Desconocido"

    try:
        print(codigo_tarjeta)
        if tipo_cuenta.lower() == 'maestra':
            print('cuenta maestra')
            cursor.execute("EXEC dbo.ListarEC @CodigoTarjeta=?", (codigo_tarjeta,))
            estados = cursor.fetchall()
            cuenta_tipo = "Estado de Cuenta"
        else:
            print('cuenta adicional')
            cursor.execute("EXEC dbo.ListarSubEC @CodigoTarjeta=?", (int(codigo_tarjeta),))
            estados = cursor.fetchall()
            for estado in estados:
                print(estado)
            cuenta_tipo = "Sub Estado de Cuenta"

        conn.commit()

    except Exception as e:
        print("Error al obtener estados de cuenta:", e)

    finally:
        cursor.close()
        conn.close()

    return render_template('EstadosCuenta.html', estados=estados, cuenta_tipo=cuenta_tipo,codigo_tarjeta=codigo_tarjeta)


@app.route('/movimientos/<int:codigo_tarjeta>/<string:tipo_cuenta>')
def movimientos(codigo_tarjeta, tipo_cuenta):
    conn = get_db_connection()
    cursor = conn.cursor()

    movimientos = []

    try:
        cursor.execute("EXEC dbo.ListarMovimientos @CodigoTarjeta = ?, @TipoCuenta = ?",
                       (codigo_tarjeta, tipo_cuenta))
        movimientos = cursor.fetchall()
        for movimiento in movimientos:
            print(movimiento)

    except Exception as e:
        print("Error al obtener movimientos:", e)

    finally:
        cursor.close()
        conn.close()

    return render_template('Movimientos.html', movimientos=movimientos, tipo_cuenta=tipo_cuenta)


if __name__ == '__main__':
    app.run(debug=True)