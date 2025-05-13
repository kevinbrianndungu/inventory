from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from pymongo import MongoClient
from datetime import datetime
import os
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from email_validator import validate_email, EmailNotValidError

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# SQLite Database
db = SQLAlchemy(app)

# MongoDB Connection
mongo_client = MongoClient('mongodb://localhost:27017/')
mongo_db = mongo_client['inventory_db']

# Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    job_id = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    items = db.relationship('Item', backref='department', lazy=True)
    users = db.relationship('User', backref='department', lazy=True)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, default=0)
    condition = db.Column(db.String(50))
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
@login_required
def index():
    departments = Department.query.all()
    return render_template('index.html', departments=departments)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        department_id = request.form['department_id']
        job_id = request.form['job_id']

        # Validate email
        try:
            validate_email(email)
        except EmailNotValidError:
            flash('Invalid email address', 'danger')
            return redirect(url_for('signup'))

        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('signup'))
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
            return redirect(url_for('signup'))

        user = User(
            username=username,
            email=email,
            department_id=department_id,
            job_id=job_id
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))

    departments = Department.query.all()
    return render_template('signup.html', departments=departments)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        
        flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

@app.route('/department/<int:dept_id>')
@login_required
def department_view(dept_id):
    department = Department.query.get_or_404(dept_id)
    items = Item.query.filter_by(department_id=dept_id).all()
    return render_template('department.html', department=department, items=items)

@app.route('/add_item', methods=['GET', 'POST'])
@login_required
def add_item():
    if request.method == 'POST':
        name = request.form['name']
        quantity = request.form['quantity']
        condition = request.form['condition']
        department_id = request.form['department_id']
        
        new_item = Item(
            name=name,
            quantity=quantity,
            condition=condition,
            department_id=department_id
        )
        
        db.session.add(new_item)
        db.session.commit()
        flash('Item added successfully!', 'success')
        return redirect(url_for('department_view', dept_id=department_id))
    
    departments = Department.query.all()
    return render_template('add_item.html', departments=departments)

@app.route('/update_item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def update_item(item_id):
    item = Item.query.get_or_404(item_id)
    if request.method == 'POST':
        item.name = request.form['name']
        item.quantity = request.form['quantity']
        item.condition = request.form['condition']
        item.last_updated = datetime.utcnow()
        
        db.session.commit()
        flash('Item updated successfully!', 'success')
        return redirect(url_for('department_view', dept_id=item.department_id))
    
    return render_template('update_item.html', item=item)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Initialize departments if they don't exist
        if not Department.query.first():
            departments = [
                Department(name='Accounts'),
                Department(name='Sales & Purchases'),
                Department(name='IT & Marketing'),
                Department(name='Masters and Costings')
            ]
            db.session.add_all(departments)
            db.session.commit()
    app.run(debug=True) 
