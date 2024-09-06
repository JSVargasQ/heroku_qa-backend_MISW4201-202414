import json
from unittest import TestCase

from faker import Faker
from faker.generator import random

from app import app


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

    def test_crear_apuesta(self):
        nueva_carrera = {
            "nombre": self.data_factory.sentence(),
            "competidores": [
                {
                    "probabilidad": 0.6,
                    "competidor": "Lorem ipsum"
                },
                {
                    "probabilidad": round(random.uniform(0.1, 0.99), 2),
                    "competidor": self.data_factory.name()
                },
                {
                    "probabilidad": round(random.uniform(0.1, 0.99), 2),
                    "competidor": self.data_factory.name()
                }
            ]
        }

        endpoint_carreras = "/usuario/{}/carreras".format(str(self.usuario_code))
        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}

        solicitud_nueva_carrera = self.client.post(endpoint_carreras,
                                                   data=json.dumps(nueva_carrera),
                                                   headers=headers)

        respuesta_al_crear_carrera = json.loads(solicitud_nueva_carrera.get_data())
        id_carrera = respuesta_al_crear_carrera["id"]
        id_competidor = \
        [x for x in respuesta_al_crear_carrera["competidores"] if x["nombre_competidor"] == "Lorem ipsum"][0]["id"]

        nueva_apuesta = {
            "valor_apostado": random.uniform(100, 10000),
            "id_apostador": self.id_apostador,
            "id_competidor": id_competidor,
            "id_carrera": id_carrera
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
        nueva_carrera = {
            "nombre": self.data_factory.sentence(),
            "competidores": [
                {
                    "probabilidad": 0.6,
                    "competidor": "Damian Corral"
                },
                {
                    "probabilidad": round(random.uniform(0.1, 0.99), 2),
                    "competidor": self.data_factory.name()
                },
                {
                    "probabilidad": round(random.uniform(0.1, 0.99), 2),
                    "competidor": self.data_factory.name()
                }
            ]
        }

        endpoint_carreras = "/usuario/{}/carreras".format(str(self.usuario_code))
        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}

        solicitud_nueva_carrera = self.client.post(endpoint_carreras,
                                                   data=json.dumps(nueva_carrera),
                                                   headers=headers)

        respuesta_al_crear_carrera = json.loads(solicitud_nueva_carrera.get_data())
        id_carrera = respuesta_al_crear_carrera["id"]
        id_competidor = \
        [x for x in respuesta_al_crear_carrera["competidores"] if x["nombre_competidor"] == "Damian Corral"][0]["id"]

        nueva_apuesta = {
            "valor_apostado": random.uniform(100, 10000),
            "id_apostador": self.id_apostador,
            "id_competidor": id_competidor,
            "id_carrera": id_carrera
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
            "id_competidor": id_competidor,
            "id_carrera": id_carrera
        }

        solicitud_editar_apuesta = self.client.put(endpoint_apuesta,
                                                   data=json.dumps(apuesta_editada),
                                                   headers=headers)

        respuesta_al_editar_apuesta = json.loads(solicitud_editar_apuesta.get_data())
        id_apostador_despues = respuesta_al_editar_apuesta["id_apostador"]

        self.assertEqual(solicitud_nueva_apuesta.status_code, 200)
        self.assertNotEqual(id_apostador_antes, id_apostador_despues)

    def test_obtener_apuesta_por_id(self):
        nueva_carrera = {
            "nombre": self.data_factory.sentence(),
            "competidores": [
                {
                    "probabilidad": 0.6,
                    "competidor": "Paz Manrique"
                },
                {
                    "probabilidad": round(random.uniform(0.1, 0.99), 2),
                    "competidor": self.data_factory.name()
                },
                {
                    "probabilidad": round(random.uniform(0.1, 0.99), 2),
                    "competidor": self.data_factory.name()
                }
            ]
        }

        endpoint_carreras = "/usuario/{}/carreras".format(str(self.usuario_code))
        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}

        solicitud_nueva_carrera = self.client.post(endpoint_carreras,
                                                   data=json.dumps(nueva_carrera),
                                                   headers=headers)

        respuesta_al_crear_carrera = json.loads(solicitud_nueva_carrera.get_data())
        id_carrera = respuesta_al_crear_carrera["id"]
        id_competidor = \
        [x for x in respuesta_al_crear_carrera["competidores"] if x["nombre_competidor"] == "Paz Manrique"][0]["id"]

        nueva_apuesta = {
            "valor_apostado": random.uniform(100, 2500),
            "id_apostador": self.id_apostador,
            "id_competidor": id_competidor,
            "id_carrera": id_carrera
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
        nueva_carrera = {
            "nombre": self.data_factory.sentence(),
            "competidores": [
                {
                    "probabilidad": 0.6,
                    "competidor": "Zakaria Vila"
                },
                {
                    "probabilidad": round(random.uniform(0.1, 0.99), 2),
                    "competidor": self.data_factory.name()
                },
                {
                    "probabilidad": round(random.uniform(0.1, 0.99), 2),
                    "competidor": self.data_factory.name()
                }
            ]
        }

        endpoint_carreras = "/usuario/{}/carreras".format(str(self.usuario_code))
        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}

        solicitud_nueva_carrera = self.client.post(endpoint_carreras,
                                                   data=json.dumps(nueva_carrera),
                                                   headers=headers)

        respuesta_al_crear_carrera = json.loads(solicitud_nueva_carrera.get_data())
        id_carrera = respuesta_al_crear_carrera["id"]
        id_competidor = \
        [x for x in respuesta_al_crear_carrera["competidores"] if x["nombre_competidor"] == "Zakaria Vila"][0]["id"]

        nueva_apuesta1 = {
            "valor_apostado": random.uniform(100, 10000),
            "id_apostador": self.id_apostador,
            "id_competidor": id_competidor,
            "id_carrera": id_carrera
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
            "id_competidor": id_competidor,
            "id_carrera": id_carrera
        }

        solicitud_nueva_apuesta2 = self.client.post(endpoint_apuestas,
                                                    data=json.dumps(nueva_apuesta2),
                                                    headers=headers)

        solicitud_consulta_apuestas_despues = self.client.get(endpoint_apuestas, headers=headers)
        total_apuestas_despues = len(json.loads(solicitud_consulta_apuestas_despues.get_data()))

        self.assertEqual(solicitud_consulta_apuestas_despues.status_code, 200)
        self.assertGreater(total_apuestas_despues, total_apuestas_antes)

    def test_eliminar_apuesta(self):
        nueva_carrera = {
            "nombre": self.data_factory.sentence(),
            "competidores": [
                {
                    "probabilidad": 0.6,
                    "competidor": "Eduardo Tejera"
                },
                {
                    "probabilidad": round(random.uniform(0.1, 0.99), 2),
                    "competidor": self.data_factory.name()
                },
                {
                    "probabilidad": round(random.uniform(0.1, 0.99), 2),
                    "competidor": self.data_factory.name()
                }
            ]
        }

        endpoint_carreras = "/usuario/{}/carreras".format(str(self.usuario_code))
        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}

        solicitud_nueva_carrera = self.client.post(endpoint_carreras,
                                                   data=json.dumps(nueva_carrera),
                                                   headers=headers)

        respuesta_al_crear_carrera = json.loads(solicitud_nueva_carrera.get_data())

        id_carrera = respuesta_al_crear_carrera["id"]
        id_competidor = \
        [x for x in respuesta_al_crear_carrera["competidores"] if x["nombre_competidor"] == "Eduardo Tejera"][0]["id"]

        nueva_apuesta1 = {
            "valor_apostado": random.uniform(100, 100000),
            "id_apostador": self.id_apostador,
            "id_competidor": id_competidor,
            "id_carrera": id_carrera
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
