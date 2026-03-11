from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
import mysql.connector

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

# @app.route("/menu")
# def menu():
#     all_items = Item.query.all()
#     return render_template('menu.html', items=all_items)





# @app.route("/menu")
# def menu():
#     search = request.args.get("search")

#     if search:
#         items = Item.query.filter(Item.name.ilike(f"%{search}%")).all()
#     else:
#         items = Item.query.all()

#     return render_template("menu.html", items=items)


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

@app.route("/feedback")
def feedback():
    return render_template("feedback.html")

#  pay bill
@app.route("/payment/<int:order_id>")
def payment(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template("payment.html", order=order)

@app.route("/process_payment/<int:order_id>", methods=["POST"])
def process_payment(order_id):
    # Normally, you'd integrate Razorpay/Stripe here
    # For demo, just show "Payment Successful"
    order = Order.query.get_or_404(order_id)
    return f"<h2 style='color:green;text-align:center;'>Payment Successful for {order.customer_name} - ₹{order.bill.total_amount}</h2>"





@app.route("/bill/<int:order_id>")
def bill_page(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template("bill.html", order=order)


#  search items in menu

@app.route("/menu")
def menu():
    search = request.args.get("search")

    if search:
        items = Item.query.filter(Item.name.ilike(f"%{search}%")).all()
    else:
        items = Item.query.all()

    return render_template("menu.html", items=items)
 


 #  add items

@app.route("/add_item", methods=["GET", "POST"])
def add_item():

    if request.method == "POST":
        name = request.form["name"]
        price = request.form["price"]

        new_item = Item(name=name, price=price)

        db.session.add(new_item)
        db.session.commit()

        return redirect(url_for("menu"))

    return render_template("add_item.html")

# updat price of item

@app.route("/update_item/<int:id>", methods=["GET","POST"])
def update_item(id):

    item = Item.query.get_or_404(id)

    if request.method == "POST":
        item.price = request.form["price"]
        db.session.commit()

        return redirect(url_for("menu"))

    return render_template("update_item.html", item=item)

#  display a order hstory

@app.route("/bills_history")
def bills_history():

    import mysql.connector

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="world",
        database="canteen_db"
    )

    cursor = conn.cursor()

    query = "SELECT id, order_id, total_amount, generated_at FROM bills ORDER BY generated_at DESC"
    cursor.execute(query)

    bills = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("bills_history.html", bills=bills)

 
if __name__ == "__main__":
    app.run(debug=True)