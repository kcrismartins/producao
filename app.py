from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
api = Api(app)

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pedidos_producao.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='Pendente')

    def __repr__(self):
        return f'<Pedido {self.descricao} - {self.status}>'

@app.before_first_request
def create_tables():
    db.create_all()

class PedidoResource(Resource):
    def get(self):
        pedidos = Pedido.query.all()
        return jsonify([{'id': pedido.id, 'descricao': pedido.descricao, 'status': pedido.status} for pedido in pedidos])

    def post(self):
        data = request.get_json()
        novo_pedido = Pedido(descricao=data['descricao'], status='Pendente')
        db.session.add(novo_pedido)
        db.session.commit()
        return {'message': 'Pedido adicionado à fila de produção', 'id': novo_pedido.id}, 201

class PedidoStatusResource(Resource):
    def patch(self, pedido_id):
        pedido = Pedido.query.get(pedido_id)
        if pedido:
            data = request.get_json()
            pedido.status = data.get('status', pedido.status)
            db.session.commit()
            return {'message': 'Status do pedido atualizado', 'id': pedido.id, 'status': pedido.status}
        return {'message': 'Pedido não encontrado'}, 404

api.add_resource(PedidoResource, '/pedidos')
api.add_resource(PedidoStatusResource, '/pedidos/<int:pedido_id>/status')

if __name__ == '__main__':
    app.run(debug=True)