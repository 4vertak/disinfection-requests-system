
from asyncio.log import logger
from flask import Blueprint, abort, render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
import json
from datetime import datetime
from ..forms import RegistrationForm, LoginForm, LoginUpdateForm
from ..models.user import Doctor, Disinfector, Administrator, Area, load_user
from ..models.application import Application, Disinfection, UserAuditLog, json_serializer
from ..extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

user = Blueprint('user', __name__)


@user.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    if not isinstance(current_user, Administrator):
        abort(403)
    
    form = RegistrationForm()
    form.area_id.choices = [(area.id, area.name_area)
                            for area in Area.query.all()]

    if form.validate_on_submit():
        try:
            if form.user_type.data == 'doctor':
                if Doctor.query.filter_by(login=form.login.data).first():
                    flash(
                        'Пользователь с таким логином уже существует. Пожалуйста, выберите другой логин.', 'danger')
                    return render_template('user/register.html', form=form)

                user = Doctor(
                    name=form.name.data,
                    login=form.login.data,
                    password_hash=generate_password_hash(form.password.data),
                    area_id=form.area_id.data,
                    user_type=form.user_type.data
                )
                db.session.add(user)
                db.session.commit()

            elif form.user_type.data == 'disinfector':
                if Disinfector.query.filter_by(login=form.login.data).first():
                    flash(
                        'Пользователь с таким логином уже существует. Пожалуйста, выберите другой логин.', 'danger')
                    return render_template('user/register.html', form=form)

                user = Disinfector(
                    name=form.name.data,
                    login=form.login.data,
                    password_hash=generate_password_hash(
                        form.password.data), 
                    user_type=form.user_type.data
                )
                db.session.add(user)
                db.session.commit()

            elif form.user_type.data == 'admin':
                if Administrator.query.filter_by(login=form.login.data).first():
                    flash(
                        'Пользователь с таким логином уже существует. Пожалуйста, выберите другой логин.', 'danger')
                    return render_template('user/register.html', form=form)

                user = Administrator(
                    name=form.name.data,
                    login=form.login.data,
                    password_hash=generate_password_hash(
                        form.password.data),  # Хешируем пароль
                    user_type=form.user_type.data
                )
                db.session.add(user)
                db.session.commit()

            flash('Регистрация прошла успешно! Вы можете теперь войти.', 'success')
            return redirect('/admin/users')

        except Exception as e:
            db.session.rollback()
            flash(
                'Произошла ошибка при регистрации. Пожалуйста, попробуйте снова.', 'danger')
            print(f"Ошибка: {e}")
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(
                    f'Ошибка в поле "{getattr(form, field).label.text}": {error}', 'danger')
    return render_template('user/register.html', form=form)


@user.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/')

    form = LoginForm()
    if form.validate_on_submit():
        login = form.login.data
        user = None
        flag_is_admin = None

        # Проверяем все таблицы
        user = Administrator.query.filter_by(login=login).first()
        if user: flag_is_admin = 1
        if not user:
            user = Disinfector.query.filter_by(login=login).first()
        if not user:
            user = Doctor.query.filter_by(login=login).first()

        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash('Вы вошли в систему!', 'success')
            if flag_is_admin: 
                return redirect('/admin')
            return redirect('/all')
        else:
            flash('Неправильное имя пользователя или пароль', 'danger')
            

    return render_template('user/login.html', form=form)


@user.route('/user/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update(id):
    user = load_user(id)
    if not (current_user.id == user.id or isinstance(current_user, Administrator)):
        flash('У вас нет прав для редактирования этого профиля.', 'danger')
        return redirect('/all')
    
    
    
    if not user:
        flash('Пользователь не найден.', 'danger')
        return redirect('/all')

    form = LoginUpdateForm(obj=user)
    form.area_id.choices = [(area.id, area.name_area) for area in Area.query.all()]
    
    if isinstance(current_user, Administrator):
        form.current_password.render_kw = {'style': 'display: none;'}
        form.current_password.label.text = ''
    
    if request.method == 'POST' and form.validate_on_submit():
        try:
            user.name = form.name.data
            user.login = form.login.data
            user.user_type = form.user_type.data
            
            if form.user_type.data == 'doctor':
                user.area_id = form.area_id.data
            else:
                user.area_id = None
            
            if form.change_password.data:
                if not isinstance(current_user, Administrator):
                    if not check_password_hash(user.password_hash, form.current_password.data):
                        flash('Текущий пароль введен неверно', 'danger')
                        return render_template('user/update.html', form=form, user=user)
                
                user.password_hash = generate_password_hash(form.new_password.data)
                log = UserAuditLog(
                    user_id=current_user.id,
                    action='change_password',
                    details=json.loads(json.dumps(
                        {'changed_at': datetime.now()},
                        default=json_serializer
                    ))
                )
                db.session.add(log)
            
            db.session.commit()
            flash('Профиль успешно обновлен!', 'success')
            if current_user.user_type == 'admin':
                return redirect('/admin/users')
            else:
                return redirect('/all')

        except Exception as e:
            db.session.rollback()
            flash(f'Произошла ошибка при обновлении профиля: {str(e)}', 'danger')
            logger.error(f'Ошибка при обновлении профиля {id}: {str(e)}')

    return render_template('user/update.html', form=form, user=user, is_admin=isinstance(current_user, Administrator))

@user.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы!', 'success')
    return redirect('/')

@user.route('/user/<int:id>/delete', methods=['GET', 'POST'])
@login_required
def delete_user(id):
    if not isinstance(current_user, Administrator):
        abort(403)
        
    if current_user.id == id:
        flash('Невозможно удалить самого себя.', 'danger')
        return redirect('/admin/users')
    
    user = load_user(id)
    if not user:
        flash('Пользователь не найден.', 'danger')
        return redirect('/admin/users')

    try:
        with db.session.begin_nested():
            transferred_apps = 0
            transferred_disinfections = 0
            new_owner_id = None

            if user.user_type == 'doctor':
                alternate_doctor = Doctor.query.filter_by(area_id=user.area_id).filter(Doctor.id != user.id).first()
                if not alternate_doctor:
                    alternate_doctor = Doctor.query.filter(Doctor.id != user.id).first()
                
                if alternate_doctor:
                    new_owner_id = alternate_doctor.id
                    transferred_apps = Application.query.filter_by(user_id=id).update(
                        {'user_id': alternate_doctor.id},
                        synchronize_session=False
                    )

            elif user.user_type == 'disinfector':
                alternate_disinfector = Disinfector.query.filter(Disinfector.id != id).first()
                
                if alternate_disinfector:
                    new_owner_id = alternate_disinfector.id
                    transferred_disinfections = Disinfection.query.filter_by(user_id=id).update(
                        {'user_id': alternate_disinfector.id},
                        synchronize_session=False
                    )

            log_details = {
                'deleted_user_id': id,
                'deleted_user_name': user.name,
                'transferred_applications': transferred_apps,
                'transferred_disinfections': transferred_disinfections,
                'new_owner_id': new_owner_id
            }
            
            log = UserAuditLog(
                user_id=current_user.id,
                action='delete_user',
                details=log_details
            )
            db.session.add(log)
            db.session.delete(user)
            
        db.session.commit()

        if new_owner_id is None and (transferred_apps > 0 or transferred_disinfections > 0):
            flash('Пользователь удален, но не найден подходящий пользователь для переноса данных!', 'warning')
        else:
            flash('Пользователь успешно удален! Все связанные данные перенесены.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Произошла ошибка при удалении пользователя: {str(e)}', 'danger')
        logger.error(f'Ошибка при удалении пользователя {id}: {str(e)}', exc_info=True)

    return redirect('/admin/users')


@user.route('/admin/users', methods=['POST', 'GET'])
@login_required
def users():

    if not isinstance(current_user, Administrator):
        abort(403)
        
    count_admins = Administrator.query.count()
    count_doctors = Doctor.query.count()
    count_disinfectors = Disinfector.query.count()
    total_users = count_doctors + count_disinfectors + count_admins
    total_info = {
        'total_users': total_users,
        'count_admins': count_admins,
        'count_doctors': count_doctors,
        'count_disinfectors': count_disinfectors
    }
    
    admins = Administrator.query.all()
    doctors = Doctor.query.all()
    disinfectors = Disinfector.query.all()
    
    all_users = []

    for admin in admins:
        all_users.append({
            'id': admin.id,
            'name': admin.name,
            'login': admin.login,
            'user_type': admin.user_type
        })

    for doctor in doctors:
        all_users.append({
            'id': doctor.id,
            'name': doctor.name,
            'login': doctor.login,
            'user_type': doctor.user_type
        })

    for disinfector in disinfectors:
        all_users.append({
            'id': disinfector.id,
            'name': disinfector.name,
            'login': disinfector.login,
            'user_type': disinfector.user_type
        })
    
    
    return render_template(
        'application/users.html',
        total_info = total_info,
        users=all_users
    )


