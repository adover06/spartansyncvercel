from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, login_required
from . import bp
from app.forms import LoginForm
from app.forms import CreateAccountForm
from app import db
from app.models import User



@bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(User.username == form.username.data).first()
        

        if user and user.check_password(form.password.data):  
            login_user(user)
            return redirect("/home")  # Simple redirect, or use url_for('main.home')
        else:
            form.password.errors.append("Invalid username or password.")
    
    return render_template("login.html", form=form)

@bp.route("/createaccount", methods=["GET", "POST"])
def create_account():
    form = CreateAccountForm()
    if form.validate_on_submit():
        existing_user = User.query.filter(
            (User.email == form.email.data) | (User.username == form.username.data)
        ).first()
        if existing_user:
            flash("Username or email already exists. Please choose another.", "error")
            return render_template("createaccount.html", form=form)

        new_user = User(
            username=form.username.data,
            email=form.email.data,
            role=form.role.data,
        )
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()

        flash("Account created successfully! Please log in.", "success")
        return redirect("/login")

    return render_template("createaccount.html", form=form)


@bp.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    if request.method == "POST":
        logout_user()
        flash("Signed out successfully.", "success")
        return redirect(url_for("auth.login"))
    return render_template("logout.html")