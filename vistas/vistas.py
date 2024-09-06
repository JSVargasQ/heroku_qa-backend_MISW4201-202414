from flask import request
from flask_jwt_extended import jwt_required, create_access_token
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from datetime import datetime

from modelos import db, Apuesta, ApuestaSchema, Usuario, TarjetaCredito, UsuarioSchema, Carrera, CarreraSchema, \
    CompetidorSchema, Competidor, ReporteSchema, UserRole, Transaccion, TransaccionSchema
from modelos.modelos import TipoTransaccionEnum

apuesta_schema = ApuestaSchema()
carrera_schema = CarreraSchema()
competidor_schema = CompetidorSchema()
usuario_schema = UsuarioSchema()
reporte_schema = ReporteSchema()
transaccion_schema = TransaccionSchema()


class VistaSignIn(Resource):

    def post(self):
        rol = request.json["rol"]

        if rol == "Apostador":
            firstname = request.json["firstname"]
            lastname = request.json["lastname"]
            user = request.json["email"]
            numberCreditCard = request.json["creditCard"]
            expirationDate = request.json["expirationDate"]
            cvv = request.json["cvv"]
            password = request.json["password"]

            usuario = Usuario.query.filter_by(usuario=user).first()
            db.session.commit()
            if not usuario:
                new_credit_card = TarjetaCredito(numero=numberCreditCard, fecha_expiracion=expirationDate, cvv=cvv)
                new_credit_card.transacciones.append(Transaccion(valor=100000, tipo=TipoTransaccionEnum.RECARGA.value, fecha_creacion=datetime.now(), id_tarjeta=new_credit_card.id))
                db.session.add(new_credit_card)
                db.session.commit()

                nuevo_usuario = Usuario(usuario=user, contrasena=password, rol=rol,
                                        nombres=firstname, apellidos=lastname, id_tarjeta=new_credit_card.id)

                db.session.add(nuevo_usuario)
                db.session.commit()

                token_de_acceso = create_access_token(identity=nuevo_usuario.id,
                                                      additional_claims={"rol": nuevo_usuario.rol})
                return {"mensaje": "usuario creado exitosamente", "token": token_de_acceso, "id": nuevo_usuario.id}
            else:
                return {"mensaje": "el usuario ya existe", "cod": "user_exist"}, 400

        else:
            firstname = request.json["firstname"]
            lastname = request.json["lastname"]
            password = request.json["password"]
            user = request.json["usuario"]

            usuario = Usuario.query.filter_by(usuario=user).first()
            db.session.commit()
            if not usuario:

                nuevo_usuario = Usuario(usuario=user, contrasena=password, rol=rol,
                                        nombres=firstname, apellidos=lastname)

                db.session.add(nuevo_usuario)
                db.session.commit()

                token_de_acceso = create_access_token(identity=nuevo_usuario.id,
                                                      additional_claims={"rol": nuevo_usuario.rol})
                return {"mensaje": "usuario creado exitosamente", "token": token_de_acceso, "id": nuevo_usuario.id}
            else:
                return {"mensaje": "el usuario ya existe", "cod": "user_exist"}, 400

    def put(self, id_usuario):
        usuario = db.get_or_404(Usuario, id_usuario)
        usuario.contrasena = request.json.get("contrasena", usuario.contrasena)
        db.session.commit()
        return usuario_schema.dump(usuario)

    def delete(self, id_usuario):
        usuario = db.get_or_404(Usuario, id_usuario)
        db.session.delete(usuario)
        db.session.commit()
        return '', 204


class VistaLogIn(Resource):

    def post(self):
        print(db.first_or_404(
            db.select(Usuario).filter_by(usuario=request.json["usuario"], contrasena=request.json["contrasena"])))
        usuario = db.first_or_404(
            db.select(Usuario).filter_by(
                usuario=request.json["usuario"],
                contrasena=request.json["contrasena"]
            )
        )

        db.session.commit()
        if usuario is None:
            return "El usuario no existe", 404
        else:
            token_de_acceso = create_access_token(identity=usuario.id, additional_claims={"rol": usuario.rol})
            return {"mensaje": "Inicio de sesión exitoso",
                    "token": token_de_acceso,
                    "rol": usuario.rol}


class VistaCarrerasUsuario(Resource):

    @jwt_required()
    def post(self, id_usuario):
        nueva_carrera = Carrera(nombre_carrera=request.json["nombre"])
        for item in request.json["competidores"]:
            cuota = round((item["probabilidad"] / (1 - item["probabilidad"])), 2)
            competidor = Competidor(nombre_competidor=item["competidor"],
                                    probabilidad=item["probabilidad"],
                                    cuota=cuota,
                                    id_carrera=nueva_carrera.id)
            nueva_carrera.competidores.append(competidor)
        usuario = db.get_or_404(Usuario, id_usuario)
        usuario.carreras.append(nueva_carrera)

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return 'El usuario ya tiene un carrera con dicho nombre', 409

        return carrera_schema.dump(nueva_carrera)

    @jwt_required()
    def get(self, id_usuario):
        usuario = db.get_or_404(Usuario, id_usuario)
        if usuario.rol == 'Apostador':
            return [carrera_schema.dump(carrera) for carrera in Carrera.query.filter_by(abierta=True).all()]
        return [carrera_schema.dump(carrera) for carrera in usuario.carreras]


class VistaCarrera(Resource):

    @jwt_required()
    def get(self, id_carrera):
        return carrera_schema.dump(db.get_or_404(Carrera, id_carrera))

    @jwt_required()
    def put(self, id_carrera):
        carrera = db.get_or_404(Carrera, id_carrera)
        carrera.nombre_carrera = request.json.get("nombre", carrera.nombre_carrera)
        carrera.competidores = []

        for item in request.json["competidores"]:
            probabilidad = float(item["probabilidad"])
            cuota = round((probabilidad / (1 - probabilidad)), 2)
            competidor = Competidor(nombre_competidor=item["competidor"],
                                    probabilidad=probabilidad,
                                    cuota=cuota,
                                    id_carrera=carrera.id)
            carrera.competidores.append(competidor)

        db.session.commit()
        return carrera_schema.dump(carrera)

    @jwt_required()
    def delete(self, id_carrera):
        carrera = db.get_or_404(Carrera, id_carrera)
        db.session.delete(carrera)
        db.session.commit()
        return '', 204


class VistaApuestas(Resource):

    @jwt_required()
    def post(self):
        usuario = db.get_or_404(Usuario, request.json["id_apostador"])
        if usuario.rol != UserRole.APOSTADOR.value:
            return "El usuario no es apostador", 400
        if usuario is None:
            return "El usuario no existe", 404
        
        saldo_cuenta = db.session.query(func.sum(Transaccion.valor)).filter_by(id_tarjeta=usuario.id_tarjeta).scalar()
        valor_apostado=request.json["valor_apostado"]
        if saldo_cuenta is None or saldo_cuenta < valor_apostado:
            return "El saldo es insuficiente para realizar la apuesta.", 400
        
        nueva_apuesta = Apuesta(valor_apostado=valor_apostado,
                                id_apostador=request.json["id_apostador"],
                                id_competidor=request.json["id_competidor"], id_carrera=request.json["id_carrera"])
        db.session.add(nueva_apuesta)
        tarjeta = db.session.get(TarjetaCredito, usuario.id_tarjeta)
        tarjeta.transacciones.append(Transaccion(valor=round(-valor_apostado,2), tipo=TipoTransaccionEnum.APUESTA.value, fecha_creacion=datetime.now(), id_tarjeta=usuario.id_tarjeta))
        db.session.commit()
        return apuesta_schema.dump(nueva_apuesta)

    @jwt_required()
    def get(self):
        apuestas = db.session.execute(db.select(Apuesta))
        return [apuesta_schema.dump(ca) for ca in apuestas.scalars().all()]


class VistaApuesta(Resource):

    @jwt_required()
    def get(self, id_apuesta):
        return apuesta_schema.dump(db.get_or_404(Apuesta, id_apuesta))

    @jwt_required()
    def put(self, id_apuesta):
        apuesta = db.get_or_404(Apuesta, id_apuesta)
        valor_anterior = apuesta.valor_apostado
        apuesta.valor_apostado = request.json.get("valor_apostado", apuesta.valor_apostado)
        apuesta.id_apostador = request.json.get("id_apostador", apuesta.id_apostador)
        apuesta.id_competidor = request.json.get("id_competidor", apuesta.id_competidor)
        apuesta.id_carrera = request.json.get("id_carrera", apuesta.id_carrera)

        usuario = db.get_or_404(Usuario, request.json["id_apostador"])
        if usuario.rol != UserRole.APOSTADOR.value:
            return "El usuario no es apostador", 400
        if usuario is None:
            return "El usuario no existe", 404
        
        saldo_cuenta = db.session.query(func.sum(Transaccion.valor)).filter_by(id_tarjeta=usuario.id_tarjeta).scalar()
        valor_apostado = float(apuesta.valor_apostado)
        if saldo_cuenta is None or (saldo_cuenta+valor_anterior) < valor_apostado:
            return "El saldo es insuficiente para realizar la apuesta.", 400
        
        tarjeta = db.session.get(TarjetaCredito, usuario.id_tarjeta)
        tarjeta.transacciones.append(Transaccion(valor=float(round(valor_anterior,2)), tipo=TipoTransaccionEnum.RECARGA.value, fecha_creacion=datetime.now(), id_tarjeta=usuario.id_tarjeta))
        tarjeta.transacciones.append(Transaccion(valor=float(round(-valor_apostado,2)), tipo=TipoTransaccionEnum.APUESTA.value, fecha_creacion=datetime.now(), id_tarjeta=usuario.id_tarjeta))
        db.session.commit()
        return apuesta_schema.dump(apuesta)

    @jwt_required()
    def delete(self, id_apuesta):
        apuesta = db.get_or_404(Apuesta, id_apuesta)
        carrera = db.session.get(Carrera, apuesta.id_carrera)

        if carrera.abierta == False:
            return "La carrera ya fue cerrada", 400
        
        usuario = db.session.get(Usuario, apuesta.id_apostador)
        valor_apostado=float(apuesta.valor_apostado)
        
        tarjeta = db.session.get(TarjetaCredito, usuario.id_tarjeta)
        tarjeta.transacciones.append(Transaccion(valor=round(valor_apostado,2), tipo=TipoTransaccionEnum.RECARGA.value, fecha_creacion=datetime.now(), id_tarjeta=usuario.id_tarjeta))

        db.session.delete(apuesta)
        db.session.commit()
        return '', 204


class VistaTerminacionCarrera(Resource):

    def put(self, id_competidor):
        competidor = db.get_or_404(Competidor, id_competidor)
        competidor.es_ganador = True
        carrera = db.get_or_404(Carrera, competidor.id_carrera)
        carrera.abierta = False

        for apuesta in carrera.apuestas:
            if apuesta.id_competidor == competidor.id:
                apuesta.ganancia = apuesta.valor_apostado + (apuesta.valor_apostado / competidor.cuota)
                tarjeta = TarjetaCredito.query.get(apuesta.apostador.id_tarjeta)
                tarjeta.transacciones.append(Transaccion(valor=round(float(apuesta.ganancia),2), tipo=TipoTransaccionEnum.GANANCIA.value, fecha_creacion=datetime.now(), id_tarjeta=tarjeta.id))
            else:
                apuesta.ganancia = 0

        db.session.commit()
        return competidor_schema.dump(competidor)


class VistaReporte(Resource):

    @jwt_required()
    def get(self, id_carrera):
        carreraReporte = db.get_or_404(Carrera, id_carrera)
        ganancia_casa_final = 0

        for apuesta in carreraReporte.apuestas:
            ganancia_casa_final = ganancia_casa_final + apuesta.valor_apostado - apuesta.ganancia

        reporte = dict(carrera=carreraReporte, ganancia_casa=ganancia_casa_final)
        schema = ReporteSchema()
        return schema.dump(reporte)


class VistaUsuario(Resource):

    @jwt_required()
    def get(self):
        usuarios = db.session.execute(db.select(Usuario).filter_by(rol=UserRole.APOSTADOR.value))
        return [usuario_schema.dump(usuario) for usuario in usuarios.scalars().all()]


class VistaTransaccionesUsuario(Resource):

    @jwt_required()
    def get(self, id_usuario):
        usuario = db.get_or_404(Usuario, id_usuario)
        return [transaccion_schema.dump(transaccion) for transaccion in
                Transaccion.query.filter_by(id_tarjeta=usuario.id_tarjeta).all()]
