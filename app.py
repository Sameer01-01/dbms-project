from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from database import db, User, Medicine, Customer, Retailer
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
    db.create_all()
    # Create admin user if not exists
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin')
        admin.set_password('admin123')
        db.session.add(admin)
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
    return render_template('dashboard.html', Medicine=Medicine, Customer=Customer, Retailer=Retailer)

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

if __name__ == '__main__':
    app.run(debug=True)