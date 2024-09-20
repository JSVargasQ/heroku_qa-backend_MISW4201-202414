from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields, Schema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from enum import Enum
from sqlalchemy import Enum as SqlEnum
from marshmallow import fields

db = SQLAlchemy()


class Apuesta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    valor_apostado = db.Column(db.Numeric)
    ganancia = db.Column(db.Numeric, default=0)
    id_apostador = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    apostador = db.relationship('Usuario', backref='apuestas')
    id_posible_resultado = db.Column(db.Integer, db.ForeignKey('posible_resultado.id'))
    id_evento = db.Column(db.Integer, db.ForeignKey('evento.id'))


class TipoEvento(Enum):
    CARRERA = "Carrera"
    PARTIDO = "Partido"


class Evento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(128))
    tipo = db.Column(SqlEnum(TipoEvento))
    fecha_inicio = db.Column(db.Date)
    fecha_fin = db.Column(db.Date)
    descripcion = db.Column(db.String(1000))
    abierta = db.Column(db.Boolean, default=True)
    equipo_1 = db.Column(db.String(128))
    equipo_2 = db.Column(db.String(128))
    posibles_resultados = db.relationship('PosibleResultado', cascade='all, delete, delete-orphan')
    apuestas = db.relationship('Apuesta', cascade='all, delete, delete-orphan')
    usuario = db.Column(db.Integer, db.ForeignKey("usuario.id"))


class TipoPosibleResultado(Enum):
    COMPETIDOR = "Competidor"
    MARCADOR = "Marcador"


class PosibleResultado(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    posible_resultado = db.Column(db.String(128))
    tipo = db.Column(SqlEnum(TipoPosibleResultado))
    probabilidad = db.Column(db.Numeric)
    cuota = db.Column(db.Numeric)
    es_ganador = db.Column(db.Boolean, default=False)
    id_evento = db.Column(db.Integer, db.ForeignKey('evento.id'))


class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(50))
    contrasena = db.Column(db.String(50))
    nombres = db.Column(db.String(50), nullable=True)
    apellidos = db.Column(db.String(50), nullable=True)
    rol = db.Column(db.String(25))
    eventos = db.relationship('Evento', cascade='all, delete, delete-orphan')
    id_tarjeta = db.Column(db.Integer, db.ForeignKey('tarjeta_credito.id'))


class TarjetaCredito(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(16))
    fecha_expiracion = db.Column(db.String(5))
    cvv = db.Column(db.Integer)
    transacciones = db.relationship('Transaccion', cascade='all, delete, delete-orphan')


class Transaccion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(10))
    fecha_creacion = db.Column(db.DateTime, default=datetime.now)
    valor = db.Column(db.Integer)
    id_tarjeta = db.Column(db.Integer, db.ForeignKey('tarjeta_credito.id'))


class UsuarioSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Usuario
        include_relationships = True
        load_instance = True


class ApuestaSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Apuesta
        include_relationships = True
        include_fk = True
        load_instance = True

    valor_apostado = fields.String()
    ganancia = fields.String()
    apostador = fields.Nested(UsuarioSchema, only=["id", "usuario", "nombres", "apellidos", "rol"])


class PosibleResultadoSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = PosibleResultado
        include_relationships = True
        load_instance = True

    tipo = fields.Method("get_tipo_posible_resultado")
    probabilidad = fields.String()
    cuota = fields.String()

    def get_tipo_posible_resultado(self, obj):
        return obj.tipo.value


class EventoSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Evento
        include_relationships = True
        load_instance = True

    tipo = fields.Method("get_tipo_evento")
    posibles_resultados = fields.List(fields.Nested(PosibleResultadoSchema()))
    apuestas = fields.List(fields.Nested(ApuestaSchema()))
    ganancia_casa = fields.Float()

    def get_tipo_evento(self, obj):
        return obj.tipo.value


class TransaccionSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Transaccion
        include_relationships = True
        load_instance = True


class ReporteSchema(Schema):
    evento = fields.Nested(EventoSchema())
    ganancia_casa = fields.Float()


class UserRole(Enum):
    APOSTADOR = "Apostador"
    ADMINISTRADOR = "Administrador"


class TipoTransaccionEnum(Enum):
    RECARGA = "recarga"
    GANANCIA = "ganancia"
    RETIRO = "retiro"
    APUESTA = "apuesta"

class ApuestaApostador:
    id: str
    valor_apostado: str
    nombre_competidor: str
    nombre_carrera: str
    
    def __init__(self, id, valor_apostado, nombre_competidor, nombre_carrera):
        self.id = id
        self.valor_apostado = valor_apostado
        self.nombre_competidor = nombre_competidor
        self.nombre_carrera = nombre_carrera

    def to_dict(self):
        return {
            "id": self.id,
            "valor_apostado": self.valor_apostado,
            "nombre_competidor": self.nombre_competidor,
            "nombre_carrera": self.nombre_carrera
        }