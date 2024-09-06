from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from marshmallow import fields, Schema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from enum import Enum
from sqlalchemy import Date

db = SQLAlchemy()


class Apuesta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    valor_apostado = db.Column(db.Numeric)
    ganancia = db.Column(db.Numeric, default=0)
    id_apostador = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    apostador = db.relationship('Usuario', backref='apuestas')
    id_competidor = db.Column(db.Integer, db.ForeignKey('competidor.id'))
    id_carrera = db.Column(db.Integer, db.ForeignKey('carrera.id'))


class Carrera(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre_carrera = db.Column(db.String(128))
    abierta = db.Column(db.Boolean, default=True)
    competidores = db.relationship('Competidor', cascade='all, delete, delete-orphan')
    apuestas = db.relationship('Apuesta', cascade='all, delete, delete-orphan')
    usuario = db.Column(db.Integer, db.ForeignKey("usuario.id"))


class Competidor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre_competidor = db.Column(db.String(128))
    probabilidad = db.Column(db.Numeric)
    cuota = db.Column(db.Numeric);
    es_ganador = db.Column(db.Boolean, default=False)
    id_carrera = db.Column(db.Integer, db.ForeignKey('carrera.id'))


class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(50))
    contrasena = db.Column(db.String(50))
    nombres = db.Column(db.String(50), nullable=True)
    apellidos = db.Column(db.String(50), nullable=True)
    rol = db.Column(db.String(25))
    carreras = db.relationship('Carrera', cascade='all, delete, delete-orphan')
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


class CompetidorSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Competidor
        include_relationships = True
        load_instance = True

    probabilidad = fields.String()
    cuota = fields.String()


class CarreraSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Carrera
        include_relationships = True
        load_instance = True

    competidores = fields.List(fields.Nested(CompetidorSchema()))
    apuestas = fields.List(fields.Nested(ApuestaSchema()))
    ganancia_casa = fields.Float()

class TransaccionSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Transaccion
        include_relationships = True
        load_instance = True


class ReporteSchema(Schema):
    carrera = fields.Nested(CarreraSchema())
    ganancia_casa = fields.Float()


class UserRole(Enum):
    APOSTADOR = "Apostador"
    ADMINISTRADOR = "Administrador"


class TipoTransaccionEnum(Enum):
    RECARGA = "recarga"
    GANANCIA = "ganancia"
    RETIRO = "retiro"
    APUESTA = "apuesta"
