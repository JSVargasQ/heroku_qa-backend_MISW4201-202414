from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_restful import Api

from modelos import db
from vistas import VistaApuestas, VistaApuesta, VistaSignIn, VistaLogIn, VistaCarrerasUsuario, \
    VistaCarrera, VistaTerminacionCarrera, VistaReporte, VistaUsuarios, VistaUsuario, VistaTransaccionesUsuario, \
    VistaUserBalanceAndTransactions, VistaApuestasApostador, VistaRecargar, VistaRetirar

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///eporra.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'frase-secreta'
app.config['PROPAGATE_EXCEPTIONS'] = True

app_context = app.app_context()
app_context.push()

db.init_app(app)
db.create_all()

cors = CORS(app)

api = Api(app)
api.add_resource(VistaSignIn, '/signin')
api.add_resource(VistaLogIn, '/login')
api.add_resource(VistaCarrerasUsuario, '/usuario/<int:id_usuario>/eventos')
api.add_resource(VistaCarrera, '/evento/<int:id_evento>')
api.add_resource(VistaApuestas, '/apuestas')
api.add_resource(VistaApuesta, '/apuesta/<int:id_apuesta>')
api.add_resource(VistaTerminacionCarrera, '/evento/<int:id_posible_resultado>/terminacion')
api.add_resource(VistaReporte, '/evento/<int:id_evento>/reporte')
api.add_resource(VistaUsuarios, '/apostadores')
api.add_resource(VistaUsuario, '/usuario/<int:id_usuario>')
api.add_resource(VistaTransaccionesUsuario, '/usuario/<int:id_usuario>/transacciones')
api.add_resource(VistaUserBalanceAndTransactions, '/usuario/<int:id_usuario>/balance_transacciones')
api.add_resource(VistaRecargar, '/usuario/<int:id_usuario>/recargar')
api.add_resource(VistaRetirar, '/usuario/<int:id_usuario>/retirar')
api.add_resource(VistaApuestasApostador, '/usuario/<int:id_usuario>/apuestas')


jwt = JWTManager(app)
