from flask import Flask, render_template, request, flash
import subprocess
import re
import logging

# Configuración básica de logging
#logging.basicConfig(filename='email_check.log', level=logging.INFO,
#                    format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Necesario para manejar mensajes flash

def validate_email(email):
    """
    Valida el formato del correo electrónico usando una expresión regular simple.
    """
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return bool(re.match(email_regex, email))

def check_email(email):
    """
    Ejecuta el comando holehe con el email dado y captura la salida.
    Filtra las líneas que contienen "[+]" para mostrar solo los resultados encontrados.
    """
    try:
        # Ejecuta el comando con un tiempo límite de 30 segundos
        result = subprocess.run(["holehe", email], capture_output=True, text=True, timeout=30)

        # Verificar si la ejecución fue exitosa
        if result.returncode == 0:
            logging.info(f'Consulta exitosa para {email}')
            # Filtrar las líneas que contienen "[+]" y excluir las que contienen "[-]" o "[x]"
            found_lines = [
                line for line in result.stdout.splitlines() 
                if "[+]" in line and not any(exclude in line for exclude in ["[-]", "[x]"])
            ]
            total_results = len(found_lines)

            if found_lines:
                return f"Se encontraron {total_results} resultados:\n" + "\n".join(found_lines)
            else:
                return "No se encontraron resultados."
        else:
            logging.error(f'Error al ejecutar el comando para {email}: {result.stderr}')
            return f"Error al ejecutar el comando: {result.stderr}"

    except subprocess.TimeoutExpired:
        logging.error(f'Tiempo de espera excedido para {email}')
        return "Error: El tiempo de espera fue excedido."
    
    except Exception as e:
        logging.error(f'Error inesperado para {email}: {str(e)}')
        return f"Error inesperado: {str(e)}"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        email = request.form.get('email')

        # Validar el formato del correo
        if not validate_email(email):
            flash('El formato del correo electrónico es inválido. Por favor, inténtalo de nuevo.', 'error')
            return render_template('index.html')

        # Ejecutar la consulta de email con holehe
        flash(f"Realizando consulta para el correo: {email}...", 'info')
        response = check_email(email)

        return render_template('index.html', response=response)

    return render_template('index.html')

if __name__ == '__main__':
    print("Iniciando servidor en http://127.0.0.1:5001")
    app.run(debug=True, port=5001)

