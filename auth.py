import secrets
from functools import wraps

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash

import db
from repositories import UserRepository

auth_bp = Blueprint("auth", __name__)
user_repository = UserRepository()

# used to keep login response time the same whether or not the email exists
DUMMY_PASSWORD_HASH = generate_password_hash(secrets.token_hex(16))


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)
    return wrapped


@auth_bp.route("/")
def index():
    if session.get("user_id"):
        return redirect(url_for("upload.upload"))
    return redirect(url_for("auth.login"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        user = user_repository.get_user_by_email(email)
        password_hash = user["password_hash"] if user else DUMMY_PASSWORD_HASH
        password_ok = check_password_hash(password_hash, password)
        if user and password_ok:
            session["user_id"] = user["id"]
            session["email"] = user["email"]
            db.log_event(user["id"], "login")
            flash("Login successful.", "success")
            return redirect(url_for("upload.upload"))
        error = "Invalid email or password."
    return render_template("login.html", error=error)


@auth_bp.route("/logout")
def logout():
    user_id = session.get("user_id")
    if user_id:
        db.log_event(user_id, "logout")
    session.clear()
    return redirect(url_for("auth.login"))
