from flask import Flask , render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:world@localhost/canteen_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

@app.route("/")
def home():
    return render_template('menu.html')

@app.route("/products")
def products():
    # render_template('index.html')
    return "Products page"

if __name__ == "__main__":
    app.run(debug=True)
