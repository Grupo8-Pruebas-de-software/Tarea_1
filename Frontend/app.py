
from flask import Flask, render_template, request, redirect, url_for, flash, session
import sys, os, requests
sys.path.append(os.path.abspath("../Backend"))  # Para importar auth.py
import auth
import eventos


app = Flask(__name__)
app.secret_key = "supersecret"  # Necesario para flash mensajes
API_URL = 'http://localhost:8000'

@app.route("/")
def home():
    if 'user_id' not in session:
        return redirect(url_for("login"))
    return redirect(url_for("eventos_index"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        uid = auth.verify_user(email, password)
        if uid:
            session['user_id'] = uid
            session['email'] = email
            flash("✅ Login exitoso", "success")
            return redirect(url_for("home"))
        else:
            flash("❌ Credenciales inválidas", "danger")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        ok = auth.create_user(name, email, password)
        if ok:
            flash("✅ Usuario creado", "success")
            return redirect(url_for("login"))
        else:
            flash("❌ Correo ya registrado", "danger")
    return render_template("register.html")

# CRUD EVENTOS
@app.route("/eventos")
def eventos_index():
    categoria = request.args.get("categoria") or None
    dias = request.args.get("dias")
    dias = int(dias) if dias and dias.isdigit() else None
    estado = request.args.get("estado") or None
    q = request.args.get("q") or None

    items = eventos.get_events_filtered(categoria=categoria, dias=dias, estado=estado, q=q)
    categorias = eventos.get_categories()
    # user_id: colócalo desde tu sesión/login
    return render_template("eventos.html", eventos=items, categorias=categorias, user_id=1)

@app.route('/evento/<int:event_id>')
def evento_detalle(event_id):
    if 'user_id' not in session:
        return redirect(url_for("login"))
    r = requests.get(f'{API_URL}/eventos/{event_id}')
    if r.status_code != 200:
        flash('Evento no encontrado', 'danger')
        return redirect(url_for('eventos_index'))
    evento = r.json()
    # Obtener entradas por usuario para este evento
    r2 = requests.get(f'{API_URL}/eventos/{event_id}/entradas_usuarios')
    entradas_usuarios = r2.json() if r2.status_code == 200 else []
    # Buscar cuántas entradas tiene el usuario actual
    user_id = session['user_id']
    entradas_usuario = 0
    for eu in entradas_usuarios:
        if eu['user_id'] == user_id:
            entradas_usuario = eu['entradas']
            break
    return render_template('evento_detalle.html', evento=evento, user_id=user_id, entradas_usuarios=entradas_usuarios, entradas_usuario=entradas_usuario)

# --- Gestión de entradas ---
@app.post('/evento/<int:event_id>/venta')
def venta_entrada(event_id):
    if 'user_id' not in session:
        return redirect(url_for("login"))
    cantidad = int(request.form.get('cantidad', 1))
    user_id = session['user_id']
    r = requests.post(f'{API_URL}/eventos/{event_id}/venta', json={"user_id": user_id, "cantidad": cantidad})
    if r.status_code == 200:
        flash('Venta registrada', 'success')
    else:
        flash(r.json().get('detail', 'No se pudo registrar la venta'), 'danger')
    return redirect(url_for('evento_detalle', event_id=event_id))

@app.post('/evento/<int:event_id>/devolucion')
def devolucion_entrada(event_id):
    if 'user_id' not in session:
        return redirect(url_for("login"))
    user_id = session['user_id']
    cantidad = int(request.form.get('cantidad', 1))
    r = requests.post(f'{API_URL}/eventos/{event_id}/devolucion', json={"user_id": user_id, "cantidad": cantidad})
    if r.status_code == 200:
        flash('Devolución registrada', 'success')
    else:
        flash(r.json().get('detail', 'No se pudo registrar la devolución'), 'danger')
    return redirect(url_for('evento_detalle', event_id=event_id))

@app.route('/crear', methods=['GET', 'POST'])
def crear_evento():
    if 'user_id' not in session:
        return redirect(url_for("login"))
    if request.method == 'POST':
        data = {
            'name': request.form['name'],
            'description': request.form['description'],
            'fecha': request.form['fecha'],
            'categoria': request.form['categoria'],
            'precio': int(request.form['precio']),
            'cupos': int(request.form['cupos']),
            'user_id': session['user_id']
        }
        r = requests.post(f'{API_URL}/eventos', json=data)
        if r.status_code == 200:
            flash('Evento creado correctamente', 'success')
            return redirect(url_for('eventos_index'))
        else:
            flash(r.json().get('detail', 'Error al crear evento'), 'danger')
    return render_template('crear_evento.html', user_id=session['user_id'])

@app.route('/editar/<int:event_id>', methods=['GET', 'POST'])
def editar_evento(event_id):
    if 'user_id' not in session:
        return redirect(url_for("login"))
    r = requests.get(f'{API_URL}/eventos/{event_id}')
    if r.status_code != 200:
        flash('Evento no encontrado', 'danger')
        return redirect(url_for('eventos_index'))
    evento = r.json()
    if request.method == 'POST':
        data = {
            'name': request.form['name'],
            'description': request.form['description'],
            'fecha': request.form['fecha'],
            'categoria': request.form['categoria'],
            'precio': int(request.form['precio']),
            'cupos': int(request.form['cupos']),
            'user_id': session['user_id']
        }
        r2 = requests.put(f'{API_URL}/eventos/{event_id}', json=data)
        if r2.status_code == 200:
            flash('Evento actualizado', 'success')
            return redirect(url_for('evento_detalle', event_id=event_id))
        else:
            flash(r2.json().get('detail', 'Error al actualizar evento'), 'danger')
    return render_template('editar_evento.html', evento=evento, user_id=session['user_id'])

@app.route('/eliminar/<int:event_id>', methods=['POST'])
def eliminar_evento(event_id):
    if 'user_id' not in session:
        return redirect(url_for("login"))
    user_id = session['user_id']
    r = requests.delete(f'{API_URL}/eventos/{event_id}', params={'user_id': user_id})
    if r.status_code == 200:
        flash('Evento eliminado', 'success')
    else:
        flash(r.json().get('detail', 'No autorizado o error'), 'danger')
    return redirect(url_for('eventos_index'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada', 'info')
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(port=5000, debug=True)
