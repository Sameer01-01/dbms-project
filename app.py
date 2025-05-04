from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from database import db, User, Medicine, Customer, Retailer, Supplier, Prescription, prescription_medicine, customer_medicine
from config import Config
from datetime import datetime
import os

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db.init_app(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create database tables
with app.app_context():
    # Force drop all tables and recreate them (only for development!)
    # db.drop_all()
    db.create_all()
    
    # Create admin user if not exists
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
    
    # Create a sample supplier if none exists
    if not Supplier.query.first():
        sample_supplier = Supplier(
            name="MedSupply Inc.",
            contact="123-456-7890",
            email="contact@medsupply.com",
            address="123 Medical Drive, Pharma City",
            company="MedSupply Pharmaceuticals",
            date_added=datetime.now().date()
        )
        db.session.add(sample_supplier)
        db.session.commit()
    
    # Create a sample prescription if none exists and there's at least one customer
    customer = Customer.query.first()
    if customer and not Prescription.query.first():
        sample_prescription = Prescription(
            patient_id=customer.id,
            doctor_name="Dr. John Smith",
            date_prescribed=datetime.now().date(),
            notes="Take twice daily after meals",
            date_added=datetime.now().date()
        )
        db.session.add(sample_prescription)
        db.session.commit()

# Routes
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    now = datetime.now()
    return render_template('dashboard.html', Medicine=Medicine, Customer=Customer, Retailer=Retailer, Supplier=Supplier, Prescription=Prescription, now=now)

# Medicines routes
@app.route('/medicines', methods=['GET', 'POST'])
@login_required
def medicines():
    if request.method == 'POST':
        if 'delete_id' in request.form:
            # Delete medicine
            medicine = Medicine.query.get(request.form['delete_id'])
            if medicine:
                db.session.delete(medicine)
                db.session.commit()
                flash('Medicine deleted successfully!', 'success')
        else:
            # Add new medicine
            name = request.form['name']
            batch_number = request.form['batch_number']
            manufacturer = request.form['manufacturer']
            quantity = int(request.form['quantity'])
            price = float(request.form['price'])
            expiry_date = datetime.strptime(request.form['expiry_date'], '%Y-%m-%d').date()
            
            medicine = Medicine(
                name=name,
                batch_number=batch_number,
                manufacturer=manufacturer,
                quantity=quantity,
                price=price,
                expiry_date=expiry_date,
                date_added=datetime.now().date()
            )
            
            db.session.add(medicine)
            db.session.commit()
            flash('Medicine added successfully!', 'success')
        
        return redirect(url_for('medicines'))
    
    # Get sorting parameters
    sort_by = request.args.get('sort_by', 'id')
    order = request.args.get('order', 'asc')
    
    # Validate sort parameters
    valid_sort_columns = ['id', 'name', 'date_added']
    if sort_by not in valid_sort_columns:
        sort_by = 'id'
    
    # Apply sorting
    if order == 'asc':
        medicines = Medicine.query.order_by(getattr(Medicine, sort_by)).all()
    else:
        medicines = Medicine.query.order_by(getattr(Medicine, sort_by).desc()).all()
    
    return render_template('medicines.html', medicines=medicines, sort_by=sort_by, order=order)

# Add edit medicine route
@app.route('/edit_medicine/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_medicine(id):
    medicine = Medicine.query.get_or_404(id)
    
    if request.method == 'POST':
        medicine.name = request.form['name']
        medicine.batch_number = request.form['batch_number']
        medicine.manufacturer = request.form['manufacturer']
        medicine.quantity = int(request.form['quantity'])
        medicine.price = float(request.form['price'])
        medicine.expiry_date = datetime.strptime(request.form['expiry_date'], '%Y-%m-%d').date()
        
        db.session.commit()
        flash('Medicine updated successfully!', 'success')
        return redirect(url_for('medicines'))
    
    return render_template('edit_medicine.html', medicine=medicine)

# Customers routes
@app.route('/customers', methods=['GET', 'POST'])
@login_required
def customers():
    if request.method == 'POST':
        if 'delete_id' in request.form:
            # Delete customer
            customer = Customer.query.get(request.form['delete_id'])
            if customer:
                db.session.delete(customer)
                db.session.commit()
                flash('Customer deleted successfully!', 'success')
        else:
            # Add new customer
            name = request.form['name']
            contact = request.form['contact']
            email = request.form.get('email', '')
            address = request.form.get('address', '')
            
            customer = Customer(
                name=name,
                contact=contact,
                email=email,
                address=address
            )
            
            db.session.add(customer)
            db.session.commit()
            flash('Customer added successfully!', 'success')
        
        return redirect(url_for('customers'))
    
    # Get sorting parameters
    sort_by = request.args.get('sort_by', 'id')
    
    # Validate sort parameters
    valid_sort_columns = ['id', 'name']
    if sort_by not in valid_sort_columns:
        sort_by = 'id'
    
    # Apply sorting
    customers = Customer.query.order_by(getattr(Customer, sort_by)).all()
    
    return render_template('customers.html', customers=customers, sort_by=sort_by)

# Add edit customer route
@app.route('/edit_customer/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_customer(id):
    customer = Customer.query.get_or_404(id)
    
    if request.method == 'POST':
        customer.name = request.form['name']
        customer.contact = request.form['contact']
        customer.email = request.form.get('email', '')
        customer.address = request.form.get('address', '')
        
        db.session.commit()
        flash('Customer updated successfully!', 'success')
        return redirect(url_for('customers'))
    
    return render_template('edit_customer.html', customer=customer)

# Retailers routes
@app.route('/retailers', methods=['GET', 'POST'])
@login_required
def retailers():
    if request.method == 'POST':
        if 'delete_id' in request.form:
            # Delete retailer
            retailer = Retailer.query.get(request.form['delete_id'])
            if retailer:
                db.session.delete(retailer)
                db.session.commit()
                flash('Retailer deleted successfully!', 'success')
        else:
            # Add new retailer
            name = request.form['name']
            contact = request.form['contact']
            email = request.form.get('email', '')
            address = request.form.get('address', '')
            location = request.form['location']
            
            retailer = Retailer(
                name=name,
                contact=contact,
                email=email,
                address=address,
                location=location
            )
            
            db.session.add(retailer)
            db.session.commit()
            flash('Retailer added successfully!', 'success')
        
        return redirect(url_for('retailers'))
    
    # Get sorting parameters
    sort_by = request.args.get('sort_by', 'location')
    order = request.args.get('order', 'asc')
    
    # Validate sort parameters
    valid_sort_columns = ['id', 'name', 'location']
    if sort_by not in valid_sort_columns:
        sort_by = 'location'
    
    # Apply sorting
    if order == 'asc':
        retailers = Retailer.query.order_by(getattr(Retailer, sort_by)).all()
    else:
        retailers = Retailer.query.order_by(getattr(Retailer, sort_by).desc()).all()
    
    return render_template('retailers.html', retailers=retailers, sort_by=sort_by, order=order)

# Add edit retailer route
@app.route('/edit_retailer/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_retailer(id):
    retailer = Retailer.query.get_or_404(id)
    
    if request.method == 'POST':
        retailer.name = request.form['name']
        retailer.contact = request.form['contact']
        retailer.email = request.form.get('email', '')
        retailer.address = request.form.get('address', '')
        retailer.location = request.form['location']
        
        db.session.commit()
        flash('Retailer updated successfully!', 'success')
        return redirect(url_for('retailers'))
    
    return render_template('edit_retailer.html', retailer=retailer)

# Suppliers routes
@app.route('/suppliers', methods=['GET', 'POST'])
@login_required
def suppliers():
    if request.method == 'POST':
        if 'delete_id' in request.form:
            # Delete supplier
            supplier = Supplier.query.get(request.form['delete_id'])
            if supplier:
                db.session.delete(supplier)
                db.session.commit()
                flash('Supplier deleted successfully!', 'success')
        else:
            # Add new supplier
            name = request.form['name']
            contact = request.form['contact']
            email = request.form.get('email', '')
            address = request.form.get('address', '')
            company = request.form['company']
            
            supplier = Supplier(
                name=name,
                contact=contact,
                email=email,
                address=address,
                company=company,
                date_added=datetime.now().date()
            )
            
            db.session.add(supplier)
            db.session.commit()
            flash('Supplier added successfully!', 'success')
        
        return redirect(url_for('suppliers'))
    
    # Get sorting parameters
    sort_by = request.args.get('sort_by', 'name')
    order = request.args.get('order', 'asc')
    
    # Validate sort parameters
    valid_sort_columns = ['id', 'name', 'company']
    if sort_by not in valid_sort_columns:
        sort_by = 'name'
    
    # Apply sorting
    if order == 'asc':
        suppliers = Supplier.query.order_by(getattr(Supplier, sort_by)).all()
    else:
        suppliers = Supplier.query.order_by(getattr(Supplier, sort_by).desc()).all()
    
    return render_template('suppliers.html', suppliers=suppliers, sort_by=sort_by, order=order)

@app.route('/edit_supplier/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_supplier(id):
    supplier = Supplier.query.get_or_404(id)
    
    if request.method == 'POST':
        supplier.name = request.form['name']
        supplier.contact = request.form['contact']
        supplier.email = request.form.get('email', '')
        supplier.address = request.form.get('address', '')
        supplier.company = request.form['company']
        
        db.session.commit()
        flash('Supplier updated successfully!', 'success')
        return redirect(url_for('suppliers'))
    
    return render_template('edit_supplier.html', supplier=supplier)

# Prescriptions routes
@app.route('/prescriptions', methods=['GET', 'POST'])
@login_required
def prescriptions():
    if request.method == 'POST':
        if 'delete_id' in request.form:
            # Delete prescription
            prescription = Prescription.query.get(request.form['delete_id'])
            if prescription:
                db.session.delete(prescription)
                db.session.commit()
                flash('Prescription deleted successfully!', 'success')
        else:
            # Add new prescription
            patient_id = request.form['patient_id']
            doctor_name = request.form['doctor_name']
            date_prescribed = datetime.strptime(request.form['date_prescribed'], '%Y-%m-%d').date()
            notes = request.form.get('notes', '')
            
            prescription = Prescription(
                patient_id=patient_id,
                doctor_name=doctor_name,
                date_prescribed=date_prescribed,
                notes=notes,
                date_added=datetime.now().date()
            )
            
            db.session.add(prescription)
            db.session.commit()
            flash('Prescription added successfully!', 'success')
        
        return redirect(url_for('prescriptions'))
    
    # Get sorting parameters
    sort_by = request.args.get('sort_by', 'date_prescribed')
    order = request.args.get('order', 'desc')
    
    # Validate sort parameters
    valid_sort_columns = ['id', 'doctor_name', 'date_prescribed', 'date_added']
    if sort_by not in valid_sort_columns:
        sort_by = 'date_prescribed'
    
    # Apply sorting
    if order == 'asc':
        prescriptions = Prescription.query.order_by(getattr(Prescription, sort_by)).all()
    else:
        prescriptions = Prescription.query.order_by(getattr(Prescription, sort_by).desc()).all()
    
    customers = Customer.query.all()
    return render_template('prescriptions.html', prescriptions=prescriptions, customers=customers, sort_by=sort_by, order=order)

@app.route('/edit_prescription/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_prescription(id):
    prescription = Prescription.query.get_or_404(id)
    
    if request.method == 'POST':
        prescription.patient_id = request.form['patient_id']
        prescription.doctor_name = request.form['doctor_name']
        prescription.date_prescribed = datetime.strptime(request.form['date_prescribed'], '%Y-%m-%d').date()
        prescription.notes = request.form.get('notes', '')
        
        db.session.commit()
        flash('Prescription updated successfully!', 'success')
        return redirect(url_for('prescriptions'))
    
    customers = Customer.query.all()
    return render_template('edit_prescription.html', prescription=prescription, customers=customers)

if __name__ == '__main__':
    app.run(debug=True)