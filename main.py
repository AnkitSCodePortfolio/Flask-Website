from flask import Flask, flash, render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import secrets
app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = (
    "mssql+pyodbc:///?odbc_connect="
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=PS-IN-LT-22307\\SQLEXPRESS;"
    "DATABASE=UserInfo;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class LoginModel(db.Model):
    Id = db.Column(db.Integer, primary_key=True)
    Login = db.Column(db.String(200), nullable=False)
    Password = db.Column(db.String(200), nullable=False)

    def __repr__(self) -> str:
        return f"{self.Id} - {self.Login} - {self.Password}"
    
class SignUpModel(db.Model):
    Id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(200), nullable=False)
    Login = db.Column(db.String(200), nullable=False)
    Password = db.Column(db.String(200), nullable=False)
    Role = db.Column(db.String(200), nullable=False, default='User')

    def __repr__(self) -> str:
        return f"{self.Id} - {self.Name} - {self.Login} - {self.Password} "

class DataModel(db.Model):
    Id = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String(200), nullable=False)
    Name = db.Column(db.String(200), nullable=False)
    Description = db.Column(db.String(300), nullable=True)

    def __repr__(self) -> str:
        return f"{self.Id} - {self.Name} - {self.Description} - {self.Title}"


@app.route("/", methods=['GET', 'POST'])
def Login():
    errors = {}
    if request.method == 'POST':
        login = request.form['Login']
        password = request.form['Password']

        if not login:
            errors['Login'] = 'Username is required.'

        if not password:
            errors['Password'] = 'Password is required.'

        if errors:
            return render_template('Login.html', errors=errors)
        
        user_exists = SignUpModel.query.filter_by(Login=login, Password=password).first()
        
        if user_exists:
            credentials = LoginModel(Login=login, Password=password)
            db.session.add(credentials)
            db.session.commit()
            return redirect("/Home")
        else:
            flash('Invalid credentials. Please sign up first.')
    
    operation = LoginModel.query.all()
    return render_template('Login.html', errors=errors, operation=operation)


@app.route('/Signup', methods=['GET', 'POST'])
def Signup():
    errors = {}
    if request.method == 'POST':
        name = request.form['Name']
        login = request.form['Login']
        password = request.form['Password']
        
        if not name:
            errors['Name'] = 'Name is required.'

        if not login:
            errors['Login'] = 'Username is required.'

        if not password:
            errors['Password'] = 'Password is required.'

        if errors:
            return render_template('Signup.html', errors=errors)

        existing_user = SignUpModel.query.filter_by(Login=login).first()
        
        if existing_user:
            flash('Username already exists. Please choose a different username.')
        else:
            try:
                new_user = SignUpModel(Name=name, Login=login, Password=password)
                db.session.add(new_user)
                db.session.commit()
                
                flash('Signup successful! Please login.')
                return redirect("/")
            except Exception as e:
                flash(f"Error occurred: {str(e)}")
                db.session.rollback()

    return render_template('Signup.html', errors=errors)


@app.route("/Home")
def Home():
    operation = DataModel.query.all()
    return render_template('Home.html', operation=operation)

@app.route("/Products", methods=['GET', 'POST'])
def ProductsAdd():
    if request.method == 'POST':
        name = request.form['Name']
        title = request.form['Title']
        description = request.form['Description']
        operations = DataModel(Name=name, Title=title, Description=description)
        db.session.add(operations)
        db.session.commit()
        return redirect("/Home")
    operations = DataModel.query.all()
    return render_template('Product.html', operations=operations)

@app.route("/ProductsUpdate/<int:Id>", methods=['GET', 'POST'])
def ProductsUpdate(Id):
    operations = DataModel.query.filter_by(Id=Id).first()
    if request.method == 'POST':
        name = request.form['Name']
        title = request.form['Title']
        description = request.form['Description']
        operations.Name = name
        operations.Title = title
        operations.Description = description
        db.session.commit()
        return redirect("/Home")
    
    return render_template('Products.html', operations=operations)


@app.route("/ProductsDelete/<int:Id>", methods=['POST'])
def ProductsDelete(Id):
    operation = DataModel.query.filter_by(Id=Id).first()
    db.session.delete(operation)
    db.session.commit()
    return redirect('/Home')

if __name__ == "__main__":
    app.run(debug=True)
