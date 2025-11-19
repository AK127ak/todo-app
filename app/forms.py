from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Optional
from app.models import User
import re

class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Зарегистрироваться')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Это имя пользователя уже занято.')

    def validate_email(self, email):
        # Простая проверка формата email
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email.data):
            raise ValidationError('Неверный формат email.')
        
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Этот email уже используется.')

class TaskForm(FlaskForm):
    title = StringField('Название задачи', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Описание')
    category_id = SelectField('Категория', coerce=int)
    priority = SelectField('Приоритет', choices=[(1, 'Высокий'), (2, 'Средний'), (3, 'Низкий')], coerce=int, default=2)
    due_date = StringField('Срок выполнения')
    submit = SubmitField('Создать задачу')

class CategoryForm(FlaskForm):
    name = StringField('Название категории', validators=[DataRequired(), Length(max=100)])
    color = StringField('Цвет', validators=[Length(max=7)], default='#007bff')
    submit = SubmitField('Создать категорию')