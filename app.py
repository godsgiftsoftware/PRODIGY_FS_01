from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
app.config["SECRET_KEY"] = "a_very_secret_and_complex_key_that_you_should_change" # IMPORTANT: Change this!
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login" # This tells Flask-Login which view to redirect to for login

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return f"User(\'{self.username}\, \'{self.email}\')"

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    hire_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Employee(\'{self.first_name}\, \'{self.last_name}\')"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def hello_world():
    return "Hello, World!"

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard")) # Redirect if already logged in

    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered. Please log in.", "danger")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)

        new_user = User(username=username, email=email, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard")) # Redirect if already logged in

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user) # Logs the user in
            flash("Login successful!", "success")
            return redirect(url_for("dashboard")) # Redirect to dashboard after login
        else:
            flash("Login Unsuccessful. Please check email and password.", "danger")
            return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/dashboard")
@login_required # This decorator protects the route
def dashboard():
    return f"Hello, {current_user.username}! Welcome to your dashboard."

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("hello_world"))

@app.route("/add_employee", methods=["GET", "POST"])
@login_required
def add_employee():
    if request.method == "POST":
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        email = request.form["email"]
        phone = request.form["phone"]
        hire_date_str = request.form["hire_date"]

        # Convert hire_date string to datetime object
        hire_date = datetime.strptime(hire_date_str, '%Y-%m-%d')

        existing_employee = Employee.query.filter_by(email=email).first()
        if existing_employee:
            flash("Employee with this email already exists.", "danger")
            return redirect(url_for("add_employee"))
        
        new_employee = Employee(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            hire_date=hire_date
        )
        db.session.add(new_employee)
        db.session.commit()

        flash("Employee added successfully!", "success")
        return redirect(url_for("employees")) # Redirect to a page that list all employees
    return render_template("add_employee.html")

@app.route("/employees")
@login_required
def employees():
    all_employees = Employee.query.all()
    return render_template("employees.html", employees=all_employees)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

@app.route("/edit_employee/<int:id>", methods=["GET", "POST"])
@login_required
def edit_employee(id):
    employee = Employee.query.get_or_404(id)

    if request.method == "POST":
        employee.first_name = request.form["first_name"]
        employee.last_name = request.form["last_name"]
        employee.email = request.form["email"]
        employee.phone = request.form["phone"]
        hire_date_str = request.form["hire_date"]

        # To convert hire_date string to datetime object
        employee.hire_date = datetime.strptime(hire_date_str, '%Y-%m-%d')

        # To check if the email is already used by another employee
        existing_employee = Employee.query.filter_by(email=employee.email).first()
        if existing_employee and existing_employee.id != employee.id:
            flash("An employee with this email already exists.", "danger")
            return redirect(url_for("edit_employee", id=id))

        db.session.commit()
        flash("Employee updated successfully!", "success")
        return redirect(url_for("employees"))

    return render_template("edit_employee.html", employee=employee)