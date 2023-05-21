from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy import UniqueConstraint


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@localhost/flaskmysql'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    nombre = db.Column(db.String(70))
    descripcion = db.Column(db.String(100))
    categoria = db.Column(db.String(30))
    precio = db.Column(db.Float)
    stock = db.Column(db.Integer)


class Pedidos(db.Model):
    id_pedido = db.Column(db.Integer, primary_key=True)



class DetallePedido(db.Model):
    id_pedido = db.Column(db.Integer, db.ForeignKey('pedidos.id_pedido'), primary_key=True)
    id_task = db.Column(db.Integer, db.ForeignKey('task.id'), primary_key=True)
    cantidad = db.Column(db.Integer)

    task = db.relationship('Task')
    pedido = db.relationship('Pedidos')

    __table_args__ = (
        UniqueConstraint('id_pedido', 'id_task', name='_id_pedido_id_task_uc'),
    )
    

    def __init__(self, nombre, descripcion, categoria, precio, stock):
        super().__init__()
        self.nombre = nombre
        self.descripcion = descripcion
        self.categoria = categoria
        self.precio = precio
        self.stock = stock

    def __init__(self):
        super().__init__()

    def __init__(self, id_pedido = None, id_task = None, cantidad = None):
        super().__init__()
        self.id_pedido = id_pedido
        self.id_task = id_task
        self.cantidad = cantidad


class TaskSchema(ma.Schema):
    class Meta:
        fields = ('id','nombre','descripcion', 'categoria', 'precio', 'stock' )

task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)

@app.route('/tasks', methods = ['POST'])
def create_task():

    nombre = request.json['nombre']
    descripcion = request.json['descripcion']
    categoria = request.json['categoria']
    precio = request.json['precio']
    stock = request.json['stock']

    new_task = Task(nombre, descripcion, categoria, precio, stock)
    db.session.add(new_task)
    db.session.commit()

    return task_schema.jsonify(new_task)


@app.route('/tasks', methods=['GET'])
def get_tasks():
  all_tasks = Task.query.all()
  result = tasks_schema.dump(all_tasks)
  return jsonify(result)

@app.route('/tasks/<id>', methods=['GET'])
def get_task(id):
  task = Task.query.get(id)
  return task_schema.jsonify(task)

@app.route('/tasks/<id>', methods=['PUT'])
def update_task(id):
  task = Task.query.get(id)

  nombre = request.json['nombre']
  descripcion = request.json['descripcion']
  categoria = request.json['categoria']
  precio = request.json['precio']
  stock = request.json['stock']

  task.nombre = nombre
  task.descripcion = descripcion
  task.categoria = categoria
  task.precio = precio
  task.stock = stock


  db.session.commit()

  return task_schema.jsonify(task)

@app.route('/tasks/<id>', methods=['DELETE'])
def delete_task(id):
  task = Task.query.get(id)
  db.session.delete(task)
  db.session.commit()
  return task_schema.jsonify(task)

@app.route('/tasks/stock-gt-zero', methods=['GET'])
def get_tasks_with_stock():
    tasks_with_stock = Task.query.filter(Task.stock > 0).all()
    result = tasks_schema.dump(tasks_with_stock)
    return jsonify(result)

@app.route('/tasks/update-stock/<id>', methods=['PUT'])
def update_task_stock(id):
    task = Task.query.get(id)

    if not task:
        return jsonify({'message': 'Task not found'}), 404

    new_stock = request.json['stock']
    task.stock = new_stock

    db.session.commit()

    return task_schema.jsonify(task)


@app.route('/pedidos', methods=['POST'])
def create_pedido():
    id_pedido = request.json['id_pedido']

    # Crear un nuevo objeto Pedidos y asignar el id_pedido
    new_pedido = Pedidos(id_pedido=id_pedido)
    db.session.add(new_pedido)
    db.session.commit()

    return task_schema.jsonify(new_pedido)

@app.route('/detalle-pedidos', methods=['POST'])
def create_detalle_pedido():
    id_pedido = request.json['id_pedido']
    id_task = request.json['id']
    cantidad = request.json['cantidad']

    # Verificar si existen el pedido y la tarea en la base de datos
    pedido = Pedidos.query.get(id_pedido)
    task = Task.query.get(id_task)

    if not pedido:
        return jsonify({'message': 'Pedido not found'}), 404

    if not task:
        return jsonify({'message': 'Task not found'}), 404

    # Crear un nuevo objeto DetallePedido y asignar el pedido, la tarea y la cantidad
    new_detalle_pedido = DetallePedido(id_pedido=id_pedido, id_task=id_task, cantidad=cantidad)
    db.session.add(new_detalle_pedido)
    db.session.commit()

    return jsonify({'message': 'DetallePedido created successfully'})





  
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)