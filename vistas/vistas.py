from flask import jsonify, request
from flask_jwt_extended import jwt_required, create_access_token
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from datetime import datetime, timedelta

from modelos import db, Apuesta, ApuestaSchema, Usuario, TarjetaCredito, UsuarioSchema, Evento, EventoSchema, \
    PosibleResultadoSchema, PosibleResultado, ReporteSchema, UserRole, Transaccion, TransaccionSchema, ApuestaApostador
from modelos.modelos import TipoTransaccionEnum, TipoEvento

apuesta_schema = ApuestaSchema()
eventos_schema = EventoSchema()
posible_resultado_schema = PosibleResultadoSchema()
usuario_schema = UsuarioSchema()
reporte_schema = ReporteSchema()
transaccion_schema = TransaccionSchema()


class VistaSignIn(Resource):

    def post(self):
        user = request.json["usuario"]
        rol = request.json["rol"]
        firstname = request.json["firstname"]
        lastname = request.json["lastname"]
        password = request.json["password"]

        if rol == "Apostador":
            user = request.json["email"]

        usuario = Usuario.query.filter_by(usuario=user).first()
        if not usuario:

            nuevo_usuario = Usuario(usuario=user, contrasena=password, rol=rol, nombres=firstname, apellidos=lastname)

            if rol == "Apostador":
                number_credit_card = request.json["creditCard"]
                expiration_date = request.json["expirationDate"]
                cvv = request.json["cvv"]
                new_credit_card = TarjetaCredito(numero=number_credit_card, fecha_expiracion=expiration_date, cvv=cvv)
                new_credit_card.transacciones.append(Transaccion(valor=100000, tipo=TipoTransaccionEnum.RECARGA.value, fecha_creacion=datetime.now(), id_tarjeta=new_credit_card.id))
                db.session.add(new_credit_card)
                db.session.commit()

                nuevo_usuario.id_tarjeta = new_credit_card.id

            db.session.add(nuevo_usuario)
            db.session.commit()

            token_de_acceso = create_access_token(identity=nuevo_usuario.id,
                                                    expires_delta=timedelta(days=1),
                                                    additional_claims={"rol": nuevo_usuario.rol})
            return {"mensaje": "usuario creado exitosamente", "token": token_de_acceso, "id": nuevo_usuario.id, "rol": nuevo_usuario.rol}
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
            token_de_acceso = create_access_token(identity=usuario.id,
                                                  expires_delta=timedelta(days=1),
                                                  additional_claims={"rol": usuario.rol})
            return {"mensaje": "Inicio de sesión exitoso",
                    "token": token_de_acceso,
                    "rol": usuario.rol}


class VistaCarrerasUsuario(Resource):

    @jwt_required()
    def post(self, id_usuario):
        try:
            fecha_inicio = datetime.strptime(request.json["fecha_inicio"], '%Y-%m-%d').date()
            fecha_fin = datetime.strptime(request.json["fecha_fin"], '%Y-%m-%d').date()

            equipo_1 = request.json["equipo_1"] if request.json["tipo"] == "PARTIDO" else None
            equipo_2 = request.json["equipo_2"] if request.json["tipo"] == "PARTIDO" else None

            nuevo_evento = Evento(
                nombre=request.json["nombre"],
                tipo=request.json["tipo"],
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                descripcion=request.json["descripcion"],
                equipo_1=equipo_1,
                equipo_2=equipo_2
            )
        except:
            return 'Revise los datos enviados de el evento', 400

        for item in request.json["posibles_resultados"]:
            cuota = round((item["probabilidad"] / (1 - item["probabilidad"])), 2)
            posible_resultado = PosibleResultado(posible_resultado=item["posible_resultado"],
                                    probabilidad=item["probabilidad"],
                                    tipo=item["tipo"],
                                    cuota=cuota,
                                    id_evento=nuevo_evento.id)
            nuevo_evento.posibles_resultados.append(posible_resultado)
        usuario = db.get_or_404(Usuario, id_usuario)
        usuario.eventos.append(nuevo_evento)

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return 'El usuario ya tiene un evento con dicho nombre', 409

        return eventos_schema.dump(nuevo_evento)

    @jwt_required()
    def get(self, id_usuario):
        usuario = db.get_or_404(Usuario, id_usuario)
        if usuario.rol == 'Apostador':
            eventos = Evento.query.filter_by(abierta=True).order_by(Evento.nombre).all()
            eventos_con_apuestas_usuario = []
            for evento in eventos:
                apuestas_usuario = [apuesta for apuesta in evento.apuestas if apuesta.id_apostador == id_usuario]
                
                evento_serializado = eventos_schema.dump(evento)
                evento_serializado['apuestas'] = [apuesta_schema.dump(apuesta) for apuesta in apuestas_usuario]
                
                eventos_con_apuestas_usuario.append(evento_serializado)
            return eventos_con_apuestas_usuario
        return [eventos_schema.dump(evento) for evento in Evento.query.order_by(Evento.nombre).all()]


class VistaCarrera(Resource):

    @jwt_required()
    def get(self, id_evento):
        return eventos_schema.dump(db.get_or_404(Evento, id_evento))

    @jwt_required()
    def put(self, id_evento):
        evento = db.get_or_404(Evento, id_evento)
        evento.nombre = request.json.get("nombre", evento.nombre)
        evento.posibles_resultados = []

        for item in request.json["posibles_resultados"]:
            probabilidad = float(item["probabilidad"])
            cuota = round((probabilidad / (1 - probabilidad)), 2)
            posible_resultado = PosibleResultado(posible_resultado=item["posible_resultado"],
                                    probabilidad=probabilidad,
                                    cuota=cuota,
                                    tipo=item["tipo"],
                                    id_evento=evento.id)
            evento.posibles_resultados.append(posible_resultado)

        db.session.commit()
        return eventos_schema.dump(evento)

    @jwt_required()
    def delete(self, id_evento):
        evento = db.get_or_404(Evento, id_evento)
        db.session.delete(evento)
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
                                id_posible_resultado=request.json["id_posible_resultado"], id_evento=request.json["id_evento"])
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
        self.actualizar_info_apuesta(apuesta)

        usuario = db.get_or_404(Usuario, request.json["id_apostador"])
        if usuario.rol != UserRole.APOSTADOR.value:
            return "El usuario no es apostador", 400
        if usuario is None:
            return "El usuario no existe", 404

        saldo_cuenta = db.session.query(func.sum(Transaccion.valor)).filter_by(id_tarjeta=usuario.id_tarjeta).scalar()
        valor_apostado = float(apuesta.valor_apostado)
        if saldo_cuenta is None or (saldo_cuenta + valor_anterior) < valor_apostado:
            return "El saldo es insuficiente para realizar la apuesta.", 400

        self.guardar_transacciones_en_base_de_datos(usuario, valor_anterior, valor_apostado)
        return apuesta_schema.dump(apuesta)

    def actualizar_info_apuesta(self, apuesta):
        apuesta.valor_apostado = request.json.get("valor_apostado", apuesta.valor_apostado)
        apuesta.id_apostador = request.json.get("id_apostador", apuesta.id_apostador)
        apuesta.id_posible_resultado = request.json.get("id_posible_resultado", apuesta.id_posible_resultado)
        apuesta.id_evento = request.json.get("id_evento", apuesta.id_evento)
        db.session.commit()

    def guardar_transacciones_en_base_de_datos(self, usuario, valor_anterior, valor_apostado):
        tarjeta = db.session.get(TarjetaCredito, usuario.id_tarjeta)
        tarjeta.transacciones.append(Transaccion(valor=float(round(valor_anterior,2)), tipo=TipoTransaccionEnum.RECARGA.value, 
                                                 fecha_creacion=datetime.now(), id_tarjeta=usuario.id_tarjeta))
        tarjeta.transacciones.append(Transaccion(valor=float(round(-valor_apostado,2)), tipo=TipoTransaccionEnum.APUESTA.value, 
                                                 fecha_creacion=datetime.now(), id_tarjeta=usuario.id_tarjeta))
        db.session.commit()

    @jwt_required()
    def delete(self, id_apuesta):
        apuesta = db.get_or_404(Apuesta, id_apuesta)
        evento = db.session.get(Evento, apuesta.id_evento)

        if not evento.abierta:
            return "El evento ya fue cerrado", 400
        
        usuario = db.session.get(Usuario, apuesta.id_apostador)
        valor_apostado=float(apuesta.valor_apostado)
        
        tarjeta = db.session.get(TarjetaCredito, usuario.id_tarjeta)
        tarjeta.transacciones.append(Transaccion(valor=round(valor_apostado,2), tipo=TipoTransaccionEnum.RECARGA.value, fecha_creacion=datetime.now(), id_tarjeta=usuario.id_tarjeta))

        db.session.delete(apuesta)
        db.session.commit()
        return '', 204


class VistaTerminacionCarrera(Resource):

    def put(self, id_posible_resultado):
        posible_resultado = db.get_or_404(PosibleResultado, id_posible_resultado)
        posible_resultado.es_ganador = True
        evento = db.get_or_404(Evento, posible_resultado.id_evento)
        evento.abierta = False

        for apuesta in evento.apuestas:
            if apuesta.id_posible_resultado == posible_resultado.id:
                apuesta.ganancia = apuesta.valor_apostado + (apuesta.valor_apostado / posible_resultado.cuota)
                tarjeta = TarjetaCredito.query.get(apuesta.apostador.id_tarjeta)
                tarjeta.transacciones.append(Transaccion(valor=round(float(apuesta.ganancia),2), tipo=TipoTransaccionEnum.GANANCIA.value, fecha_creacion=datetime.now(), id_tarjeta=tarjeta.id))
            else:
                apuesta.ganancia = 0

        db.session.commit()
        return posible_resultado_schema.dump(posible_resultado)


class VistaReporte(Resource):

    @jwt_required()
    def get(self, id_evento):
        evento_reporte = db.get_or_404(Evento, id_evento)
        ganancia_casa_final = 0

        for apuesta in evento_reporte.apuestas:
            ganancia_casa_final = ganancia_casa_final + apuesta.valor_apostado - apuesta.ganancia

        reporte = dict(evento=evento_reporte, ganancia_casa=ganancia_casa_final)
        schema = ReporteSchema()
        return schema.dump(reporte)


class VistaUsuarios(Resource):

    @jwt_required()
    def get(self):
        usuarios = db.session.execute(db.select(Usuario).filter_by(rol=UserRole.APOSTADOR.value))
        return [usuario_schema.dump(usuario) for usuario in usuarios.scalars().all()]

class VistaUsuario(Resource):

    @jwt_required()
    def get(self, id_usuario):
        usuario = db.get_or_404(Usuario, id_usuario)
        return usuario_schema.dump(usuario)


class VistaTransaccionesUsuario(Resource):

    @jwt_required()
    def get(self, id_usuario):
        usuario = db.get_or_404(Usuario, id_usuario)
        return [transaccion_schema.dump(transaccion) for transaccion in
                Transaccion.query.filter_by(id_tarjeta=usuario.id_tarjeta).all()]
    
class VistaUserBalanceAndTransactions(Resource):
    
    @jwt_required()
    def get(self, id_usuario):

        usuario = db.get_or_404(Usuario, id_usuario)
   
        saldo_cuenta = db.session.query(func.sum(Transaccion.valor)).filter_by(id_tarjeta=usuario.id_tarjeta).scalar()
        saldo_cuenta = saldo_cuenta if saldo_cuenta else 0  
        
        transacciones_list = [transaccion_schema.dump(transaccion) for transaccion in 
                              Transaccion.query.filter_by(id_tarjeta=usuario.id_tarjeta).all()]

        return {
            "balance": saldo_cuenta,
            "transactions": transacciones_list
        }, 200

class VistaRecargar(Resource):

    @jwt_required()
    def post(self, id_usuario):
        usuario = db.get_or_404(Usuario, id_usuario)

        if usuario.rol != UserRole.APOSTADOR.value:
            return "El usuario no es apostador", 403
        
        valorarecargar = request.json["valor"]
        tarjeta = db.session.get(TarjetaCredito, usuario.id_tarjeta)
        tarjeta.transacciones.append(Transaccion(valor=round(valorarecargar,2), tipo=TipoTransaccionEnum.RECARGA.value, fecha_creacion=datetime.now(), id_tarjeta=usuario.id_tarjeta))
        db.session.commit()
        return "Recarga exitosa", 200

class VistaRetirar(Resource):
    
    @jwt_required()
    def post(self, id_usuario):
        usuario = db.get_or_404(Usuario, id_usuario)

        if usuario.rol != UserRole.APOSTADOR.value:
            return "El usuario no es apostador", 403
        
        saldo_cuenta = db.session.query(func.sum(Transaccion.valor)).filter_by(id_tarjeta=usuario.id_tarjeta).scalar()
        saldo_cuenta = saldo_cuenta if saldo_cuenta else 0  

        valoraretirar = request.json["valor"]
        if saldo_cuenta < valoraretirar:
            return "El saldo es insuficiente para realizar el retiro.", 400
        
        tarjeta = db.session.get(TarjetaCredito, usuario.id_tarjeta)
        tarjeta.transacciones.append(Transaccion(valor=round(-valoraretirar,2), tipo=TipoTransaccionEnum.RETIRO.value, fecha_creacion=datetime.now(), id_tarjeta=usuario.id_tarjeta))
        db.session.commit()
        return "Retiro exitoso", 200

class VistaApuestasApostador(Resource):

    @jwt_required()
    def get(self, id_usuario):
        usuario = db.get_or_404(Usuario, id_usuario)
        apuestas = db.session.execute(db.select(Apuesta).filter_by(id_apostador=usuario.id).order_by(Apuesta.id.desc()))
        apuestas_apostador: ApuestaApostador = []
        for apuesta in apuestas.scalars().all():
            evento = db.session.get(Evento, apuesta.id_evento)
            posible_resultado = db.session.get(PosibleResultado, apuesta.id_posible_resultado)
            apuestas_apostador.append(ApuestaApostador(apuesta.id, apuesta.valor_apostado, posible_resultado.posible_resultado, evento.nombre))
        return jsonify([ap.to_dict() for ap in apuestas_apostador])