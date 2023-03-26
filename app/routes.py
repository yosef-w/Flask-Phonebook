from app import app, db
from flask import render_template, redirect, url_for, flash
from app.forms import PhoneForm, SignUpForm, LoginForm
from app.models import Directory, User
from flask_login import login_user, logout_user, login_required, current_user

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        print('User confirmation form complete.')
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        username = form.username.data
        password = form.password.data
        print(first_name, last_name, email, username, password)

        check_user = db.session.execute(db.select(User).filter((User.username == username) | (User.email == email))).scalars().all()
        if check_user:
            flash("A user with that username and/or email already exists", "warning")
            return redirect(url_for('signup'))
        
        new_user = User(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
        flash(f"Thank you {new_user.username} for signing up!", "success")
    return render_template('index.html', form=form)


@app.route('/add_contact', methods=["GET", "POST"])
def add_contact():
    form = PhoneForm()
    if form.validate_on_submit():
        first = form.first_name.data
        last = form.last_name.data
        address = form.address.data
        phone = form.phone_number.data
        print(first, last, address, phone)
        new_contact = Directory(first_name=first, last_name=last, address=address, phone_number=phone)
        flash(f"{new_contact.first_name} {new_contact.last_name} has been added your phonebook", "success")
        return redirect(url_for('index'))
    return render_template('add_contact.html', form=form)

@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        print('Form Validated :)')
        username = form.username.data
        password = form.password.data
        print(username, password)

        user = User.query.filter_by(username=username).first()
        if user is not None and user.check_password(password):

            login_user(user)
            flash(f'You have successfully logged in as {username}', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username and/or password. Please try again', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash("You have logged out", "info")
    return redirect(url_for('index'))

@app.route('/directory')
def show_directory():
    contacts = Directory.query.all()
    return render_template('directory.html', contacts=contacts)

@app.route('/edit/<directory_id>', methods=["GET", "POST"])
@login_required
def edit_contact(directory_id):
    form = PhoneForm()
    contact_to_edit = Directory.query.get_or_404(directory_id)
    if contact_to_edit.author != current_user:
        flash("You do not have permission to edit this contact", "danger")
        return redirect(url_for('index'))

    if form.validate_on_submit():
        contact_to_edit.first_name = form.first_name.data
        contact_to_edit.last_name = form.last_name.data
        contact_to_edit.phone_number = form.phone_number.data
        contact_to_edit.address = form.address.data

        db.session.commit()
        flash(f"{contact_to_edit.first_name} {contact_to_edit.last_name} has been edited!", "success")
        return redirect(url_for('index'))

    form.first_name.data = contact_to_edit.first_name
    form.last_name.data = contact_to_edit.last_name
    form.phone_number.data = contact_to_edit.phone_number
    form.address.data = contact_to_edit.address
    return render_template('edit.html', form=form, contact=contact_to_edit)

@app.route('/delete/<directory_id>')
@login_required
def delete_post(directory_id):
    contact = Directory.query.get_or_404(directory_id)
    if contact.user_id != current_user.id:
        flash("You do not have permission to delete this contact", "danger")
        return redirect(url_for('directory'))

    db.session.delete(contact)
    db.session.commit()
    flash(f"{contact.first_name} {contact.last_name} has been deleted", "info")
    return redirect(url_for('directory'))