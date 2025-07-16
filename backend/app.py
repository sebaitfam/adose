from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import jwt
import datetime
import os
from dotenv import load_dotenv
from db_connection import get_connection  # 👈 Importas la conexión de la base datos

load_dotenv()

frontend_build_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

# Servir archivos estáticos (JS, CSS, imágenes)
app = Flask(__name__, static_folder=frontend_build_dir, static_url_path='/')
CORS(app)

# Ruta principal para servir index.html
@app.route('/')
def serve_frontend():
    return send_from_directory(frontend_build_dir, 'index.html')

# Ruteo para cualquier otro path que no sea API o uploads (React Router funciona)
@app.errorhandler(404)
def not_found(e):
    return send_from_directory(frontend_build_dir, 'index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)


SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("SECRET_KEY no está definida")

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    usuario = data.get('usuario')
    password = data.get('password')

    conn = get_connection()
    if conn is None:
        return jsonify({"success": False, "message": "Error al conectar a la base de datos"}), 700

    cursor = conn.cursor()
    cursor.execute(
        "SELECT ID_Usuario, Usuario, Nombre, Apellido, Rol, Email, foto_perfil FROM usuarios WHERE Usuario=%s AND Passwords=%s",
        (usuario, password)
    )
    resultado = cursor.fetchone()
    cursor.close()
    conn.close()

    if resultado:
        nombre_completo = f"{resultado[2]} {resultado[3]}"
        payload = {
            'usuario_id': resultado[0],
            'usuario': resultado[1],  # Nombre de usuario (login)
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        return jsonify({
            "success": True,
            "token": token,
            "userType": resultado[4],
            "nombreUsuario": nombre_completo,
            "usuario": resultado[1],
            "emailUsuario": resultado[5],
            "fotoPerfil": resultado[6],
            "usuario_id": resultado[0]  # <-- AGREGA ESTA LÍNEA
        }), 200
    else:
        return jsonify({"success": False, "message": "Credenciales inválidas"}), 401

@app.route('/api/upload_foto', methods=['POST'])
def upload_foto():
    usuario_id = request.form.get('usuario_id')
    file = request.files.get('foto')
    if not usuario_id or not file:
        return jsonify({"success": False, "message": "Faltan datos"}), 400

    # 1. Busca la foto anterior en la base de datos
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT foto_perfil FROM usuarios WHERE ID_Usuario=%s", (usuario_id,))
    result = cursor.fetchone()
    foto_anterior = result[0] if result else None

    # 2. Elimina la foto anterior si existe y no es None/vacía
    if foto_anterior:
        ruta_anterior = os.path.join(UPLOAD_FOLDER, foto_anterior)
        if os.path.exists(ruta_anterior):
            try:
                os.remove(ruta_anterior)
            except Exception as e:
                print(f"Error eliminando la foto anterior: {e}")

    # 3. Guarda la nueva foto
    filename = f"user_{usuario_id}.jpg"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    # 4. Actualiza la base de datos con el nuevo nombre de archivo
    cursor.execute("UPDATE usuarios SET foto_perfil=%s WHERE ID_Usuario=%s", (filename, usuario_id))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"success": True, "foto_perfil": filename}), 200

# Endpoint para obtener la foto (opcional, si no sirves estáticos)
@app.route('/uploads/<filename>')
def get_foto(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)