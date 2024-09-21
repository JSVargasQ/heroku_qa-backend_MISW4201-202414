import json
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

        nuevo_administrador = {
            "rol": "Administrador",
            "usuario": self.data_factory.name(),
            "password": self.data_factory.word(),
            "firstname": self.data_factory.name(),
            "lastname": self.data_factory.name(),
            "email": self.data_factory.email()
        }

        solicitud_nuevo_apostador = self.client.post("/signin",
                                                   data=json.dumps(nuevo_apostador),
                                                   headers={'Content-Type': 'application/json'})

        respuesta_al_crear_apostador = json.loads(solicitud_nuevo_apostador.get_data())

        self.id_apostador = respuesta_al_crear_apostador["id"]
        self.apostador_token = respuesta_al_crear_apostador["token"]

        solicitud_nuevo_administrador = self.client.post("/signin",
                                                   data=json.dumps(nuevo_administrador),
                                                   headers={'Content-Type': 'application/json'})

        respuesta_al_crear_administrador = json.loads(solicitud_nuevo_administrador.get_data())

        self.id_administrador= respuesta_al_crear_administrador["id"]
        self.administrador_token = respuesta_al_crear_administrador["token"]

    def tearDown(self):
        db.session.query(Usuario).filter(Usuario.id == self.id_apostador).delete()
        db.session.query(Usuario).filter(Usuario.id == self.id_administrador).delete()
        db.session.commit()

    def test_crear_usuario(self):
        nuevo_usuario = {
            "rol": "Apostador",
            "usuario": self.data_factory.name(),
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
            "usuario": self.data_factory.name(),
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
            "usuario": self.data_factory.name(),
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

        user_transactions = self.client.get(f"/usuario/{self.id_apostador}/balance_transacciones",
                                            headers={"Authorization": f"Bearer {self.apostador_token}"})
        
        user_transactions_data = json.loads(user_transactions.get_data(as_text=True))
        transactions = user_transactions_data.get("transactions", [])

        self.assertEqual(user_transactions.status_code, 200)
        recarga_test_found = any(transaccion['tipo'] == 'recarga_test' and  float(transaccion['valor'])  == float(valor) for transaccion in transactions)
        self.assertTrue(recarga_test_found, "No se encontró ninguna transacción de tipo")
        db.session.delete(transaccion)

    def test_user_recargar_saldo(self):
        valor = self.data_factory.random_number(digits=6, fix_len=True)
        recarga = {
            "valor": valor
        }

        user_transactions = self.client.get(f"/usuario/{self.id_apostador}/balance_transacciones",
                                            headers={"Authorization": f"Bearer {self.apostador_token}"})
        user_transactions_data = json.loads(user_transactions.get_data(as_text=True))
        saldoinicial = user_transactions_data.get("balance")

        recarga_saldo = self.client.post(f"/usuario/{self.id_apostador}/recargar",
                                         data=json.dumps(recarga),
                                         headers={
                                             "Authorization": f"Bearer {self.apostador_token}",
                                             "Content-Type": "application/json"
                                             })

        user_transactions = self.client.get(f"/usuario/{self.id_apostador}/balance_transacciones",
                                            headers={"Authorization": f"Bearer {self.apostador_token}"})
        
        user_transactions_data = json.loads(user_transactions.get_data(as_text=True))
        saldofinal = user_transactions_data.get("balance")

        self.assertEqual(recarga_saldo.status_code, 200)
        self.assertEqual(saldoinicial+valor, saldofinal)
    
    def test_user_recargar_saldo_noapostador(self):
        valor = self.data_factory.random_number(digits=6, fix_len=True)
        recarga = {
            "valor": valor
        }

        recarga_saldo = self.client.post(f"/usuario/{self.id_administrador}/recargar",
                                    data=json.dumps(recarga),
                                    headers={
                                        "Authorization": f"Bearer {self.apostador_token}",
                                        "Content-Type": "application/json"
                                        })
    
        self.assertEqual(recarga_saldo.status_code, 403)


    def test_user_retirar_saldo(self):
        user_transactions = self.client.get(f"/usuario/{self.id_apostador}/balance_transacciones",
                                            headers={"Authorization": f"Bearer {self.apostador_token}"})
        user_transactions_data = json.loads(user_transactions.get_data(as_text=True))
        saldoinicial = user_transactions_data.get("balance")

        retiro = {
            "valor": saldoinicial
        }

        retiro_saldo = self.client.post(f"/usuario/{self.id_apostador}/retirar",
                                         data=json.dumps(retiro),
                                         headers={
                                             "Authorization": f"Bearer {self.apostador_token}",
                                                "Content-Type": "application/json"
                                                })
        
        user_transactions = self.client.get(f"/usuario/{self.id_apostador}/balance_transacciones",
                                            headers={"Authorization": f"Bearer {self.apostador_token}"})
        user_transactions_data = json.loads(user_transactions.get_data(as_text=True))
        saldofinal = user_transactions_data.get("balance")

        self.assertEqual(retiro_saldo.status_code, 200)
        self.assertEqual(0, saldofinal)
    
    def test_user_retirar_saldo_noapostador(self):
        valor = self.data_factory.random_number(digits=6, fix_len=True)
        retiro = {
            "valor": valor
        }

        retiro_saldo = self.client.post(f"/usuario/{self.id_administrador}/retirar",
                                    data=json.dumps(retiro),
                                    headers={
                                        "Authorization": f"Bearer {self.apostador_token}",
                                        "Content-Type": "application/json"
                                        })
    
        self.assertEqual(retiro_saldo.status_code, 403)


    def test_user_retirar_saldo_insuficiente(self):
        user_transactions = self.client.get(f"/usuario/{self.id_apostador}/balance_transacciones",
                                            headers={"Authorization": f"Bearer {self.apostador_token}"})
        user_transactions_data = json.loads(user_transactions.get_data(as_text=True))
        saldoinicial = user_transactions_data.get("balance")

        retiro = {
            "valor": saldoinicial+1
        }

        retiro_saldo = self.client.post(f"/usuario/{self.id_apostador}/retirar",
                                         data=json.dumps(retiro),
                                         headers={
                                             "Authorization": f"Bearer {self.apostador_token}",
                                                "Content-Type": "application/json"
                                                })

        self.assertEqual(retiro_saldo.status_code, 400)

    def test_get_user_info(self):
        user_info = self.client.get(f"/usuario/{self.id_apostador}",
                                    headers={"Authorization": f"Bearer {self.apostador_token}"})

        user_info_data = json.loads(user_info.get_data(as_text=True))

        self.assertEqual(user_info.status_code, 200)
        self.assertEqual(user_info_data["id"], self.id_apostador)

    def test_get_user_info_bad_id(self):
        user_info = self.client.get(f"/usuario/{self.data_factory.random_int(min=1000, max=9999)}",
                                    headers={"Authorization": f"Bearer {self.apostador_token}"})

        self.assertEqual(user_info.status_code, 404)
