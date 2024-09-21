import json
from unittest import TestCase
from datetime import timedelta
from faker import Faker
from faker.generator import random
from app import app
from modelos import db, Usuario, Evento

fake = Faker()

class TestEvento(TestCase):

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

        

    def tearDown(self) -> None:
        db.session.query(Usuario).filter(Usuario.id == self.usuario_code).delete()
        db.session.query(Usuario).filter(Usuario.id == self.id_apostador).delete()
        db.session.commit()

    def test_crear_evento_carrera(self):
        fecha_inicio, fecha_fin =  generar_fecha_inicio_fin_random()
        nuevo_evento = {
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

        endpoint_eventos = "/usuario/{}/eventos".format(str(self.usuario_code))
        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}

        solicitud_nuevo_evento = self.client.post(endpoint_eventos,
                                                   data=json.dumps(nuevo_evento),
                                                   headers=headers)

        self.assertEqual(solicitud_nuevo_evento.status_code, 200)


    def test_crear_evento_partido(self):
        fecha_inicio, fecha_fin =  generar_fecha_inicio_fin_random()
        nuevo_evento = {
            "nombre": self.data_factory.sentence(),
            "tipo": "PARTIDO",
            "fecha_inicio": fecha_inicio.isoformat(),
            "fecha_fin": fecha_fin.isoformat(),
            "descripcion": self.data_factory.sentence(nb_words=10),
            "equipo_1": self.data_factory.sentence(),
            "equipo_2": self.data_factory.sentence(),
            "posibles_resultados": [
                {
                    "probabilidad": round(random.uniform(0.1, 0.99), 2),
                    "posible_resultado": self.data_factory.name(),
                    "tipo": "MARCADOR"
                },
                {
                    "probabilidad": round(random.uniform(0.1, 0.99), 2),
                    "posible_resultado": self.data_factory.name(),
                    "tipo": "MARCADOR"
                },
                {
                    "probabilidad": round(random.uniform(0.1, 0.99), 2),
                    "posible_resultado": self.data_factory.name(),
                    "tipo": "MARCADOR"
                }
            ]
        }

        endpoint_eventos = "/usuario/{}/eventos".format(str(self.usuario_code))
        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}

        solicitud_nuevo_evento = self.client.post(endpoint_eventos,
                                                   data=json.dumps(nuevo_evento),
                                                   headers=headers)

        self.assertEqual(solicitud_nuevo_evento.status_code, 200)

    def test_crear_evento_partido(self):
        fecha_inicio, fecha_fin =  generar_fecha_inicio_fin_random()
        nuevo_evento = {
            "nombre": self.data_factory.sentence(),
            "tipo": "PARTIDO",
            "fecha_inicio": fecha_inicio.isoformat(),
            "fecha_fin": fecha_fin.isoformat(),
            "descripcion": self.data_factory.sentence(nb_words=10),
            "equipo_1": self.data_factory.sentence(),
            "equipo_2": self.data_factory.sentence(),
            "posibles_resultados": [
                {
                    "probabilidad": round(random.uniform(0.1, 0.99), 2),
                    "posible_resultado": self.data_factory.name(),
                    "tipo": "MARCADOR"
                },
                {
                    "probabilidad": round(random.uniform(0.1, 0.99), 2),
                    "posible_resultado": self.data_factory.name(),
                    "tipo": "MARCADOR"
                },
                {
                    "probabilidad": round(random.uniform(0.1, 0.99), 2),
                    "posible_resultado": self.data_factory.name(),
                    "tipo": "MARCADOR"
                }
            ]
        }

        endpoint_eventos = "/usuario/{}/eventos".format(str(self.usuario_code))
        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}

        solicitud_nuevo_evento = self.client.post(endpoint_eventos,
                                                   data=json.dumps(nuevo_evento),
                                                   headers=headers)

        self.assertEqual(solicitud_nuevo_evento.status_code, 200)

    def test_crear_evento_partido_bad_request(self):
        fecha_inicio, fecha_fin = generar_fecha_inicio_fin_random()
        nuevo_evento = {
            "nombre": self.data_factory.sentence(),
            "fecha_inicio": fecha_inicio.isoformat(),
            "fecha_fin": fecha_fin.isoformat(),
            "descripcion": self.data_factory.sentence(nb_words=10),
            "equipo_1": self.data_factory.sentence(),
            "equipo_2": self.data_factory.sentence()
        }

        endpoint_eventos = "/usuario/{}/eventos".format(str(self.usuario_code))
        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}

        solicitud_nuevo_evento = self.client.post(endpoint_eventos,
                                                   data=json.dumps(nuevo_evento),
                                                   headers=headers)

        self.assertEqual(solicitud_nuevo_evento.status_code, 400)

    def test_crear_evento_partido_bad_token(self):
        fecha_inicio, fecha_fin = generar_fecha_inicio_fin_random()
        nuevo_evento = {
            "nombre": self.data_factory.sentence(),
            "tipo": "PARTIDO",
            "fecha_inicio": fecha_inicio.isoformat(),
            "fecha_fin": fecha_fin.isoformat(),
            "descripcion": self.data_factory.sentence(nb_words=10),
            "equipo_1": self.data_factory.sentence(),
            "equipo_2": self.data_factory.sentence(),
            "posibles_resultados": [
                {
                    "probabilidad": round(random.uniform(0.1, 0.99), 2),
                    "posible_resultado": self.data_factory.name(),
                    "tipo": "MARCADOR"
                },
                {
                    "probabilidad": round(random.uniform(0.1, 0.99), 2),
                    "posible_resultado": self.data_factory.name(),
                    "tipo": "MARCADOR"
                },
                {
                    "probabilidad": round(random.uniform(0.1, 0.99), 2),
                    "posible_resultado": self.data_factory.name(),
                    "tipo": "MARCADOR"
                }
            ]
        }

        endpoint_eventos = "/usuario/{}/eventos".format(str(self.usuario_code))
        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format("1234asdf1234asdfa")}

        solicitud_nuevo_evento = self.client.post(endpoint_eventos,
                                                   data=json.dumps(nuevo_evento),
                                                   headers=headers)

        self.assertEqual(solicitud_nuevo_evento.status_code, 422)

    def test_editar_carrera(self):
        fecha_inicio, fecha_fin =  generar_fecha_inicio_fin_random()
        nuevo_evento_1 = {
            "nombre": "Sakhir. 57 vueltas",
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

        fecha_inicio, fecha_fin =  generar_fecha_inicio_fin_random()
        nuevo_evento_2 = {
            "nombre": "Sakhir 130 vueltas",
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
                }
            ]
        }

        endpoint_crear_evento = "/usuario/{}/eventos".format(str(self.usuario_code))
        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}

        solicitud_nuevo_evento_1 = self.client.post(endpoint_crear_evento,
                                                     data=json.dumps(nuevo_evento_1),
                                                     headers=headers)

        respuesta_al_crear_evento = json.loads(solicitud_nuevo_evento_1.get_data())
        id_evento = respuesta_al_crear_evento["id"]

        endpoint_editar_evento = "/evento/{}".format(str(id_evento))

        solicitud_editar_evento = self.client.put(endpoint_editar_evento,
                                                   data=json.dumps(nuevo_evento_2),
                                                   headers=headers)

        evento_editado = json.loads(solicitud_editar_evento.get_data())

        self.assertEqual(solicitud_editar_evento.status_code, 200)
        self.assertEqual(evento_editado["nombre"], "Sakhir 130 vueltas")

    def test_obtener_carrera_por_id(self):
        nuevo_evento = {
            "nombre": "GP de Miami",
            "tipo": "CARRERA",
            "fecha_inicio": "2024-09-15",
            "fecha_fin": "2024-09-25",
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
                }
            ]
        }

        endpoint_crear_evento = "/usuario/{}/eventos".format(str(self.usuario_code))
        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}

        solicitud_nuevo_evento = self.client.post(endpoint_crear_evento,
                                                   data=json.dumps(nuevo_evento),
                                                   headers=headers)

        respuesta_al_crear_evento = json.loads(solicitud_nuevo_evento.get_data())
        id_evento = respuesta_al_crear_evento["id"]

        endpoint_obtener_evento = "/evento/{}".format(str(id_evento))

        solicitud_consultar_evento_por_id = self.client.get(endpoint_obtener_evento, headers=headers)
        evento_obtenido = json.loads(solicitud_consultar_evento_por_id.get_data())

        self.assertEqual(solicitud_consultar_evento_por_id.status_code, 200)
        self.assertEqual(evento_obtenido["nombre"], "GP de Miami")
        self.assertEqual(evento_obtenido["fecha_inicio"], "2024-09-15")
        self.assertEqual(evento_obtenido["fecha_fin"], "2024-09-25")

    def test_obtener_carreras(self):
        fecha_inicio, fecha_fin = generar_fecha_inicio_fin_random()
        nuevo_evento = {
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
                }
            ]
        }

        endpoint = "/usuario/{}/eventos".format(str(self.usuario_code))
        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}

        solicitud_consultar_eventos_antes = self.client.get(endpoint, headers=headers)
        eventos_antes = json.loads(solicitud_consultar_eventos_antes.get_data())
        total_eventos_antes = len(eventos_antes)

        solicitud_nuevo_evento = self.client.post(endpoint, data=json.dumps(nuevo_evento), headers=headers)
        self.assertEqual(solicitud_nuevo_evento.status_code, 200) 

        solicitud_consultar_eventos_despues = self.client.get(endpoint, headers=headers)
        eventos_despues = json.loads(solicitud_consultar_eventos_despues.get_data())
        total_eventos_despues = len(eventos_despues)

        self.assertGreater(total_eventos_despues, total_eventos_antes)

    def test_obtener_solo_eventos_activos_para_apostador(self):
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

        nuevo_evento_1 = self.client.post(f"/usuario/{self.usuario_code}/eventos",
                                         headers={'Content-Type': 'application/json',
                                                  "Authorization": f"Bearer {self.token}"},
                                         data=json.dumps(evento_body))

        evento_1_data = json.loads(nuevo_evento_1.get_data(as_text=True))

        evento_body["nombre"] = self.data_factory.sentence()

        nuevo_evento_2 = self.client.post(f"/usuario/{self.usuario_code}/eventos",
                                         headers={'Content-Type': 'application/json',
                                                  "Authorization": f"Bearer {self.token}"},
                                         data=json.dumps(evento_body))

        evento_2_data = json.loads(nuevo_evento_2.get_data(as_text=True))
        
        evento_1 = db.get_or_404(Evento, evento_1_data["id"])
        evento_1.abierta = False
        db.session.add(evento_1)       
        db.session.commit()

        eventos = self.client.get(f"/usuario/{self.id_apostador}/eventos",
                                    headers={'Content-Type': 'application/json',
                                             "Authorization": f"Bearer {self.apostador_token}"})
        
        eventos_data = json.loads(eventos.get_data(as_text=True))

        self.assertEqual(eventos.status_code, 200)
        for evento in eventos_data:
            self.assertTrue(evento["abierta"])

        db.session.query(Evento).filter(Evento.id == evento_1_data["id"]).delete()
        db.session.query(Evento).filter(Evento.id == evento_2_data["id"]).delete()
        db.session.commit()

    def test_eliminar_evento(self):
        fecha_inicio, fecha_fin =  generar_fecha_inicio_fin_random()
        nuevo_evento = {
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

        endpoint_eventos = "/usuario/{}/eventos".format(str(self.usuario_code))
        headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}

        solicitud_nuevo_evento = self.client.post(endpoint_eventos,
                                                   data=json.dumps(nuevo_evento),
                                                   headers=headers)

        id_evento = json.loads(solicitud_nuevo_evento.get_data())["id"]
        solicitud_consultar_eventos_antes = self.client.get(endpoint_eventos, headers=headers)
        total_eventos_antes = len(json.loads(solicitud_consultar_eventos_antes.get_data()))

        endpoint_evento = "/evento/{}".format(str(id_evento))

        solicitud_eliminar_evento = self.client.delete(endpoint_evento, headers=headers)
        solicitud_consultar_eventos_despues = self.client.get(endpoint_eventos, headers=headers)
        total_eventos_despues = len(json.loads(solicitud_consultar_eventos_despues.get_data()))
        solicitud_consultar_evento_por_id = self.client.get(endpoint_evento, headers=headers)

        self.assertLess(total_eventos_despues, total_eventos_antes)
        self.assertEqual(solicitud_consultar_evento_por_id.status_code, 404)
        self.assertEqual(solicitud_eliminar_evento.status_code, 204)

def generar_fecha_inicio_fin_random():
    fecha_inicio = fake.date_this_year()
    dias_adicionales = fake.random_int(min=1, max=30)
    fecha_fin = fecha_inicio + timedelta(days=dias_adicionales)
    return fecha_inicio, fecha_fin