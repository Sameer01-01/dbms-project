from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Medicine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    batch_number = db.Column(db.String(50), nullable=False, unique=True)
    manufacturer = db.Column(db.String(100))
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    expiry_date = db.Column(db.Date, nullable=False)
    date_added = db.Column(db.Date, nullable=False)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100))
    address = db.Column(db.Text)
    medicines_purchased = db.relationship('Medicine', secondary='customer_medicine')

class Retailer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100))
    address = db.Column(db.Text)
    location = db.Column(db.String(100), nullable=False)

# New Supplier model
class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100))
    address = db.Column(db.Text)
    company = db.Column(db.String(100), nullable=False)
    date_added = db.Column(db.Date, nullable=False, default=datetime.now().date())

# New Prescription model
class Prescription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    patient = db.relationship('Customer', backref='prescriptions')
    doctor_name = db.Column(db.String(100), nullable=False)
    date_prescribed = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text)
    date_added = db.Column(db.Date, nullable=False, default=datetime.now().date())

# Association table between prescriptions and medicines
prescription_medicine = db.Table('prescription_medicine',
    db.Column('prescription_id', db.Integer, db.ForeignKey('prescription.id')),
    db.Column('medicine_id', db.Integer, db.ForeignKey('medicine.id')),
    db.Column('dosage', db.String(50))
)

# Association table for many-to-many relationship between customers and medicines
customer_medicine = db.Table('customer_medicine',
    db.Column('customer_id', db.Integer, db.ForeignKey('customer.id')),
    db.Column('medicine_id', db.Integer, db.ForeignKey('medicine.id'))
)