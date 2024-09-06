from datetime import datetime
import json
import random
import string
from unittest import TestCase
from faker import Faker
from app import app
from modelos import db, Transaccion, Usuario


class TestUsuario(TestCase):

    def setUp(self):
        self.data_factory = Faker()
        self.client = app.test_client()

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

    def tearDown(self):
        db.session.query(Usuario).filter(Usuario.id == self.id_apostador).delete()
        db.session.commit()

    def test_crear_usuario(self):
        nuevo_usuario = {
            "rol": "Apostador",
            "email": self.data_factory.email(),
            "password": self.data_factory.word(),
            "firstname": self.data_factory.name(),
            "lastname": self.data_factory.name(),

            "creditCard": self.data_factory.random_number(digits=16, fix_len=True),
            "expirationDate": self.data_factory.date_this_century().strftime("%m/%y"),
            "cvv": self.data_factory.random_number(digits=3, fix_len=True),
        }

        solicitud_nuevo_usuario = self.client.post("/signin",
                                                   data=json.dumps(nuevo_usuario),
                                                   headers={'Content-Type': 'application/json'})

        respuesta_al_crear_usuario = json.loads(solicitud_nuevo_usuario.get_data())

        self.token = respuesta_al_crear_usuario["token"]
        self.usuario_code = respuesta_al_crear_usuario["id"]

        self.assertEqual(solicitud_nuevo_usuario.status_code, 200)

    def test_usuario_existe(self):
        emailUsuario = self.data_factory.email()

        first_user = {
            "rol": "Apostador",
            "email": emailUsuario,
            "password": self.data_factory.word(),
            "firstname": self.data_factory.name(),
            "lastname": self.data_factory.name(),

            "creditCard": self.data_factory.random_number(digits=16, fix_len=True),
            "expirationDate": self.data_factory.date_this_century().strftime("%m/%y"),
            "cvv": self.data_factory.random_number(digits=3, fix_len=True),
        }

        self.client.post("/signin", data=json.dumps(first_user), headers={'Content-Type': 'application/json'})

        second_user = {
            "rol": "Apostador",
            "email": emailUsuario,
            "password": self.data_factory.word(),
            "firstname": self.data_factory.name(),
            "lastname": self.data_factory.name(),

            "creditCard": self.data_factory.random_number(digits=16, fix_len=True),
            "expirationDate": self.data_factory.date_this_century().strftime("%m/%y"),
            "cvv": self.data_factory.random_number(digits=3, fix_len=True),
        }

        request = self.client.post("/signin", data=json.dumps(second_user), headers={'Content-Type': 'application/json'})
        response = json.loads(request.get_data())

        self.assertEqual(request.status_code, 400)
        self.assertEqual(response["cod"], "user_exist")

    def test_get_user_transactions(self):
        valor=self.data_factory.random_number(digits=6, fix_len=True)
        transaccion = Transaccion(tipo="recarga_test", 
                                  valor=float(valor),
                                  fecha_creacion=self.data_factory.date_time_this_century(),
                                  id_tarjeta=Usuario.query.filter_by(id=self.id_apostador).first().id_tarjeta)
        db.session.add(transaccion)
        db.session.commit()

        user_transactions = self.client.get(f"/usuario/{self.id_apostador}/transacciones",
                                            headers={"Authorization": f"Bearer {self.apostador_token}"})
        
        user_transactions_data = json.loads(user_transactions.get_data(as_text=True))

        self.assertEqual(user_transactions.status_code, 200)
        recarga_test_found = any(transaccion['tipo'] == 'recarga_test' and  float(transaccion['valor'])  == float(valor) for transaccion in user_transactions_data)
        self.assertTrue(recarga_test_found, "No se encontró ninguna transacción de tipo")
        db.session.delete(transaccion)