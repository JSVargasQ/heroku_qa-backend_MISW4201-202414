import json
from unittest import TestCase

from datetime import timedelta
from faker import Faker
from faker.generator import random
from app import app
from modelos import db, Usuario, Evento, Apuesta

fake = Faker()


class TestApuesta(TestCase):

    def setUp(self):
        self.data_factory = Faker()
        self.client = app.test_client()

        nuevo_usuario = {
            "rol": "Admin",
            "usuario": self.data_factory.name(),
            "password": self.data_factory.word(),
            "firstname": self.data_factory.name(),
            "lastname": self.data_factory.name(),
        }

        solicitud_nuevo_usuario = self.client.post("/signin",
                                                   data=json.dumps(nuevo_usuario),
                                                   headers={'Content-Type': 'application/json'})

        respuesta_al_crear_usuario = json.loads(solicitud_nuevo_usuario.get_data())

        self.token = respuesta_al_crear_usuario["token"]
        self.usuario_code = respuesta_al_crear_usuario["id"]

        nuevo_apostador = {
            "rol": "Apostador",
            "usuario": self.data_factory.name(),
            "password": self.data_factory.word(),
            "firstname": self.data_factory.name(),
            "lastname": self.data_factory.name(),
            "email": self.data_factory.email(),
            "expirationDate": self.data_factory.date(pattern="%m/%y", end_datetime=None),
            "cvv": self.data_factory.random_int(min=100, max=999),	
            "creditCard": self.data_factory.credit_card_number(),
        }

        solicitud_nuevo_apostador = self.client.post("/signin",
                                                   data=json.dumps(nuevo_apostador),
                                                   headers={'Content-Type': 'application/json'})

        respuesta_al_crear_apostador = json.loads(solicitud_nuevo_apostador.get_data())
        self.id_apostador = respuesta_al_crear_apostador["id"]
        self.apostador_token = respuesta_al_crear_apostador["token"]

        nuevo_apostador2 = {
            "rol": "Apostador",
            "usuario": self.data_factory.name(),
            "password": self.data_factory.word(),
            "firstname": self.data_factory.name(),
            "lastname": self.data_factory.name(),
            "email": self.data_factory.email(),
            "expirationDate": self.data_factory.date(pattern="%m/%y", end_datetime=None),
            "cvv": self.data_factory.random_int(min=100, max=999),	
            "creditCard": self.data_factory.credit_card_number(),
        }

        solicitud_nuevo_apostador2 = self.client.post("/signin",
                                                   data=json.dumps(nuevo_apostador2),
                                                   headers={'Content-Type': 'application/json'})

        respuesta_al_crear_apostador2 = json.loads(solicitud_nuevo_apostador2.get_data())

        self.id_apostador2 = respuesta_al_crear_apostador2["id"]

    def tearDown(self) -> None:
        db.session.query(Usuario).filter(Usuario.id == self.usuario_code).delete()
        db.session.query(Usuario).filter(Usuario.id == self.id_apostador).delete()
        db.session.query(Usuario).filter(Usuario.id == self.id_apostador2).delete()
        db.session.commit()

    def test_crear_apuesta(self):
        fecha_inicio, fecha_fin =  generar_fecha_inicio_fin_random()
        nuevo_evento = {
            "nombre": self.data_factory.sentence(),
            "tipo": "CARRERA",
            "fecha_inicio": fecha_inicio.isoformat(),
            "fecha_fin": fecha_fin.isoformat(),
            "descripcion": self.data_factory.sentence(nb_words=10),
            "posibles_resultados": [
                {
                    "probabilidad": 0.6,
                    "posible_resultado": "Lorem ipsum",
                    "tipo": "COMPETIDOR"
                },
                {
                    "probabilidad": round(random.uniform(0.1, 0.99), 2),
                    "posible_resultado": self.data_factory.name(),
                    "tipo": "COMPETIDOR"
                },
                {
                    "probabilidad": round(random.uniform(0.1, 0.99), 2),
                    "posible_resultado": self.data_factory.name(),
                    "tipo": "COMPETIDOR"
                }
            ]
        }


        endpoint_eventos = "/usuario/{}/eventos".format(str(self.usuario_code))
        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}

        solicitud_nuevo_evento = self.client.post(endpoint_eventos,
                                                   data=json.dumps(nuevo_evento),
                                                   headers=headers)

        respuesta_al_crear_evento = json.loads(solicitud_nuevo_evento.get_data())
        id_evento = respuesta_al_crear_evento["id"]
        id_posible_resultado = respuesta_al_crear_evento["posibles_resultados"][0]["id"]

        nueva_apuesta = {
            "valor_apostado": random.uniform(100, 10000),
            "id_apostador": self.id_apostador,
            "id_posible_resultado": id_posible_resultado,
            "id_evento": id_evento
        }

        endpoint_apuestas = "/apuestas"

        solicitud_nueva_apuesta = self.client.post(endpoint_apuestas,
                                                   data=json.dumps(nueva_apuesta),
                                                   headers=headers)

        respuesta_al_crear_apuesta = json.loads(solicitud_nueva_apuesta.get_data())
        id_apostador = respuesta_al_crear_apuesta["id_apostador"]

        self.assertEqual(solicitud_nueva_apuesta.status_code, 200)
        self.assertEqual(id_apostador, self.id_apostador)

    def test_editar_apuesta(self):
        fecha_inicio, fecha_fin =  generar_fecha_inicio_fin_random()
        nuevo_event = {
            "nombre": self.data_factory.sentence(),
            "tipo": "CARRERA",
            "fecha_inicio": fecha_inicio.isoformat(),
            "fecha_fin": fecha_fin.isoformat(),
            "descripcion": self.data_factory.sentence(nb_words=10),
            "posibles_resultados": [
                {
                    "probabilidad": 0.6,
                    "posible_resultado": "Damian Corral",
                    "tipo": "COMPETIDOR"
                },
                {
                    "probabilidad": round(random.uniform(0.1, 0.99), 2),
                    "posible_resultado": self.data_factory.name(),
                    "tipo": "COMPETIDOR"
                },
                {
                    "probabilidad": round(random.uniform(0.1, 0.99), 2),
                    "posible_resultado": self.data_factory.name(),
                    "tipo": "COMPETIDOR"
                }
            ]
        }

        endpoint_eventos = "/usuario/{}/eventos".format(str(self.usuario_code))
        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}

        solicitud_nuevo_evento = self.client.post(endpoint_eventos,
                                                   data=json.dumps(nuevo_event),
                                                   headers=headers)

        respuesta_al_crear_evento = json.loads(solicitud_nuevo_evento.get_data())
        id_evento = respuesta_al_crear_evento["id"]
        id_posible_resultado = respuesta_al_crear_evento["posibles_resultados"][0]["id"]

        nueva_apuesta = {
            "valor_apostado": random.uniform(100, 10000),
            "id_apostador": self.id_apostador,
            "id_posible_resultado": id_posible_resultado,
            "id_evento": id_evento
        }

        endpoint_apuestas = "/apuestas"

        solicitud_nueva_apuesta = self.client.post(endpoint_apuestas,
                                                   data=json.dumps(nueva_apuesta),
                                                   headers=headers)

        respuesta_al_crear_apuesta = json.loads(solicitud_nueva_apuesta.get_data())
        id_apostador_antes = respuesta_al_crear_apuesta["id_apostador"]
        id_apuesta = respuesta_al_crear_apuesta["id"]

        endpoint_apuesta = "/apuesta/{}".format(str(id_apuesta))

        apuesta_editada = {
            "valor_apostado": random.uniform(100, 5000),
            "id_apostador": self.id_apostador2,
            "id_posible_resultado": id_posible_resultado,
            "id_evento": id_evento
        }

        solicitud_editar_apuesta = self.client.put(endpoint_apuesta,
                                                   data=json.dumps(apuesta_editada),
                                                   headers=headers)

        respuesta_al_editar_apuesta = json.loads(solicitud_editar_apuesta.get_data())
        id_apostador_despues = respuesta_al_editar_apuesta["id_apostador"]

        self.assertEqual(solicitud_nueva_apuesta.status_code, 200)
        self.assertNotEqual(id_apostador_antes, id_apostador_despues)

    def test_obtener_apuesta_por_id(self):
        fecha_inicio, fecha_fin =  generar_fecha_inicio_fin_random()
        nuevo_evento = {
            "nombre": self.data_factory.sentence(),
            "tipo": "CARRERA",
            "fecha_inicio": fecha_inicio.isoformat(),
            "fecha_fin": fecha_fin.isoformat(),
            "descripcion": self.data_factory.sentence(nb_words=10),
            "posibles_resultados": [
                {
                    "probabilidad": 0.6,
                    "posible_resultado": "Paz Manrique",
                    "tipo": "COMPETIDOR"
                },
                {
                    "probabilidad": round(random.uniform(0.1, 0.99), 2),
                    "posible_resultado": self.data_factory.name(),
                    "tipo": "COMPETIDOR"
                },
                {
                    "probabilidad": round(random.uniform(0.1, 0.99), 2),
                    "posible_resultado": self.data_factory.name(),
                    "tipo": "COMPETIDOR"
                }
            ]
        }

        endpoint_eventos = "/usuario/{}/eventos".format(str(self.usuario_code))
        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}

        solicitud_nuevo_evento = self.client.post(endpoint_eventos,
                                                   data=json.dumps(nuevo_evento),
                                                   headers=headers)

        respuesta_al_crear_evento = json.loads(solicitud_nuevo_evento.get_data())
        id_evento = respuesta_al_crear_evento["id"]
        id_posible_resultado = respuesta_al_crear_evento["posibles_resultados"][0]["id"]

        nueva_apuesta = {
            "valor_apostado": random.uniform(100, 2500),
            "id_apostador": self.id_apostador,
            "id_posible_resultado": id_posible_resultado,
            "id_evento": id_evento
        }

        endpoint_apuestas = "/apuestas"

        solicitud_nueva_apuesta = self.client.post(endpoint_apuestas,
                                                   data=json.dumps(nueva_apuesta),
                                                   headers=headers)

        respuesta_al_crear_apuesta = json.loads(solicitud_nueva_apuesta.get_data())
        id_apuesta = respuesta_al_crear_apuesta["id"]

        endpoint_apuesta = "/apuesta/{}".format(str(id_apuesta))

        solicitud_consultar_apuesta_por_id = self.client.get(endpoint_apuesta, headers=headers)
        apuesta_obtenida = json.loads(solicitud_consultar_apuesta_por_id.get_data())
        self.assertEqual(solicitud_consultar_apuesta_por_id.status_code, 200)
        self.assertEqual(apuesta_obtenida["id_apostador"], self.id_apostador)

    def test_obtener_apuestas(self):
        fecha_inicio, fecha_fin =  generar_fecha_inicio_fin_random()
        nuevo_evento = {
            "nombre": self.data_factory.sentence(),
            "tipo": "CARRERA",
            "fecha_inicio": fecha_inicio.isoformat(),
            "fecha_fin": fecha_fin.isoformat(),
            "descripcion": self.data_factory.sentence(nb_words=10),
            "posibles_resultados": [
                {
                    "probabilidad": 0.6,
                    "posible_resultado": "Zakaria Vila",
                    "tipo": "COMPETIDOR"
                },
                {
                    "probabilidad": round(random.uniform(0.1, 0.99), 2),
                    "posible_resultado": self.data_factory.name(),
                    "tipo": "COMPETIDOR"
                },
                {
                    "probabilidad": round(random.uniform(0.1, 0.99), 2),
                    "posible_resultado": self.data_factory.name(),
                    "tipo": "COMPETIDOR"
                }
            ]
        }

        endpoint_eventos = "/usuario/{}/eventos".format(str(self.usuario_code))
        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}

        solicitud_nuevo_evento = self.client.post(endpoint_eventos,
                                                   data=json.dumps(nuevo_evento),
                                                   headers=headers)

        respuesta_al_crear_evento = json.loads(solicitud_nuevo_evento.get_data())
        id_evento = respuesta_al_crear_evento["id"]
        id_posible_resultado = respuesta_al_crear_evento["posibles_resultados"][0]["id"]

        nueva_apuesta1 = {
            "valor_apostado": random.uniform(100, 10000),
            "id_apostador": self.id_apostador,
            "id_posible_resultado": id_posible_resultado,
            "id_evento": id_evento
        }

        endpoint_apuestas = "/apuestas"

        solicitud_nueva_apuesta1 = self.client.post(endpoint_apuestas,
                                                    data=json.dumps(nueva_apuesta1),
                                                    headers=headers)

        solicitud_consulta_apuestas_antes = self.client.get(endpoint_apuestas, headers=headers)
        total_apuestas_antes = len(json.loads(solicitud_consulta_apuestas_antes.get_data()))

        nueva_apuesta2 = {
            "valor_apostado": random.uniform(100, 10000),
            "id_apostador": self.id_apostador,
            "id_posible_resultado": id_posible_resultado,
            "id_evento": id_evento
        }

        solicitud_nueva_apuesta2 = self.client.post(endpoint_apuestas,
                                                    data=json.dumps(nueva_apuesta2),
                                                    headers=headers)

        solicitud_consulta_apuestas_despues = self.client.get(endpoint_apuestas, headers=headers)
        total_apuestas_despues = len(json.loads(solicitud_consulta_apuestas_despues.get_data()))

        self.assertEqual(solicitud_consulta_apuestas_despues.status_code, 200)
        self.assertGreater(total_apuestas_despues, total_apuestas_antes)

    def test_eliminar_apuesta(self):
        fecha_inicio, fecha_fin =  generar_fecha_inicio_fin_random()
        nuevo_evento = {
            "nombre": self.data_factory.sentence(),
            "tipo": "CARRERA",
            "fecha_inicio": fecha_inicio.isoformat(),
            "fecha_fin": fecha_fin.isoformat(),
            "descripcion": self.data_factory.sentence(nb_words=10),
            "posibles_resultados": [
                {
                    "probabilidad": 0.6,
                    "posible_resultado": "Eduardo Tejera",
                    "tipo": "COMPETIDOR"
                },
                {
                    "probabilidad": round(random.uniform(0.1, 0.99), 2),
                    "posible_resultado": self.data_factory.name(),
                    "tipo": "COMPETIDOR"
                },
                {
                    "probabilidad": round(random.uniform(0.1, 0.99), 2),
                    "posible_resultado": self.data_factory.name(),
                    "tipo": "COMPETIDOR"
                }
            ]
        }

        endpoint_eventos = "/usuario/{}/eventos".format(str(self.usuario_code))
        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}

        solicitud_nuevo_evento = self.client.post(endpoint_eventos,
                                                   data=json.dumps(nuevo_evento),
                                                   headers=headers)

        respuesta_al_crear_evento = json.loads(solicitud_nuevo_evento.get_data())

        id_evento = respuesta_al_crear_evento["id"]
        id_posible_resultado = respuesta_al_crear_evento["posibles_resultados"][0]["id"]

        nueva_apuesta1 = {
            "valor_apostado": random.uniform(100, 100000),
            "id_apostador": self.id_apostador,
            "id_posible_resultado": id_posible_resultado,
            "id_evento": id_evento
        }

        endpoint_apuestas = "/apuestas"

        solicitud_nueva_apuesta1 = self.client.post(endpoint_apuestas,
                                                    data=json.dumps(nueva_apuesta1),
                                                    headers=headers)

        respuesta_al_crear_apuesta = json.loads(solicitud_nueva_apuesta1.get_data())

        id_apuesta = respuesta_al_crear_apuesta["id"]
        solicitud_consulta_apuestas_antes = self.client.get(endpoint_apuestas, headers=headers)
        total_apuestas_antes = len(json.loads(solicitud_consulta_apuestas_antes.get_data()))

        endpoint_apuesta = "/apuesta/{}".format(str(id_apuesta))

        solicitud_eliminar_apuesta = self.client.delete(endpoint_apuesta, headers=headers)
        solicitud_consulta_apuestas_despues = self.client.get(endpoint_apuestas, headers=headers)
        total_apuestas_despues = len(json.loads(solicitud_consulta_apuestas_despues.get_data()))

        self.assertLess(total_apuestas_despues, total_apuestas_antes)
        self.assertEqual(solicitud_eliminar_apuesta.status_code, 204)

    def test_obtener_apuestas_por_apostador(self):
        fecha_inicio, fecha_fin =  generar_fecha_inicio_fin_random()
        evento_body = {
            "nombre": self.data_factory.sentence(),
            "tipo": "CARRERA",
            "fecha_inicio": fecha_inicio.isoformat(),
            "fecha_fin": fecha_fin.isoformat(),
            "descripcion": self.data_factory.sentence(nb_words=10),
            "posibles_resultados": [
                {
                    "probabilidad": round(random.uniform(0.1, 0.99), 2),
                    "posible_resultado": self.data_factory.name(),
                    "tipo": "COMPETIDOR"
                },
                {
                    "probabilidad": round(random.uniform(0.1, 0.99), 2),
                    "posible_resultado": self.data_factory.name(),
                    "tipo": "COMPETIDOR"
                },
                {
                    "probabilidad": round(random.uniform(0.1, 0.99), 2),
                    "posible_resultado": self.data_factory.name(),
                    "tipo": "COMPETIDOR"
                }
            ]
        }

        nuevo_evento = self.client.post(f"/usuario/{self.id_apostador}/eventos",
                                         headers={'Content-Type': 'application/json',
                                                  "Authorization": f"Bearer {self.apostador_token}"},
                                         data=json.dumps(evento_body))

        evento_data = json.loads(nuevo_evento.get_data(as_text=True))

        apuesta_body = {
            "valor_apostado": random.uniform(100, 10000),
            "id_apostador": self.id_apostador,
            "id_posible_resultado": evento_data["posibles_resultados"][0]["id"],
            "id_evento": evento_data["id"]
        }

        nueva_apuesta = self.client.post("/apuestas",
                                         headers={'Content-Type': 'application/json',
                                                  "Authorization": f"Bearer {self.apostador_token}"},
                                         data=json.dumps(apuesta_body))

        apuesta_data = json.loads(nueva_apuesta.get_data(as_text=True))

        apuestas = self.client.get(f"/usuario/{self.id_apostador}/apuestas",
                                   headers={"Authorization": f"Bearer {self.apostador_token}"})

        apuestas_data = json.loads(apuestas.get_data(as_text=True))

        self.assertEqual(apuestas.status_code, 200)
        self.assertEqual(len(apuestas_data), len(db.session.execute(
            db.select(Apuesta).filter_by(id_apostador=self.id_apostador)).scalars().all()))
        self.assertEqual(apuestas_data[0]["id"], apuesta_data["id"])

        db.session.query(Evento).filter(Evento.id == evento_data["id"]).delete()
        db.session.query(Apuesta).filter(Apuesta.id == apuesta_data["id"]).delete()
        db.session.commit()

    def test_obtener_apuestas_por_apostador_sin_apuestas(self):
        nuevo_apostador = {
            "rol": "Apostador",
            "usuario": self.data_factory.name(),
            "password": self.data_factory.word(),
            "firstname": self.data_factory.name(),
            "lastname": self.data_factory.name(),
            "email": self.data_factory.email(),
            "expirationDate": self.data_factory.date(pattern="%m/%y", end_datetime=None),
            "cvv": self.data_factory.random_int(min=100, max=999),
            "creditCard": self.data_factory.credit_card_number(),
        }

        solicitud_nuevo_apostador = self.client.post("/signin",
                                                     data=json.dumps(nuevo_apostador),
                                                     headers={'Content-Type': 'application/json'})

        respuesta_al_crear_apostador = json.loads(solicitud_nuevo_apostador.get_data())
        id_nuevo_apostador = respuesta_al_crear_apostador["id"]
        nuevo_apostador_token = respuesta_al_crear_apostador["token"]
        apuestas = self.client.get(f"/usuario/{id_nuevo_apostador}/apuestas",
                                   headers={"Authorization": f"Bearer {nuevo_apostador_token}"})

        apuestas_data = json.loads(apuestas.get_data(as_text=True))

        self.assertEqual(apuestas.status_code, 200)
        self.assertEqual(len(apuestas_data), 0)

        db.session.query(Usuario).filter(Usuario.id == id_nuevo_apostador).delete()
        db.session.commit()

    def test_obtener_apuestas_por_apostador_no_existente(self):
        apuestas = self.client.get(f"/usuario/{self.data_factory.random_int(min=900, max=999)}/apuestas",
                                   headers={"Authorization": f"Bearer {self.apostador_token}"})

        self.assertEqual(apuestas.status_code, 404)

def generar_fecha_inicio_fin_random():
    fecha_inicio = fake.date_this_year()
    dias_adicionales = fake.random_int(min=1, max=30)
    fecha_fin = fecha_inicio + timedelta(days=dias_adicionales)
    return fecha_inicio, fecha_fin