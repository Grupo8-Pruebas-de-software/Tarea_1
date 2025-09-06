from flask import Flask, render_template, request, redirect, url_for, flash
import sys, os
sys.path.append(os.path.abspath("../Backend"))  # Para importar auth.py
import auth

app = Flask(__name__)
app.secret_key = "supersecret"  # Necesario para flash mensajes

@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        uid = auth.verify_user(email, password)
        if uid:
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

if __name__ == "__main__":
    app.run(port=5000, debug=True)
