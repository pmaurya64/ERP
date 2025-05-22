from flask import Flask, render_template, request, redirect, url_for, session, g
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DATABASE = 'erp.db'

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# Simple user auth with role (just for example)
users = {
    'admin': {'password': 'admin123', 'role': 'admin'},
    'user': {'password': 'user123', 'role': 'user'}
}

@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users.get(username)
        if user and user['password'] == password:
            session['username'] = username
            session['role'] = user['role']
            return redirect(url_for('dashboard'))
        return "Invalid credentials", 401
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['username'], role=session['role'])

# Role-based access decorator
from functools import wraps
def role_required(role):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if 'role' not in session or session['role'] != role:
                return "Access denied", 403
            return f(*args, **kwargs)
        return wrapped
    return wrapper

# Inventory Module CRUD
@app.route('/inventory')
def inventory():
    if 'username' not in session:
        return redirect(url_for('login'))
    db = get_db()
    items = db.execute("SELECT * FROM inventory").fetchall()
    return render_template('inventory.html', items=items)

@app.route('/inventory/add', methods=['POST'])
@role_required('admin')
def add_inventory():
    name = request.form['name']
    quantity = request.form['quantity']
    db = get_db()
    db.execute("INSERT INTO inventory (name, quantity) VALUES (?, ?)", (name, quantity))
    db.commit()
    return redirect(url_for('inventory'))

@app.route('/inventory/delete/<int:id>')
@role_required('admin')
def delete_inventory(id):
    db = get_db()
    db.execute("DELETE FROM inventory WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for('inventory'))

# Employees Module CRUD
@app.route('/employees')
def employees():
    if 'username' not in session:
        return redirect(url_for('login'))
    db = get_db()
    staff = db.execute("SELECT * FROM employees").fetchall()
    return render_template('employees.html', employees=staff)

@app.route('/employees/add', methods=['POST'])
@role_required('admin')
def add_employee():
    name = request.form['name']
    role = request.form['role']
    db = get_db()
    db.execute("INSERT INTO employees (name, role) VALUES (?, ?)", (name, role))
    db.commit()
    return redirect(url_for('employees'))

@app.route('/employees/delete/<int:id>')
@role_required('admin')
def delete_employee(id):
    db = get_db()
    db.execute("DELETE FROM employees WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for('employees'))

# Sales Module CRUD
@app.route('/sales')
def sales():
    if 'username' not in session:
        return redirect(url_for('login'))
    db = get_db()
    sales_list = db.execute("SELECT * FROM sales").fetchall()
    return render_template('sales.html', sales=sales_list)

@app.route('/sales/add', methods=['POST'])
@role_required('admin')
def add_sale():
    item = request.form['item']
    amount = request.form['amount']
    db = get_db()
    db.execute("INSERT INTO sales (item, amount) VALUES (?, ?)", (item, amount))
    db.commit()
    return redirect(url_for('sales'))

@app.route('/sales/delete/<int:id>')
@role_required('admin')
def delete_sale(id):
    db = get_db()
    db.execute("DELETE FROM sales WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for('sales'))

if __name__ == '__main__':
    app.run(debug=True)

