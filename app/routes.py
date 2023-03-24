from app import app, db
from flask import render_template, redirect, url_for, flash
from app.forms import PhoneForm, SignUpForm
from app.models import Directory
from flask_login import login_user, logout_user, login_required, current_user

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        print('User confirmation form complete.')
        first = form.first_name.data
        last = form.last_name.data
        phone = form.phone.data
        address = form.address.data
        print(first, last, phone, address)
        new_contact = Directory(first_name = first, last_name = last, phone = phone, address = address)
        flash(f"Thank you {first} for signing up!", "success")
        return redirect(url_for('index'))
    return render_template('signup.html', form=form)


@app.route('/add-phone', methods=["GET", "POST"])
def add_phone():
    form = PhoneForm()
    if form.validate_on_submit():
        first = form.first_name.data
        last = form.last_name.data
        address = form.address.data
        phone = form.phone_number.data
        print(first, last, address, phone)
        new_contact = Directory(first_name=first, last_name=last, address=address, phone_number=phone)
        flash(f"{new_contact.first_name} {new_contact.last_name} has been added to the phone book", "success")
        return redirect(url_for('index'))
    return render_template('add_phone.html', form=form)

@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        print('Form Validated :)')
        username = form.username.data
        password = form.password.data
        print(username, password)
        # Check if there is a user with username and that password
        user = User.query.filter_by(username=username).first()
        if user is not None and user.check_password(password):
            # If the user exists and has the correct password, log them in
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

@app.route('/create', methods=["GET", "POST"])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        # Get the data from the form
        title = form.title.data
        body = form.body.data
        image_url = form.image_url.data or None
        # Create an instance of Post with form data AND auth user ID
        new_post = Post(title=title, body=body, image_url=image_url, user_id=current_user.id)
        flash(f"{new_post.title} has been created!", "success")
        return redirect(url_for('index'))
    return render_template('create.html', form=form)

@app.route('/edit/<post_id>', methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    form = PostForm()
    post_to_edit = Post.query.get_or_404(post_id)
    # Make sure that the post author is the current user
    if post_to_edit.author != current_user:
        flash("You do not have permission to edit this post", "danger")
        return redirect(url_for('index'))

    # If form submitted, update Post
    if form.validate_on_submit():
        # update the post with the form data
        post_to_edit.title = form.title.data
        post_to_edit.body = form.body.data
        post_to_edit.image_url = form.image_url.data
        # Commit that to the database
        db.session.commit()
        flash(f"{post_to_edit.title} has been edited!", "success")
        return redirect(url_for('index'))

    # Pre-populate the form with Post To Edit's values
    form.title.data = post_to_edit.title
    form.body.data = post_to_edit.body
    form.image_url.data = post_to_edit.image_url
    return render_template('edit.html', form=form, post=post_to_edit)

@app.route('/delete/<post_id>')
@login_required
def delete_post(post_id):
    post_to_delete = Post.query.get_or_404(post_id)
    if post_to_delete.author != current_user:
        flash("You do not have permission to delete this post", "danger")
        return redirect(url_for('index'))

    db.session.delete(post_to_delete)
    db.session.commit()
    flash(f"{post_to_delete.title} has been deleted", "info")
    return redirect(url_for('index'))