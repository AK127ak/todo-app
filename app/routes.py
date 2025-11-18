from flask import render_template, redirect, url_for, flash, request, jsonify, Blueprint
from flask_login import current_user, login_user, logout_user, login_required
from app import db
from app.models import User, Task, Category
from app.forms import LoginForm, RegistrationForm, TaskForm, CategoryForm
from datetime import datetime
from sqlalchemy import or_

main = Blueprint('main', __name__)
auth = Blueprint('auth', __name__)
tasks = Blueprint('tasks', __name__)
categories = Blueprint('categories', __name__)

@main.route('/')
@main.route('/index')
def index():
    if current_user.is_authenticated:
        tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.created_at.desc()).limit(5).all()
        return render_template('index.html', title='Главная', tasks=tasks)
    else:
        return render_template('index.html', title='Главная')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user is None or not user.check_password(form.password.data):
            flash('Неверное имя пользователя или пароль', 'danger')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=form.remember_me.data)
        flash('Вы успешно вошли в систему!', 'success')
        
        next_page = request.args.get('next')
        return redirect(next_page or url_for('main.index'))
    
    return render_template('auth/login.html', title='Вход', form=form)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        default_categories = [
            ('Работа', '#007bff'),
            ('Личное', '#28a745'),
            ('Учеба', '#ffc107')
        ]
        
        for name, color in default_categories:
            category = Category(name=name, color=color, user_id=user.id)
            db.session.add(category)
        
        db.session.commit()
        flash('Регистрация прошла успешно! Теперь вы можете войти.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', title='Регистрация', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы.', 'info')
    return redirect(url_for('main.index'))

@tasks.route('/tasks')
@login_required
def task_list():
    category_id = request.args.get('category_id', type=int)
    status = request.args.get('status', type=str)
    search = request.args.get('search', type=str)
    
    query = Task.query.filter_by(user_id=current_user.id)
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    if status == 'completed':
        query = query.filter_by(completed=True)
    elif status == 'active':
        query = query.filter_by(completed=False)
    
    if search and search.strip():
        search_term = f"%{search.strip()}%"
        query = query.filter(or_(
            Task.title.ilike(search_term),
            Task.description.ilike(search_term)
        ))
    
    tasks = query.order_by(Task.priority.asc(), Task.due_date.asc()).all()
    categories = Category.query.filter_by(user_id=current_user.id).all()
    
    return render_template('tasks/task_list.html', title='Задачи', 
                         tasks=tasks, categories=categories)

@tasks.route('/tasks/create', methods=['GET', 'POST'])
@login_required
def create_task():
    form = TaskForm()
    form.category_id.choices = [(c.id, c.name) for c in Category.query.filter_by(user_id=current_user.id).all()]
    form.category_id.choices.insert(0, (0, 'Без категории'))
    
    if form.validate_on_submit():
        due_date = None
        if form.due_date.data:
            try:
                due_date = datetime.strptime(form.due_date.data, '%Y-%m-%dT%H:%M')
            except ValueError:
                flash('Неверный формат даты', 'danger')
                return render_template('tasks/create_task.html', title='Создать задачу', form=form)
        
        task = Task(
            title=form.title.data.strip(),
            description=form.description.data.strip() if form.description.data else None,
            priority=form.priority.data,
            due_date=due_date,
            user_id=current_user.id,
            category_id=form.category_id.data if form.category_id.data != 0 else None
        )
        db.session.add(task)
        db.session.commit()
        flash('Задача создана!', 'success')
        return redirect(url_for('tasks.task_list'))
    
    return render_template('tasks/create_task.html', title='Создать задачу', form=form)

@tasks.route('/tasks/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    
    if task.user_id != current_user.id:
        flash('Доступ запрещен', 'danger')
        return redirect(url_for('tasks.task_list'))
    
    form = TaskForm(obj=task)
    form.category_id.choices = [(c.id, c.name) for c in Category.query.filter_by(user_id=current_user.id).all()]
    form.category_id.choices.insert(0, (0, 'Без категории'))
    
    if form.validate_on_submit():
        due_date = None
        if form.due_date.data:
            try:
                due_date = datetime.strptime(form.due_date.data, '%Y-%m-%dT%H:%M')
            except ValueError:
                flash('Неверный формат даты', 'danger')
                return render_template('tasks/edit_task.html', title='Редактировать задачу', form=form, task=task)
        
        task.title = form.title.data.strip()
        task.description = form.description.data.strip() if form.description.data else None
        task.priority = form.priority.data
        task.due_date = due_date
        task.category_id = form.category_id.data if form.category_id.data != 0 else None
        task.updated_at = datetime.utcnow()
        
        db.session.commit()
        flash('Задача обновлена!', 'success')
        return redirect(url_for('tasks.task_list'))
    
    if task.due_date:
        form.due_date.data = task.due_date.strftime('%Y-%m-%dT%H:%M')
    
    return render_template('tasks/edit_task.html', title='Редактировать задачу', form=form, task=task)

@tasks.route('/tasks/<int:task_id>/toggle', methods=['POST'])
@login_required
def toggle_task(task_id):
    task = Task.query.get_or_404(task_id)
    
    if task.user_id != current_user.id:
        return jsonify({'error': 'Доступ запрещен'}), 403
    
    task.completed = not task.completed
    task.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'completed': task.completed})

@tasks.route('/tasks/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    
    if task.user_id != current_user.id:
        flash('Доступ запрещен', 'danger')
        return redirect(url_for('tasks.task_list'))
    
    db.session.delete(task)
    db.session.commit()
    flash('Задача удалена!', 'success')
    return redirect(url_for('tasks.task_list'))

@categories.route('/categories')
@login_required
def category_list():
    categories = Category.query.filter_by(user_id=current_user.id).all()
    return render_template('categories/category_list.html', title='Категории', categories=categories)

@categories.route('/categories/create', methods=['GET', 'POST'])
@login_required
def create_category():
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(
            name=form.name.data.strip(),
            color=form.color.data,
            user_id=current_user.id
        )
        db.session.add(category)
        db.session.commit()
        flash('Категория создана!', 'success')
        return redirect(url_for('categories.category_list'))
    
    return render_template('categories/create_category.html', title='Создать категорию', form=form)

@categories.route('/categories/<int:category_id>/delete', methods=['POST'])
@login_required
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    
    if category.user_id != current_user.id:
        flash('Доступ запрещен', 'danger')
        return redirect(url_for('categories.category_list'))
    
    Task.query.filter_by(category_id=category_id, user_id=current_user.id).update({Task.category_id: None})
    db.session.delete(category)
    db.session.commit()
    
    flash('Категория удалена!', 'success')
    return redirect(url_for('categories.category_list'))