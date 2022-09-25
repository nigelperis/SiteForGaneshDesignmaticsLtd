from flask import Flask, render_template, url_for, redirect, request, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError, Email
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message

app = Flask(__name__)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = "filesystem"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'secretkey'
Session(app)
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'ganeshdesignmatics@gmail.com'
app.config['MAIL_PASSWORD'] = 'xikzdaurqznxrptq'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True  
mail = Mail(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "dashboard"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)


class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Email(granular_message=True)], render_kw={"placeholder": "Email"})
    password = PasswordField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField("Register")

    def validate_username(self, username):
        existing_user_name = User.query.filter_by(
            username=username.data).first()
        if existing_user_name:
            raise ValidationError("Email already exists")



class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Email(granular_message=True)], render_kw={"placeholder": "Email"})
    password = PasswordField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField("login")


@app.route("/")
def home(): 
    loggedin = session["loggedin"] if "loggedin" in session.keys() else False
    username = session["username"] if "username" in session.keys() else None
    return render_template("dashboard.html", username=username, loggedin=loggedin)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    error = None
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                session['username'] = user.username.split('@')[0]
                session['loggedin'] = True  
                return redirect(url_for("dashboard"))
            else:
                error = "Incorrect Email or Password"
        else:
            error = "Incorrect Email or Password"

    return render_template("login.html", form=form, error=error)


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    error = None
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    else:
        error = form.errors

    return render_template("register.html", form=form, error=error)


@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    loggedin = session["loggedin"] if "loggedin" in session.keys() else False
    username = session["username"] if "username" in session.keys() else None
    return render_template('dashboard.html', username=username, loggedin=loggedin)


@app.route("/logout", methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    session['username'] = None
    session['loggedin'] = False
    return redirect(url_for('dashboard'))

@app.route("/contact", methods=['GET', 'POST'])
def contact():
    loggedin = session["loggedin"] if "loggedin" in session.keys() else False
    username = session["username"] if "username" in session.keys() else None
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        message = request.form.get("message")
        msg = Message('Client Message', sender = email, recipients = ['ganeshdesignmatics@gmail.com'])
        msg.body = f'Name: {name}\nEmail: {email}\nMessage: {message}'
        mail.send(msg)
        return render_template("contact.html", msg=True)
    return render_template("contact.html", username=username, loggedin=loggedin)

@app.route("/gallery")
def gallery():
    loggedin = session["loggedin"] if "loggedin" in session.keys() else False
    username = session["username"] if "username" in session.keys() else None
    return render_template("gallery.html", username=username, loggedin=loggedin)

@app.route("/about")
def about():
    loggedin = session["loggedin"] if "loggedin" in session.keys() else False
    username = session["username"] if "username" in session.keys() else None
    return render_template("about.html", username=username, loggedin=loggedin)


if __name__ == "__main__":
    app.run(debug=True)
