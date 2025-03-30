from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import BooleanField, SelectField, StringField, PasswordField, SubmitField, DateField, FloatField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo, Optional


class RegistrationForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired(
        message='Имя обязательно'), Length(min=1, max=100)])
    login = StringField('Логин', validators=[DataRequired(message='Логин обязателен'), Length(
        min=2, max=20, message='Логин  должен содержать минимум 2 символа')])
    password = PasswordField('Пароль', validators=[DataRequired(message='Пароль обязателен'), Length(
        min=8, message='Пароль должен содержать минимум 8 символов.')])
    confirm_password = PasswordField('Подтвердите пароль', validators=[DataRequired(
        message='Подтверждение пароля обязательно'), EqualTo('password', message='Пароли не совпадают')])
    user_type = SelectField('Тип пользователя', choices=[(
        'doctor', 'Врач'), ('disinfector', 'Дезинфектор'), ('admin', 'Администратор')], default='disinfector')
    area_id = SelectField('Участок', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')

class LoginUpdateForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired(message='Имя обязательно'), 
                                         Length(min=1, max=100)])
    login = StringField('Логин', validators=[DataRequired(message='Логин обязателен'), 
                                           Length(min=2, max=20)])
    
    
    change_password = BooleanField('Изменить пароль')
    current_password = PasswordField('Текущий пароль', validators=[Optional()])
    
    new_password = PasswordField('Новый пароль', validators=[
        Optional(),
        Length(min=8, message='Пароль должен содержать минимум 8 символов.')
    ])
    confirm_new_password = PasswordField('Подтвердите новый пароль', validators=[
        Optional(),
        EqualTo('new_password', message='Пароли не совпадают')
    ])
    
    user_type = SelectField('Тип пользователя', choices=[
        ('doctor', 'Врач'), 
        ('disinfector', 'Дезинфектор'), 
        ('admin', 'Администратор')
    ], default='disinfector')
    
    area_id = SelectField('Участок', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Обновить')


class LoginForm(FlaskForm):
    login = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


class ApplicationForm(FlaskForm):
    patient_full_name = StringField(
        'Ф.И.О. пациента', validators=[DataRequired()])
    birth_date = DateField(
        'Дата рождения', format='%Y-%m-%d', validators=[DataRequired()])
    address = StringField('Адрес', validators=[DataRequired()])
    contact_phone = StringField(
        'Контактный телефон', validators=[Optional()])
    relative_contact_phone = StringField(
        'Контактный телефон родственника', validators=[Optional()])
    workplace = StringField('Место работы', validators=[Optional()])
    position = StringField('Должность', default='не работает', validators=[Optional()])
    diagnosis_id = SelectField(
        'Диагноз', validators=[Optional()])
    focus_id = SelectField('Очаг', coerce=int, validators=[DataRequired()])
    reason_application = SelectField('Причина дезинфекции', choices=[(
        'hospitalization', 'Госпитализация'), ('posthumously', 'Посмертно')], default='hospitalization', validators=[Optional()])
    hospitalization_date = DateField(
        'Дата госпитализации', format='%Y-%m-%d', validators=[Optional()])
    gdu = SelectField('Группа диспансерного наблюдения', choices=[(
        '0', '0'), ('I-А-МБТ+', 'I-А-МБТ+'), ('I-А-МБТ-', 'I-А-МБТ-'), ('I-В', 'I-В'), ('II-А', 'II-Б'), ('III', 'III'), ('III-А', 'III'),('IV-А', 'IV-А'), ('IV-Б', 'IV-Б'), ('V', 'V') , ('VI', 'VI')], validators=[DataRequired()])
    registration_date = DateField(
        'Дата взятия на учет', format='%Y-%m-%d', validators=[DataRequired()])
    place_of_hospitalization = StringField(
        'Место госпитализации', validators=[Optional()])


class DisinfectionForm(FlaskForm):
    area_size = FloatField('Площадь помещения (кв.м.)',
                           validators=[Optional()], default=0)
    rejection_reason = TextAreaField('Причина отказа', validators=[
                                     Optional()], default='completed')
    disinfection_date = DateField(
        'Дата проведения дезинфекции', format='%Y-%m-%d', validators=[DataRequired()], default=datetime.now())

    volume_size = FloatField('Объем помещения (куб.м.)',
                             validators=[Optional()])
    spraying_time = TextAreaField('Время раcпыления', validators=[
                                  Optional()])
    submit = SubmitField('Добавить')
