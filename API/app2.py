from flask import  Flask, render_template, request, redirect, url_for, jsonify, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import enum
from sqlalchemy.exc import SQLAlchemyError
from datetime import date
from datetime import datetime
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)

login_manager = LoginManager(app)
login_manager.login_view = 'login'



# Usa 'mysql+pymysql' si tienes PyMySQL instalado
app.config['SECRET_KEY'] = 'your_secret_key_here'
#cambiar el nombre de la base de dato a furgofinder
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/prueba'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app)
db = SQLAlchemy(app)


class Alumno(db.Model):
    __tablename__ = 'alumno'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre_completo = db.Column(db.String(255), nullable=False)
    rut = db.Column(db.String(20), unique=True, nullable=False)
    fecha_nacimiento = db.Column(db.Date, nullable=False)
    horario_entrada = db.Column(db.Time, nullable=False)
    horario_salida = db.Column(db.Time, nullable=False)
    curso = db.Column(db.String(50), nullable=False)
    direccion_hogar = db.Column(db.String(255), nullable=True)
    nombre_contacto_emergencia = db.Column(db.String(255), nullable=True)
    contacto_emergencia = db.Column(db.String(15), nullable=False)
    
    # Relaciones ManyToOne
    colegio_id = db.Column(db.Integer, db.ForeignKey('colegio.id'), nullable=False)
    colegio = db.relationship('Colegio', backref='alumnos_colegio')  # Cambiado el backref
    apoderado_id = db.Column(db.Integer, db.ForeignKey('apoderado.id'), nullable=False)
    sector_id = db.Column(db.Integer, db.ForeignKey('sector.id'), nullable=False)
    sector = db.relationship('Sector', backref='alumnos_sector')  # Cambiado el backref


class Apoderado(db.Model):
    __tablename__ = 'apoderado'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre_completo = db.Column(db.String(255), nullable=False)
    rut = db.Column(db.String(20), unique=True, nullable=False)  # Ejemplo: largo máximo de 20 para el RUT
    correo = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    direccion = db.Column(db.String(255), nullable=False)
    numero_telefono = db.Column(db.String(15), nullable=False)  # Ejemplo: largo máximo de 15 para un número de teléfono
    sexo = db.Column(db.String(10), nullable=True)  # Ejemplo: largo máximo de 10 para 'M'/'F' o 'Masculino'/'Femenino'
    rol = db.Column(db.String(50), nullable=True)  # Ejemplo: largo máximo de 50 para roles como 'Admin', 'User', etc.

    # Relaciones OneToMany
    alumnos = db.relationship('Alumno', backref='apoderado', cascade='all, delete-orphan', lazy=True)
    contratos = db.relationship('Contrato', backref='apoderado', cascade='all, delete-orphan', lazy=True)
    solicitudes = db.relationship('Solicitud', backref='apoderado', cascade='all, delete-orphan', lazy=True)
    # apoderado = db.relationship('Apoderado', backref='alumnos')
    # apoderado = db.relationship('Apoderado', backref='contratos')
    # apoderado = db.relationship('Apoderado', backref='solicitudes')


class Colegio(db.Model):
    __tablename__ = 'colegio'
    
    id = db.Column(db.Integer, primary_key=True)
    rbd = db.Column(db.String(20), nullable=True)  # Ejemplo: largo máximo de 20 para el RBD
    nombre_colegio = db.Column(db.String(255), nullable=True)
    direccion = db.Column(db.String(255), nullable=True)
    contacto = db.Column(db.String(15), nullable=True)  # Ejemplo: largo máximo de 15 para el número de contacto
    
    # Relación ManyToOne con Sector
    sector_id = db.Column(db.Integer, db.ForeignKey('sector.id'), nullable=False)
    sector = db.relationship('Sector', backref='colegios')


class Asistente(db.Model):
    __tablename__ = 'asistente'
    
    id = db.Column(db.Integer, primary_key=True)
    correo = db.Column(db.String(255), nullable=False)
    nombre_completo = db.Column(db.String(255), nullable=False)
    rut = db.Column(db.String(20), unique=True, nullable=False)  # Ejemplo: largo máximo de 20 para el RUT
    sexo = db.Column(db.String(10), nullable=True)  # Ejemplo: largo máximo de 10 para 'M'/'F' o 'Masculino'/'Femenino'
    telefono = db.Column(db.String(15), nullable=False)  # Ejemplo: largo máximo de 15 para el número de teléfono
    
    # Campo LOB (Large Object Binary) para la imagen
    image = db.Column(db.LargeBinary, nullable=True)
    
    # Relación ManyToOne con Conductor
    conductor_id = db.Column(db.Integer, db.ForeignKey('conductor.id'), nullable=False)
    # conductor = db.relationship('Conductor', backref='asistentes')
    
    # Relación OneToOne con Furgon
    furgon_id = db.Column(db.Integer, db.ForeignKey('furgon.id'), unique=True, nullable=True)
    furgon = db.relationship('Furgon', backref=db.backref('asistente', uselist=False))


class Conductor(db.Model):
    __tablename__ = 'conductor'
    id = db.Column(db.Integer, primary_key=True)
    nombre_completo = db.Column(db.String(255), nullable=False)
    rut = db.Column(db.String(20), unique=True, nullable=False)  # Ejemplo: largo máximo de 20 para el RUT
    correo = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    numero_telefono = db.Column(db.String(15), nullable=False)  # Ejemplo: largo máximo de 15 para el número de teléfono
    sexo = db.Column(db.String(10), nullable=True)  # Ejemplo: largo máximo de 10 para 'M'/'F' o 'Masculino'/'Femenino'
    rol = db.Column(db.String(50), nullable=True)  # Ejemplo: largo máximo de 50 para roles como 'Admin', 'User', etc.
    # Campo LOB (Large Object Binary) para la imagen
    image = db.Column(db.LargeBinary, nullable=True)
    # Relación OneToMany con Asistente
    asistentes = db.relationship('Asistente', backref='conductor', cascade='all, delete-orphan', lazy=True)



# Definición del enumerado para TipoDocumento
class TipoDocumentoEnum(enum.Enum):
    LICENCIA = "LICENCIA"
    SEGURO = "SEGURO"
    REVISION_TECNICA = "REVISION_TECNICA"
    # Añade otros tipos de documentos si es necesario

class DocumentoFurgon(db.Model):
    __tablename__ = 'documento_furgon'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Campo Enum para TipoDocumento
    tipo_documento = db.Column(db.Enum(TipoDocumentoEnum), nullable=False)
    
    # Campo LOB (Large Object Binary) para el archivo
    archivo = db.Column(db.LargeBinary, nullable=False)
    
    # Relación ManyToOne con Furgon
    furgon_id = db.Column(db.Integer, db.ForeignKey('furgon.id'), nullable=False)
    furgon = db.relationship('Furgon', backref='documentos')


class Furgon(db.Model):
    __tablename__ = 'furgon'
    
    id = db.Column(db.Integer, primary_key=True)
    patente = db.Column(db.String(20), unique=True, nullable=False)  # Ejemplo: largo máximo de 20 para la patente
    marca = db.Column(db.String(50), nullable=False)  # Ejemplo: largo máximo de 50 para la marca
    modelo = db.Column(db.String(50), nullable=False)  # Ejemplo: largo máximo de 50 para el modelo
    ano = db.Column(db.Integer, nullable=False)
    capacidad = db.Column(db.Integer, nullable=False)
    cupos_disponibles = db.Column(db.Integer, nullable=False)
    precio_base = db.Column(db.Float, nullable=False)
    validado = db.Column(db.Boolean, nullable=False)
    
    # Relaciones ManyToOne
    conductor_id = db.Column(db.Integer, db.ForeignKey('conductor.id'), nullable=False)
    #conductor = db.relationship('Conductor', backref='furgones')
    
    sector_id = db.Column(db.Integer, db.ForeignKey('sector.id'), nullable=False)
    #sector = db.relationship('Sector', backref='furgones')
    
    colegio_id = db.Column(db.Integer, db.ForeignKey('colegio.id'), nullable=False)
    #colegio = db.relationship('Colegio', backref='furgones')
    
    # Relaciones OneToMany
    contratos = db.relationship('Contrato', backref='furgon', cascade='all, delete-orphan', lazy=True)
    imagenes = db.relationship('ImagenFurgon', backref='furgon', cascade='all, delete-orphan', lazy=True)



class ImagenFurgon(db.Model):
    __tablename__ = 'imagen_furgon'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Campo LOB (Large Object Binary) para la imagen
    imagen = db.Column(db.LargeBinary, nullable=False)
    
    # Relación ManyToOne con Furgon
    furgon_id = db.Column(db.Integer, db.ForeignKey('furgon.id'), nullable=False)
    #furgon = db.relationship('Furgon', backref='imagenes')




class Calificacion(db.Model):
    __tablename__ = 'calificacion'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Relación ManyToOne con Apoderado
    apoderado_id = db.Column(db.Integer, db.ForeignKey('apoderado.id'), nullable=False)
    #apoderado = db.relationship('Apoderado', backref='calificaciones')
    
    # Relación ManyToOne con Conductor
    conductor_id = db.Column(db.Integer, db.ForeignKey('conductor.id'), nullable=False)
    #conductor = db.relationship('Conductor', backref='calificaciones')
    
    # Relación OneToOne con Contrato
    contrato_id = db.Column(db.Integer, db.ForeignKey('contrato.id'), nullable=False, unique=True)
    #contrato = db.relationship('Contrato', backref=db.backref('calificacion', uselist=False))
    
    puntuacion = db.Column(db.Integer, nullable=False)  # Puntuación numérica
    comentario = db.Column(db.String(500), nullable=True)  # Comentario con límite de 500 caracteres
    fecha_calificacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)  # F


class Contrato(db.Model):
    __tablename__ = 'contrato'
    
    id = db.Column(db.Integer, primary_key=True)
    direccion_establecimiento = db.Column(db.String(255), nullable=False)
    direccion_hogar = db.Column(db.String(255), nullable=False)
    fecha_contratacion = db.Column(db.Date, default=date.today, nullable=False)
    nombre_alumno = db.Column(db.String(255), nullable=False)
    nombre_apoderado = db.Column(db.String(255), nullable=False)
    rut_apoderado = db.Column(db.String(20), nullable=False)  # Ejemplo: largo máximo de 20 para el RUT
    nombre_establecimiento = db.Column(db.String(255), nullable=False)
    periodo = db.Column(db.String(50), nullable=False)  # Ejemplo: largo máximo de 50 para el periodo
    precio = db.Column(db.Float, nullable=False)
    estado = db.Column(db.String(50), nullable=False)  # Ejemplo: largo máximo de 50 para el estado del contrato
    tipo_servicio = db.Column(db.String(50), nullable=False)  # Ejemplo: largo máximo de 50 para el tipo de servicio
    nombre_contacto_emergencia = db.Column(db.String(255), nullable=False)
    numero_contacto_emergencia = db.Column(db.String(15), nullable=False)  # Ejemplo: largo máximo de 15 para el número de contacto

    # Relaciones ManyToOne
    furgon_id = db.Column(db.Integer, db.ForeignKey('furgon.id'), nullable=False)
    #furgon = db.relationship('Furgon', backref='contratos')
    
    conductor_id = db.Column(db.Integer, db.ForeignKey('conductor.id'), nullable=False)
    #conductor = db.relationship('Conductor', backref='contratos')
    
    apoderado_id = db.Column(db.Integer, db.ForeignKey('apoderado.id'), nullable=False)
    
    
    alumno_id = db.Column(db.Integer, db.ForeignKey('alumno.id'), nullable=False)
    #alumno = db.relationship('Alumno', backref='contratos')
    
    colegio_id = db.Column(db.Integer, db.ForeignKey('colegio.id'), nullable=False)
   # colegio = db.relationship('Colegio', backref='contratos')

class Documentos(db.Model):
    __tablename__ = 'documentos'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Campo LOB (Large Object Binary) para el contenido del documento
    contenido_documento = db.Column(db.LargeBinary, nullable=True)
    
    # Tipo de documento
    tipo_documento = db.Column(db.String(50), nullable=False)  # Ejemplo: largo máximo de 50 para el tipo de documento
    
    # Relación ManyToOne con Conductor
    conductor_id = db.Column(db.Integer, db.ForeignKey('conductor.id'), nullable=True)
    #conductor = db.relationship('Conductor', backref='documentos')
    
    # Relación ManyToOne con Asistente
    asistente_id = db.Column(db.Integer, db.ForeignKey('asistente.id'), nullable=True)
    #asistente = db.relationship('Asistente', backref='documentos')

class Notificacion(db.Model):
    __tablename__ = 'notificacion'
    
    id = db.Column(db.Integer, primary_key=True)
    mensaje = db.Column(db.String(255), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relación ManyToOne con Conductor
    conductor_destino_id = db.Column(db.Integer, db.ForeignKey('conductor.id'), nullable=True)
    #conductor_destino = db.relationship('Conductor', backref='notificaciones')
    
    # Relación ManyToOne con Apoderado
    apoderado_destino_id = db.Column(db.Integer, db.ForeignKey('apoderado.id'), nullable=True)
    #apoderado_destino = db.relationship('Apoderado', backref='notificaciones')


class Pago(db.Model):
    __tablename__ = 'pago'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Relación ManyToOne con Apoderado
    apoderado_id = db.Column(db.Integer, db.ForeignKey('apoderado.id'), nullable=False)
    apoderado = db.relationship('Apoderado', backref='pagos')
    
    # Relación OneToOne con Contrato
    contrato_id = db.Column(db.Integer, db.ForeignKey('contrato.id'), nullable=False, unique=True)
    contrato = db.relationship('Contrato', backref=db.backref('pago', uselist=False))
    
    monto = db.Column(db.Float, nullable=False)
    completado = db.Column(db.Boolean, nullable=False)
    fecha_pago = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    metodo_pago = db.Column(db.String(255), nullable=True)  # Ejemplo: largo máximo de 25

class Solicitud(db.Model):
    __tablename__ = 'solicitud'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Relaciones ManyToOne
    apoderado_id = db.Column(db.Integer, db.ForeignKey('apoderado.id'), nullable=False)
    
    
    conductor_id = db.Column(db.Integer, db.ForeignKey('conductor.id'), nullable=False)
    #conductor = db.relationship('Conductor', backref='solicitudes')
    
    furgon_id = db.Column(db.Integer, db.ForeignKey('furgon.id'), nullable=False)
    #furgon = db.relationship('Furgon', backref='solicitudes')
    
    # Campos adicionales
    fecha_solicitud = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    fecha_respuesta = db.Column(db.DateTime, nullable=True)
    aceptada = db.Column(db.Boolean, nullable=False, default=False)
    rechazada = db.Column(db.Boolean, nullable=False, default=False)
    vencida = db.Column(db.Boolean, nullable=False, default=False)
    estado = db.Column(db.String(50), nullable=True)  # Ejemplo: largo máxi
    
class Sector(db.Model):
    __tablename__ = 'sector'
    
    id = db.Column(db.Integer, primary_key=True)
    poblacion = db.Column(db.String(255), nullable=True)
    comuna = db.Column(db.String(255), nullable=True)

#TERMINO DEL MODELO AHORA VAMOS CON LAS RUTAS 
##---------------------------------------------------------------------------------------
##
# Registrar alumno 
#registrar alumno
#Crear un nuevo alumno
@app.route('/alumnos', methods=['POST'])
def create_alumno():
    data = request.get_json()
    try:
        nuevo_alumno = Alumno(
            nombre_completo=data['nombre_completo'],
            rut=data['rut'],
            fecha_nacimiento=datetime.strptime(data['fecha_nacimiento'], '%Y-%m-%d').date(),
            horario_entrada=datetime.strptime(data['horario_entrada'], '%H:%M').time(),
            horario_salida=datetime.strptime(data['horario_salida'], '%H:%M').time(),
            curso=data['curso'],
            direccion_hogar=data.get('direccion_hogar'),
            nombre_contacto_emergencia=data.get('nombre_contacto_emergencia'),
            contacto_emergencia=data['contacto_emergencia'],
            colegio_id=data['colegio_id'],
            apoderado_id=data['apoderado_id'],
            sector_id=data['sector_id']
        )
        db.session.add(nuevo_alumno)
        db.session.commit()
        return jsonify({'mensaje': 'Alumno creado exitosamente'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    

#consultar por alumno filtrando por ID
@app.route('/alumnos/<int:id>', methods=['GET'])
def get_alumno(id):
    alumno = Alumno.query.get(id)
    if not alumno:
        abort(404)
    return jsonify({
        'id': alumno.id,
        'nombre_completo': alumno.nombre_completo,
        'rut': alumno.rut,
        'fecha_nacimiento': alumno.fecha_nacimiento.isoformat(),
        'horario_entrada': alumno.horario_entrada.isoformat(),
        'horario_salida': alumno.horario_salida.isoformat(),
        'curso': alumno.curso,
        'direccion_hogar': alumno.direccion_hogar,
        'nombre_contacto_emergencia': alumno.nombre_contacto_emergencia,
        'contacto_emergencia': alumno.contacto_emergencia,
        'colegio_id': alumno.colegio_id,
        'apoderado_id': alumno.apoderado_id,
        'sector_id': alumno.sector_id
    })

# Obtener todos los alumnos
@app.route('/alumnos', methods=['GET'])
def get_all_alumnos():
    alumnos = Alumno.query.all()
    result = []
    for alumno in alumnos:
        result.append({
            'id': alumno.id,
            'nombre_completo': alumno.nombre_completo,
            'rut': alumno.rut,
            'fecha_nacimiento': alumno.fecha_nacimiento.isoformat(),
            'horario_entrada': alumno.horario_entrada.isoformat(),
            'horario_salida': alumno.horario_salida.isoformat(),
            'curso': alumno.curso,
            'direccion_hogar': alumno.direccion_hogar,
            'nombre_contacto_emergencia': alumno.nombre_contacto_emergencia,
            'contacto_emergencia': alumno.contacto_emergencia,
            'colegio_id': alumno.colegio_id,
            'apoderado_id': alumno.apoderado_id,
            'sector_id': alumno.sector_id
        })
    return jsonify(result)




# Actualizar un alumno
@app.route('/alumnos/<int:id>', methods=['PUT'])
def update_alumno(id):
    alumno = Alumno.query.get(id)
    if not alumno:
        abort(404)
    data = request.get_json()
    try:
        alumno.nombre_completo = data['nombre_completo']
        alumno.rut = data['rut']
        alumno.fecha_nacimiento = datetime.strptime(data['fecha_nacimiento'], '%Y-%m-%d').date()
        alumno.horario_entrada = datetime.strptime(data['horario_entrada'], '%H:%M').time()
        alumno.horario_salida = datetime.strptime(data['horario_salida'], '%H:%M').time()
        alumno.curso = data['curso']
        alumno.direccion_hogar = data.get('direccion_hogar')
        alumno.nombre_contacto_emergencia = data.get('nombre_contacto_emergencia')
        alumno.contacto_emergencia = data['contacto_emergencia']
        alumno.colegio_id = data['colegio_id']
        alumno.apoderado_id = data['apoderado_id']
        alumno.sector_id = data['sector_id']
        db.session.commit()
        return jsonify({'mensaje': 'Alumno actualizado exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# Eliminar un alumno
@app.route('/alumnos/<int:id>', methods=['DELETE'])
def delete_alumno(id):
    alumno = Alumno.query.get(id)
    if not alumno:
        abort(404)
    try:
        db.session.delete(alumno)
        db.session.commit()
        return jsonify({'mensaje': 'Alumno eliminado exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400





# Ruta para registrar un apoderado
@app.route('/registro-apoderado', methods=['POST'])
def registrar_apoderado():
    data = request.get_json()
    try:
        nuevo_apoderado = Apoderado(
            nombre_completo=data['nombre_completo'],
            rut=data['rut'],
            correo=data['correo'],
            direccion=data['direccion'],
            sexo=data.get('sexo'),
            numero_telefono=data['numero_telefono'],
            password=generate_password_hash(data['password'])  # Encripta la contraseña
        )
        db.session.add(nuevo_apoderado)
        db.session.commit()
        return jsonify({'mensaje': 'Apoderado registrado exitosamente'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400



      

# Crear un nuevo apoderado
@app.route('/apoderados', methods=['POST'])
def create_apoderado():
    data = request.get_json()
    try:
        nuevo_apoderado = Apoderado(
            nombre_completo=data['nombre_completo'],
            rut=data['rut'],
            correo=data['correo'],
            password=data['password'],  # Asegúrate de cifrar la contraseña en un entorno de producción
            direccion=data['direccion'],
            numero_telefono=data['numero_telefono'],
            sexo=data.get('sexo'),
            rol=data.get('rol')
        )
        db.session.add(nuevo_apoderado)
        db.session.commit()
        return jsonify({'mensaje': 'Apoderado creado exitosamente'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# Obtener un apoderado por ID
@app.route('/apoderados/<int:id>', methods=['GET'])
def get_apoderado(id):
    apoderado = Apoderado.query.get(id)
    if not apoderado:
        abort(404)
    return jsonify({
        'id': apoderado.id,
        'nombre_completo': apoderado.nombre_completo,
        'rut': apoderado.rut,
        'correo': apoderado.correo,
        'direccion': apoderado.direccion,
        'numero_telefono': apoderado.numero_telefono,
        'sexo': apoderado.sexo,
        'rol': apoderado.rol
    })

#ve todos los apoderados de la base de datos 
@app.route('/apoderados', methods=['GET'])
def get_all_apoderados():
    apoderados = Apoderado.query.all()
    result = []
    for apoderado in apoderados:
        result.append({
            'id': apoderado.id,
            'nombre_completo': apoderado.nombre_completo,
            'rut': apoderado.rut,
            'correo': apoderado.correo,
            'direccion': apoderado.direccion,
            'numero_telefono': apoderado.numero_telefono,
            'sexo': apoderado.sexo,
            'rol': apoderado.rol
        })
    return jsonify({"apoderados":result})


# Actualizar un apoderado
@app.route('/apoderados/<int:id>', methods=['PUT'])
def update_apoderado(id):
    apoderado = Apoderado.query.get(id)
    if not apoderado:
        abort(404)
    data = request.get_json()
    try:
        apoderado.nombre_completo = data['nombre_completo']
        apoderado.rut = data['rut']
        apoderado.correo = data['correo']
        apoderado.password = data['password']  # Recuerda cifrar la contraseña en producción
        apoderado.direccion = data['direccion']
        apoderado.numero_telefono = data['numero_telefono']
        apoderado.sexo = data.get('sexo')
        apoderado.rol = data.get('rol')
        db.session.commit()
        return jsonify({'mensaje': 'Apoderado actualizado exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    

# Eliminar un apoderado
@app.route('/apoderados/<int:id>', methods=['DELETE'])
def delete_apoderado(id):
    apoderado = Apoderado.query.get(id)
    if not apoderado:
        abort(404)
    try:
        db.session.delete(apoderado)
        db.session.commit()
        return jsonify({'mensaje': 'Apoderado eliminado exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    
#Parámetros de consulta : comuna, colegioy poblacionse obtienen de la URL como parámetros opcionales. 
#http://127.0.0.1:5000/furgones?comuna=Santiago&colegio=1&poblacion=Centro
#FURGONNNNN
@app.route('/furgones', methods=['GET'])
def obtener_furgones_filtrados():
    comuna = request.args.get('comuna')
    colegio_id = request.args.get('colegio')
    poblacion = request.args.get('poblacion')

    # Consulta base para Furgones
    query = db.session.query(Furgon).join(Sector).join(Colegio)

    # Filtrar por comuna si está presente
    if comuna:
        query = query.filter(Sector.comuna == comuna)
    
    # Filtrar por colegio si está presente
    if colegio_id:
        query = query.filter(Furgon.colegio_id == colegio_id)

    # Filtrar por población si está presente
    if poblacion:
        query = query.filter(Sector.poblacion == poblacion)

    # Obtener resultados
    furgones = query.all()
    
    # Convertir resultados a JSON
    furgones_json = [
        {
            "id": furgon.id,
            "patente": furgon.patente,
            "marca": furgon.marca,
            "modelo": furgon.modelo,
            "ano": furgon.ano,
            "capacidad": furgon.capacidad,
            "cupos_disponibles": furgon.cupos_disponibles,
            "precio_base": furgon.precio_base,
            "validado": furgon.validado,
            "sector_id": furgon.sector_id,
            "colegio_id": furgon.colegio_id,
            "conductor_id": furgon.conductor_id
        }
        for furgon in furgones
    ]

    return jsonify({"furgones": furgones_json}), 200


# Crear un nuevo furgón
@app.route('/furgones', methods=['POST'])
def create_furgon():
    data = request.get_json()
    try:
        nuevo_furgon = Furgon(
            patente=data['patente'],
            marca=data['marca'],
            modelo=data['modelo'],
            ano=data['ano'],
            capacidad=data['capacidad'],
            cupos_disponibles=data['cupos_disponibles'],
            precio_base=data['precio_base'],
            validado=data['validado'],
            conductor_id=data['conductor_id'],
            sector_id=data['sector_id'],
            colegio_id=data['colegio_id']
        )
        db.session.add(nuevo_furgon)
        db.session.commit()
        return jsonify({'mensaje': 'Furgón creado exitosamente'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# Obtener un furgón por ID
@app.route('/furgones/<int:id>', methods=['GET'])
def get_furgon(id):
    furgon = Furgon.query.get(id)
    if not furgon:
        abort(404)
    return jsonify({
        'id': furgon.id,
        'patente': furgon.patente,
        'marca': furgon.marca,
        'modelo': furgon.modelo,
        'ano': furgon.ano,
        'capacidad': furgon.capacidad,
        'cupos_disponibles': furgon.cupos_disponibles,
        'precio_base': furgon.precio_base,
        'validado': furgon.validado,
        'conductor_id': furgon.conductor_id,
        'sector_id': furgon.sector_id,
        'colegio_id': furgon.colegio_id
    })

# Obtener todos los furgones
@app.route('/furgones', methods=['GET'])
def get_all_furgones():
    furgones = Furgon.query.all()
    result = []
    for furgon in furgones:
        result.append({
            'id': furgon.id,
            'patente': furgon.patente,
            'marca': furgon.marca,
            'modelo': furgon.modelo,
            'ano': furgon.ano,
            'capacidad': furgon.capacidad,
            'cupos_disponibles': furgon.cupos_disponibles,
            'precio_base': furgon.precio_base,
            'validado': furgon.validado,
            'conductor_id': furgon.conductor_id,
            'sector_id': furgon.sector_id,
            'colegio_id': furgon.colegio_id
        })
    return jsonify(result)

# Actualizar un furgón
@app.route('/furgones/<int:id>', methods=['PUT'])
def update_furgon(id):
    furgon = Furgon.query.get(id)
    if not furgon:
        abort(404)
    data = request.get_json()
    try:
        furgon.patente = data['patente']
        furgon.marca = data['marca']
        furgon.modelo = data['modelo']
        furgon.ano = data['ano']
        furgon.capacidad = data['capacidad']
        furgon.cupos_disponibles = data['cupos_disponibles']
        furgon.precio_base = data['precio_base']
        furgon.validado = data['validado']
        furgon.conductor_id = data['conductor_id']
        furgon.sector_id = data['sector_id']
        furgon.colegio_id = data['colegio_id']
        db.session.commit()
        return jsonify({'mensaje': 'Furgón actualizado exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# Eliminar un furgón
@app.route('/furgones/<int:id>', methods=['DELETE'])
def delete_furgon(id):
    furgon = Furgon.query.get(id)
    if not furgon:
        abort(404)
    try:
        db.session.delete(furgon)
        db.session.commit()
        return jsonify({'mensaje': 'Furgón eliminado exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400




#contrato uwu


# Crear un nuevo contrato
@app.route('/contrato', methods=['POST'])
def create_contrato():
    data = request.get_json()
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'El cuerpo de la solicitud está vacío o no es JSON válido'}), 400

        #print("Datos recibidos:", data)  # Esto debería imprimir el JSON recibido
        #print(data['id_colegio'])


        colegio = Colegio.query.get(data['id_colegio'])
        alumno = Alumno.query.get(data['id_alumno'])
        apoderado=Apoderado.query.get(data['id_apoderado'])
        furgon=Furgon.query.get(data['id_furgon'])
        conductor=Conductor.query.get(data['id_conductor'])
        # print(colegio.direccion)
        # print(alumno)

        nuevo_contrato = Contrato(
            direccion_establecimiento=colegio.direccion,
            direccion_hogar=alumno.direccion_hogar,
            fecha_contratacion=date.today(),
            nombre_alumno=alumno.nombre_completo,
            nombre_apoderado=apoderado.nombre_completo,
            rut_apoderado=apoderado.rut,
            nombre_establecimiento=colegio.direccion,
            periodo=data['periodo'],
            precio=furgon.precio_base,
            estado=data['estado'],
            tipo_servicio=data['tipo_servicio'],
            nombre_contacto_emergencia=data['nombre_contacto_emergencia'],
            numero_contacto_emergencia=data['numero_contacto_emergencia'],
            furgon_id=furgon.id,
            conductor_id=conductor.id,
            apoderado_id=apoderado.id,
            alumno_id=alumno.id,
            colegio_id=colegio.id 
        )
        db.session.add(nuevo_contrato)
        db.session.commit()
        return jsonify({'mensaje': 'Contrato creado exitosamente'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


# Obtener un contrato por ID
@app.route('/contrato/<int:id>', methods=['GET'])
def get_contrato(id):
    contrato = Contrato.query.get(id)
    if not contrato:
        abort(404)
    return jsonify({
        'id': contrato.id,
        'direccion_establecimiento': contrato.direccion_establecimiento,
        'direccion_hogar': contrato.direccion_hogar,
        'fecha_contratacion': contrato.fecha_contratacion.isoformat(),
        'nombre_alumno': contrato.nombre_alumno,
        'nombre_apoderado': contrato.nombre_apoderado,
        'rut_apoderado': contrato.rut_apoderado,
        'nombre_establecimiento': contrato.nombre_establecimiento,
        'periodo': contrato.periodo,
        'precio': contrato.precio,
        'estado': contrato.estado,
        'tipo_servicio': contrato.tipo_servicio,
        'nombre_contacto_emergencia': contrato.nombre_contacto_emergencia,
        'numero_contacto_emergencia': contrato.numero_contacto_emergencia,
        'furgon_id': contrato.furgon_id,
        'conductor_id': contrato.conductor_id,
        'apoderado_id': contrato.apoderado_id,
        'alumno_id': contrato.alumno_id,
        'colegio_id': contrato.colegio_id
    })

# Obtener todos los contratos
@app.route('/contrato', methods=['GET'])
def get_all_contratos():
    contratos = Contrato.query.all()
    result = []
    for contrato in contratos:
        result.append({
            'id': contrato.id,
            'direccion_establecimiento': contrato.direccion_establecimiento,
            'direccion_hogar': contrato.direccion_hogar,
            'fecha_contratacion': contrato.fecha_contratacion.isoformat(),
            'nombre_alumno': contrato.nombre_alumno,
            'nombre_apoderado': contrato.nombre_apoderado,
            'rut_apoderado': contrato.rut_apoderado,
            'nombre_establecimiento': contrato.nombre_establecimiento,
            'periodo': contrato.periodo,
            'precio': contrato.precio,
            'estado': contrato.estado,
            'tipo_servicio': contrato.tipo_servicio,
            'nombre_contacto_emergencia': contrato.nombre_contacto_emergencia,
            'numero_contacto_emergencia': contrato.numero_contacto_emergencia,
            'furgon_id': contrato.furgon_id,
            'conductor_id': contrato.conductor_id,
            'apoderado_id': contrato.apoderado_id,
            'alumno_id': contrato.alumno_id,
            'colegio_id': contrato.colegio_id
        })
    return jsonify(result)

# Actualizar un contrato
@app.route('/contrato/<int:id>', methods=['PUT'])
def update_contrato(id):
    contrato = Contrato.query.get(id)
    if not contrato:
        abort(404)
    data = request.get_json()
    try:
        contrato.direccion_establecimiento = data['direccion_establecimiento']
        contrato.direccion_hogar = data['direccion_hogar']
        contrato.nombre_alumno = data['nombre_alumno']
        contrato.nombre_apoderado = data['nombre_apoderado']
        contrato.rut_apoderado = data['rut_apoderado']
        contrato.nombre_establecimiento = data['nombre_establecimiento']
        contrato.periodo = data['periodo']
        contrato.precio = data['precio']
        contrato.estado = data['estado']
        contrato.tipo_servicio = data['tipo_servicio']
        contrato.nombre_contacto_emergencia = data['nombre_contacto_emergencia']
        contrato.numero_contacto_emergencia = data['numero_contacto_emergencia']
        contrato.furgon_id = data['furgon_id']
        contrato.conductor_id = data['conductor_id']
        contrato.apoderado_id = data['apoderado_id']
        contrato.alumno_id = data['alumno_id']
        contrato.colegio_id = data['colegio_id']
        db.session.commit()
        return jsonify({'mensaje': 'Contrato actualizado exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# Eliminar un contrato
@app.route('/contrato/<int:id>', methods=['DELETE'])
def delete_contrato(id):
    contrato = Contrato.query.get(id)
    if not contrato:
        abort(404)
    try:
        db.session.delete(contrato)
        db.session.commit()
        return jsonify({'mensaje': 'Contrato eliminado exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400



# Crear un nuevo asistente
@app.route('/asistentes', methods=['POST'])
def create_asistente():
    data = request.get_json()
    try:
        nuevo_asistente = Asistente(
            correo=data['correo'],
            nombre_completo=data['nombre_completo'],
            rut=data['rut'],
            sexo=data.get('sexo'),
            telefono=data['telefono'],
            image=data.get('image'),  # Suponiendo que la imagen se envía como base64 y luego se decodifica
            conductor_id=data['conductor_id'],
            furgon_id=data.get('furgon_id')
        )
        db.session.add(nuevo_asistente)
        db.session.commit()
        return jsonify({'mensaje': 'Asistente creado exitosamente'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400



# Obtener un asistente por ID
@app.route('/asistentes/<int:id>', methods=['GET'])
def get_asistente(id):
    asistente = Asistente.query.get(id)
    if not asistente:
        abort(404)
    return jsonify({
        'id': asistente.id,
        'correo': asistente.correo,
        'nombre_completo': asistente.nombre_completo,
        'rut': asistente.rut,
        'sexo': asistente.sexo,
        'telefono': asistente.telefono,
        'image': asistente.image.decode('utf-8') if asistente.image else None,  # Convertir la imagen a base64 si existe
        'conductor_id': asistente.conductor_id,
        'furgon_id': asistente.furgon_id
    })


# Obtener todos los asistentes
@app.route('/asistentes', methods=['GET'])
def get_all_asistentes():
    asistentes = Asistente.query.all()
    result = []
    for asistente in asistentes:
        result.append({
            'id': asistente.id,
            'correo': asistente.correo,
            'nombre_completo': asistente.nombre_completo,
            'rut': asistente.rut,
            'sexo': asistente.sexo,
            'telefono': asistente.telefono,
            'image': asistente.image.decode('utf-8') if asistente.image else None,
            'conductor_id': asistente.conductor_id,
            'furgon_id': asistente.furgon_id
        })
    return jsonify(result)

# Actualizar un asistente
@app.route('/asistentes/<int:id>', methods=['PUT'])
def update_asistente(id):
    asistente = Asistente.query.get(id)
    if not asistente:
        abort(404)
    data = request.get_json()
    try:
        asistente.correo = data['correo']
        asistente.nombre_completo = data['nombre_completo']
        asistente.rut = data['rut']
        asistente.sexo = data.get('sexo')
        asistente.telefono = data['telefono']
        asistente.image = data.get('image')  # Si se recibe en base64, asegúrate de decodificar antes de asignar
        asistente.conductor_id = data['conductor_id']
        asistente.furgon_id = data.get('furgon_id')
        db.session.commit()
        return jsonify({'mensaje': 'Asistente actualizado exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# Eliminar un asistente
@app.route('/asistentes/<int:id>', methods=['DELETE'])
def delete_asistente(id):
    asistente = Asistente.query.get(id)
    if not asistente:
        abort(404)
    try:
        db.session.delete(asistente)
        db.session.commit()
        return jsonify({'mensaje': 'Asistente eliminado exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    
# Crear un nuevo colegio
@app.route('/colegios', methods=['POST'])
def create_colegio():
    data = request.get_json()
    try:
        nuevo_colegio = Colegio(
            rbd=data.get('rbd'),
            nombre_colegio=data.get('nombre_colegio'),
            direccion=data.get('direccion'),
            contacto=data.get('contacto'),
            sector_id=data['sector_id']
        )
        db.session.add(nuevo_colegio)
        db.session.commit()
        return jsonify({'mensaje': 'Colegio creado exitosamente'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# Obtener un colegio por ID
@app.route('/colegios/<int:id>', methods=['GET'])
def get_colegio(id):
    colegio = Colegio.query.get(id)
    if not colegio:
        abort(404)
    return jsonify({
        'id': colegio.id,
        'rbd': colegio.rbd,
        'nombre_colegio': colegio.nombre_colegio,
        'direccion': colegio.direccion,
        'contacto': colegio.contacto,
        'sector_id': colegio.sector_id
    })

# Obtener todos los colegios
@app.route('/colegios', methods=['GET'])
def get_all_colegios():
    colegios = Colegio.query.all()
    return jsonify([{
        'id': colegio.id,
        'rbd': colegio.rbd,
        'nombre_colegio': colegio.nombre_colegio,
        'direccion': colegio.direccion,
        'contacto': colegio.contacto,
        'sector_id': colegio.sector_id
    } for colegio in colegios])


# Actualizar un colegio
@app.route('/colegios/<int:id>', methods=['PUT'])
def update_colegio(id):
    colegio = Colegio.query.get(id)
    if not colegio:
        abort(404)
    data = request.get_json()
    try:
        colegio.rbd = data.get('rbd')
        colegio.nombre_colegio = data.get('nombre_colegio')
        colegio.direccion = data.get('direccion')
        colegio.contacto = data.get('contacto')
        colegio.sector_id = data['sector_id']
        db.session.commit()
        return jsonify({'mensaje': 'Colegio actualizado exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# Eliminar un colegio
@app.route('/colegios/<int:id>', methods=['DELETE'])
def delete_colegio(id):
    colegio = Colegio.query.get(id)
    if not colegio:
        abort(404)
    try:
        db.session.delete(colegio)
        db.session.commit()
        return jsonify({'mensaje': 'Colegio eliminado exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400



# Crear una nueva calificación
@app.route('/calificaciones', methods=['POST'])
def create_calificacion():
    data = request.get_json()
    try:
        nueva_calificacion = Calificacion(
            apoderado_id=data['apoderado_id'],
            conductor_id=data['conductor_id'],
            contrato_id=data['contrato_id'],
            puntuacion=data['puntuacion'],
            comentario=data.get('comentario')
        )
        db.session.add(nueva_calificacion)
        db.session.commit()
        return jsonify({'mensaje': 'Calificación creada exitosamente'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# Obtener una calificación por ID
@app.route('/calificaciones/<int:id>', methods=['GET'])
def get_calificacion(id):
    calificacion = Calificacion.query.get(id)
    if not calificacion:
        abort(404)
    return jsonify({
        'id': calificacion.id,
        'apoderado_id': calificacion.apoderado_id,
        'conductor_id': calificacion.conductor_id,
        'contrato_id': calificacion.contrato_id,
        'puntuacion': calificacion.puntuacion,
        'comentario': calificacion.comentario,
        'fecha_calificacion': calificacion.fecha_calificacion.isoformat()
    })

# Obtener todas las calificaciones
@app.route('/calificaciones', methods=['GET'])
def get_all_calificaciones():
    calificaciones = Calificacion.query.all()
    return jsonify([{
        'id': calificacion.id,
        'apoderado_id': calificacion.apoderado_id,
        'conductor_id': calificacion.conductor_id,
        'contrato_id': calificacion.contrato_id,
        'puntuacion': calificacion.puntuacion,
        'comentario': calificacion.comentario,
        'fecha_calificacion': calificacion.fecha_calificacion.isoformat()
    } for calificacion in calificaciones])

# Actualizar una calificación
@app.route('/calificaciones/<int:id>', methods=['PUT'])
def update_calificacion(id):
    calificacion = Calificacion.query.get(id)
    if not calificacion:
        abort(404)
    data = request.get_json()
    try:
        calificacion.puntuacion = data['puntuacion']
        calificacion.comentario = data.get('comentario')
        db.session.commit()
        return jsonify({'mensaje': 'Calificación actualizada exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    
# Eliminar una calificación
@app.route('/calificaciones/<int:id>', methods=['DELETE'])
def delete_calificacion(id):
    calificacion = Calificacion.query.get(id)
    if not calificacion:
        abort(404)
    try:
        db.session.delete(calificacion)
        db.session.commit()
        return jsonify({'mensaje': 'Calificación eliminada exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    
# Crear un nuevo documento
@app.route('/documentos', methods=['POST'])
def create_documento():
    data = request.get_json()
    try:
        nuevo_documento = Documentos(
            contenido_documento=data['contenido_documento'],
            tipo_documento=data['tipo_documento'],
            conductor_id=data.get('conductor_id'),
            asistente_id=data.get('asistente_id')
        )
        db.session.add(nuevo_documento)
        db.session.commit()
        return jsonify({'mensaje': 'Documento creado exitosamente'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
# Obtener un documento por ID
@app.route('/documentos/<int:id>', methods=['GET'])
def get_documento(id):
    documento = Documentos.query.get(id)
    if not documento:
        abort(404)
    return jsonify({
        'id': documento.id,
        'contenido_documento': documento.contenido_documento.decode('utf-8') if documento.contenido_documento else None,
        'tipo_documento': documento.tipo_documento,
        'conductor_id': documento.conductor_id,
        'asistente_id': documento.asistente_id
    })
# Obtener todos los documentos
@app.route('/documentos', methods=['GET'])
def get_all_documentos():
    documentos = Documentos.query.all()
    return jsonify([{
        'id': documento.id,
        'contenido_documento': documento.contenido_documento.decode('utf-8') if documento.contenido_documento else None,
        'tipo_documento': documento.tipo_documento,
        'conductor_id': documento.conductor_id,
        'asistente_id': documento.asistente_id
    } for documento in documentos])


# Actualizar un documento
@app.route('/documentos/<int:id>', methods=['PUT'])
def update_documento(id):
    documento = Documentos.query.get(id)
    if not documento:
        abort(404)
    data = request.get_json()
    try:
        documento.tipo_documento = data['tipo_documento']
        documento.contenido_documento = data['contenido_documento']
        db.session.commit()
        return jsonify({'mensaje': 'Documento actualizado exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
# Eliminar un documento
@app.route('/documentos/<int:id>', methods=['DELETE'])
def delete_documento(id):
    documento = Documentos.query.get(id)
    if not documento:
        abort(404)
    try:
        db.session.delete(documento)
        db.session.commit()
        return jsonify({'mensaje': 'Documento eliminado exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# Crear una nueva notificación
@app.route('/notificaciones', methods=['POST'])
def create_notificacion():
    data = request.get_json()
    try:
        nueva_notificacion = Notificacion(
            mensaje=data['mensaje'],
            conductor_destino_id=data.get('conductor_destino_id'),
            apoderado_destino_id=data.get('apoderado_destino_id')
        )
        db.session.add(nueva_notificacion)
        db.session.commit()
        return jsonify({'mensaje': 'Notificación creada exitosamente'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# Obtener una notificación por ID
@app.route('/notificaciones/<int:id>', methods=['GET'])
def get_notificacion(id):
    notificacion = Notificacion.query.get(id)
    if not notificacion:
        abort(404)
    return jsonify({
        'id': notificacion.id,
        'mensaje': notificacion.mensaje,
        'fecha': notificacion.fecha.isoformat(),
        'conductor_destino_id': notificacion.conductor_destino_id,
        'apoderado_destino_id': notificacion.apoderado_destino_id
    })

# Obtener todas las notificaciones
@app.route('/notificaciones', methods=['GET'])
def get_all_notificaciones():
    notificaciones = Notificacion.query.all()
    return jsonify([{
        'id': notificacion.id,
        'mensaje': notificacion.mensaje,
        'fecha': notificacion.fecha.isoformat(),
        'conductor_destino_id': notificacion.conductor_destino_id,
        'apoderado_destino_id': notificacion.apoderado_destino_id
    } for notificacion in notificaciones])


# Eliminar una notificación
@app.route('/notificaciones/<int:id>', methods=['DELETE'])
def delete_notificacion(id):
    notificacion = Notificacion.query.get(id)
    if not notificacion:
        abort(404)
    try:
        db.session.delete(notificacion)
        db.session.commit()
        return jsonify({'mensaje': 'Notificación eliminada exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400



# Crear un nuevo pago
@app.route('/pagos', methods=['POST'])
def create_pago():
    data = request.get_json()
    try:
        nuevo_pago = Pago(
            apoderado_id=data['apoderado_id'],
            contrato_id=data['contrato_id'],
            monto=data['monto'],
            completado=data['completado'],
            metodo_pago=data.get('metodo_pago')
        )
        db.session.add(nuevo_pago)
        db.session.commit()
        return jsonify({'mensaje': 'Pago creado exitosamente'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


# Obtener un pago por ID
@app.route('/pagos/<int:id>', methods=['GET'])
def get_pago(id):
    pago = Pago.query.get(id)
    if not pago:
        abort(404)
    return jsonify({
        'id': pago.id,
        'apoderado_id': pago.apoderado_id,
        'contrato_id': pago.contrato_id,
        'monto': pago.monto,
        'completado': pago.completado,
        'fecha_pago': pago.fecha_pago.isoformat(),
        'metodo_pago': pago.metodo_pago
    })

# Obtener todos los pagos
@app.route('/pagos', methods=['GET'])
def get_all_pagos():
    pagos = Pago.query.all()
    return jsonify([{
        'id': pago.id,
        'apoderado_id': pago.apoderado_id,
        'contrato_id': pago.contrato_id,
        'monto': pago.monto,
        'completado': pago.completado,
        'fecha_pago': pago.fecha_pago,
        'metodo_pago': pago.metodo_pago
    } for pago in pagos])


# Actualizar un pago
@app.route('/pagos/<int:id>', methods=['PUT'])
def update_pago(id):
    pago = Pago.query.get(id)
    if not pago:
        abort(404)
    data = request.get_json()
    try:
        pago.monto = data['monto']
        pago.completado = data['completado']
        pago.metodo_pago = data.get('metodo_pago')
        db.session.commit()
        return jsonify({'mensaje': 'Pago actualizado exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# Eliminar un pago
@app.route('/pagos/<int:id>', methods=['DELETE'])
def delete_pago(id):
    pago = Pago.query.get(id)
    if not pago:
        abort(404)
    try:
        db.session.delete(pago)
        db.session.commit()
        return jsonify({'mensaje': 'Pago eliminado exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    
# Crear una nueva solicitud
@app.route('/solicitudes', methods=['POST'])
def create_solicitud():
    data = request.get_json()
    try:
        nueva_solicitud = Solicitud(
            apoderado_id=data['apoderado_id'],
            conductor_id=data['conductor_id'],
            furgon_id=data['furgon_id'],
            aceptada=data.get('aceptada', False),
            rechazada=data.get('rechazada', False),
            vencida=data.get('vencida', False),
            estado=data.get('estado')
        )
        db.session.add(nueva_solicitud)
        db.session.commit()
        return jsonify({'mensaje': 'Solicitud creada exitosamente'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400



# Obtener una solicitud por ID
@app.route('/solicitudes/<int:id>', methods=['GET'])
def get_solicitud(id):
    solicitud = Solicitud.query.get(id)
    if not solicitud:
        abort(404)
    return jsonify({
        'id': solicitud.id,
        'apoderado_id': solicitud.apoderado_id,
        'conductor_id': solicitud.conductor_id,
        'furgon_id': solicitud.furgon_id,
        'aceptada': solicitud.aceptada,
        'rechazada': solicitud.rechazada,
        'vencida': solicitud.vencida,
        'estado': solicitud.estado
    })

# Obtener todas las solicitudes
@app.route('/solicitudes', methods=['GET'])
def get_all_solicitudes():
    solicitudes = Solicitud.query.all()
    return jsonify([{
        'id': solicitud.id,
        'apoderado_id': solicitud.apoderado_id,
        'conductor_id': solicitud.conductor_id,
        'furgon_id': solicitud.furgon_id,
        'aceptada': solicitud.aceptada,
        'rechazada': solicitud.rechazada,
        'vencida': solicitud.vencida,
        'estado': solicitud.estado
    } for solicitud in solicitudes])

# Actualizar una solicitud
@app.route('/solicitudes/<int:id>', methods=['PUT'])
def update_solicitud(id):
    solicitud = Solicitud.query.get(id)
    if not solicitud:
        abort(404)
    data = request.get_json()
    try:
        solicitud.aceptada = data.get('aceptada', solicitud.aceptada)
        solicitud.rechazada = data.get('rechazada', solicitud.rechazada)
        solicitud.vencida = data.get('vencida', solicitud.vencida)
        solicitud.estado = data.get('estado', solicitud.estado)
        db.session.commit()
        return jsonify({'mensaje': 'Solicitud actualizada exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# Eliminar una solicitud
@app.route('/solicitudes/<int:id>', methods=['DELETE'])
def delete_solicitud(id):
    solicitud = Solicitud.query.get(id)
    if not solicitud:
        abort(404)
    try:
        db.session.delete(solicitud)
        db.session.commit()
        return jsonify({'mensaje': 'Solicitud eliminada exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    

#esto que viene ahora puede ser que se cambie 
# Función para cargar el usuario por correo
def load_user_by_username(correo):
    # Buscar en la tabla Apoderado
    apoderado = Apoderado.query.filter_by(correo=correo).first()
    if apoderado:
        return {'role': 'apoderado', 'id': apoderado.id, 'correo': apoderado.correo}

    # Buscar en la tabla Conductor
    conductor = Conductor.query.filter_by(correo=correo).first()
    if conductor:
        return {'role': 'conductor', 'id': conductor.id, 'correo': conductor.correo}

    # Buscar en la tabla Admin usando un Optional similar
    admin = Admin.query.filter_by(correo=correo).first()
    if admin:
        return {'role': 'admin', 'id': admin.id, 'correo': admin.correo}

    # Si no se encuentra en ninguna tabla
    raise NotFound(f"Usuario no encontrado con correo: {correo}")

# Ruta de ejemplo para autenticar al usuario usando load_user_by_username
@app.route('/authenticate', methods=['POST'])
def authenticate():
    data = request.get_json()
    correo = data.get('correo')
    password = data.get('password')

    try:
        # Cargar usuario por correo
        user_detail = load_user_by_username(correo)

        # Comprobar la contraseña en la base de datos
        if (user_detail['role'] == 'apoderado' and Apoderado.query.get(user_detail['id']).password == password) or \
           (user_detail['role'] == 'conductor' and Conductor.query.get(user_detail['id']).password == password) or \
           (user_detail['role'] == 'admin' and Admin.query.get(user_detail['id']).password == password):
            # Almacenar la información del usuario en la sesión
            session['user_id'] = user_detail['id']
            session['user_role'] = user_detail['role']
            return jsonify({'mensaje': f'Inicio de sesión exitoso para {user_detail["role"].capitalize()}'}), 200
        else:
            return jsonify({'error': 'Correo o contraseña incorrectos'}), 401
    except NotFound as e:
        return jsonify({'error': str(e)}), 404





if __name__ == '__main__':
    app.run(debug=True)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
