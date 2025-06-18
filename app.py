from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return f"User(\\\'{self.username}\\, \\'{self.email}\\,)"

@app.route("/")
def hello_world():
    return "Hello, World!"

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)