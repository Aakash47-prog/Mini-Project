from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Database config
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:world@localhost/canteen_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ---------------- Models ----------------
class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    order_items = db.relationship('OrderItem', backref='order', cascade="all, delete", lazy=True)
    bill = db.relationship('Bill', backref='order', uselist=False, cascade="all, delete", lazy=True)

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id', ondelete='CASCADE'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    item = db.relationship('Item', backref='order_items', lazy=True)

class Bill(db.Model):
    __tablename__ = 'bills'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id', ondelete='CASCADE'), unique=True, nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    generated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

# ---------------- Routes ----------------
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/menu")
def menu():
    all_items = Item.query.all()
    return render_template('menu.html', items=all_items)

@app.route("/place_order", methods=["POST"])
def place_order():
    customer_name = request.form.get("customer_name")
    order = Order(customer_name=customer_name)
    db.session.add(order)
    db.session.flush()

    total_amount = 0
    items = Item.query.all()
    for item in items:
        qty = int(request.form.get(f"quantity_{item.id}", 0))
        if qty > 0:
            order_item = OrderItem(order_id=order.id, item_id=item.id, quantity=qty)
            db.session.add(order_item)
            total_amount += float(item.price) * qty

    bill = Bill(order_id=order.id, total_amount=total_amount)
    db.session.add(bill)
    db.session.commit()

    return redirect(url_for("bill_page", order_id=order.id))

@app.route("/bill/<int:order_id>")
def bill_page(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template("bill.html", order=order)

if __name__ == "__main__":
    app.run(debug=True)
