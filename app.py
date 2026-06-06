from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)

#Conectar BASE DE DATOS, uri del .env
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')

#Apagar avisos de SQLAIchemy
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#Crea la BD y pasa la aplicacion
db = SQLAlchemy(app)

class Estudiante(db.Model):
    __tablename__ = 'estudiantes' 
    id = db.Column(db.Integer, primary_key=True)
    documento = db.Column(db.String(20), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    
    
    correo_electronico = db.Column(db.String(120), unique=True, nullable=False)
    programa_formacion = db.Column(db.String(100), nullable=False)
    ficha = db.Column(db.String(50), nullable=False)

    def to_dict(self):
        # Esta pequeña función será nuestra "traductora"
        # Nos ayudará a convertir los datos de la BD en un formato JSON para el usuario
        return {
            "id": self.id,
            "documento": self.documento,
            "nombre": self.nombre,
            "correo_electronico": self.correo_electronico,
            "programa_formacion": self.programa_formacion,
            "ficha": self.ficha
        }

# Contexto de la aplicación para crear las tablas automáticamente
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

#ENDPOINT de registro
@app.route('/estudiantes' , methods=['POST'])
def registrar_estudiante():
    #1.Atrapamos los datos del JSON
    datos = request.json

    #2. VALIDACION 

    # Lista de los campos que son obligatorios en nuestra base de datos
    campos_requeridos = ['documento', 'nombre', 'correo_electronico', 'programa_formacion', 'ficha']

   # Recorremos la lista y verificamos si cada campo está dentro de 'datos'
    for campo in campos_requeridos:
        if campo not in datos:
            
            return jsonify({"error": f"Falta el dato obligatorio: {campo}"}), 400

    #CONTROL DE EXCEPCIONES
    try:
        nuevo = Estudiante(documento=datos['documento'], 
                           nombre=datos['nombre'], 
                           correo_electronico=datos['correo_electronico'],
                           programa_formacion=datos['programa_formacion'],
                           ficha=datos['ficha']
                           )
        #GUARDAMOS EN LA DB
        db.session.add(nuevo)
        db.session.commit()
        return jsonify({"mensaje": "Estudiante registrado exitosamente"}), 201
    
    except Exception as e: 
      # se activa esta alarma. ¡Esto es lo que te dará el pantallazo del error!
        db.session.rollback() # Cancelamos cualquier transacción a medias
        return jsonify({
            "error": "Ocurrió un error inesperado al guardar en la base de datos.",
            "detalle": str(e)
        }), 500  

# ENDPOINT GET (Requisito 3: Consultar todos los estudiantes)
@app.route('/estudiantes', methods=['GET'])
def obtener_estudiantes():
    try:
        # Le pedimos al ORM que traiga todos los registros de la tabla
        estudiantes = Estudiante.query.all()
        # Transformamos cada objeto a diccionario usando la función que creaste en el modelo
        lista_estudiantes = [estudiante.to_dict() for estudiante in estudiantes]
        return jsonify(lista_estudiantes), 200
    except Exception as e:
        return jsonify({"error": "Error al consultar la base de datos", "detalle": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
