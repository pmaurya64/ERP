from flask import Flask, render_template, request, redirect, url_for, session, g
import sqlite3
from functools import wraps

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
    if db:
        db.close()

# Role-based decorator
def role_required(role):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if 'role' not in session or session['role'] != role:
                return "Access denied", 403
            return f(*args, **kwargs)
        return wrapped
    return wrapper

@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        db = get_db()
        existing = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if existing:
            return "User already exists", 400
        db.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
        db.commit()
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password)).fetchone()
        if user:
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect(url_for('dashboard'))
        return "Invalid credentials", 401
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['username'], role=session['role'])

# Inventory
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

# Employees
@app.route('/employees')
def employees():
    if 'username' not in session:
        return redirect(url_for('login'))
    db = get_db()
    employees = db.execute("SELECT * FROM employees").fetchall()
    return render_template('employees.html', employees=employees)

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

# Sales
@app.route('/sales')
def sales():
    if 'username' not in session:
        return redirect(url_for('login'))
    db = get_db()
    sales = db.execute("SELECT * FROM sales").fetchall()
    return render_template('sales.html', sales=sales)

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

