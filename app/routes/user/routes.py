
from asyncio.log import logger

from ...domain.models.application.entities import Application, Disinfection, Area
from ...domain.models.audit.entities import UserAuditLog
from ...utils.serializers import json_serializer

from ...domain.models.user.entities import User
from ...domain.services.user_service import UserService
from flask import Blueprint, abort, render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
import json
from datetime import datetime
from .forms import RegistrationForm, LoginForm, LoginUpdateForm
from werkzeug.security import generate_password_hash, check_password_hash
from ...core.extensions import db

user = Blueprint('user', __name__)


@user.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/')

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash('Вы вошли в систему!', 'success')
            if user.role == "Admin":
                return redirect('/admin')
            return redirect('/all')
        else:
            flash('Неправильное имя пользователя или пароль', 'danger')

    return render_template('user/login.html', form=form)


@user.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    if current_user.role != "Admin":
        abort(403)

    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            user_data = {
                'username': form.username.data,
                'password': form.password.data,
                'role': form.role.data,
            }
            UserService.create_user(user_data)
            flash('Регистрация прошла успешно!', 'success')
            return redirect('/admin/users')

        except Exception as e:
            flash('Ошибка при регистрации. Попробуйте снова.', 'danger')
            logger.error(f'Ошибка при регистрации: {str(e)}')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'Ошибка в поле "{getattr(form, field).label.text}": {error}', 'danger')

    return render_template('user/register.html', form=form)


@user.route('/user/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update(id):
    user = User.query.get(id)
    if not user:
        flash('Пользователь не найден.', 'danger')
        return redirect(url_for('application.all'))

    if not (current_user.id == user.id or current_user.role == "Admin"):
        flash('У вас нет прав для редактирования этого профиля.', 'danger')
        return redirect(url_for('application.all'))

    form = LoginUpdateForm(obj=user)

    if request.method == 'POST' and form.validate_on_submit():
        try:
            update_data = {
                'username': form.username.data,
                'role': form.role.data
            }

            if form.change_password.data:
                if current_user.role != "Admin":
                    if not check_password_hash(user.password_hash, form.current_password.data):
                        flash('Текущий пароль введен неверно', 'danger')
                        return render_template('user/update.html', form=form, user=user)

                update_data['password_hash'] = generate_password_hash(form.new_password.data)

                log = UserAuditLog(
                    user_id=current_user.id,
                    action='change_password',
                    details=json.loads(json.dumps({'changed_at': datetime.now()}, default=json_serializer))
                )
                db.session.add(log)

            UserService.update_user(user.id, update_data)
            flash('Профиль успешно обновлен!', 'success')
            if current_user.role == 'Admin':
                return redirect('/admin/users')
            else:
                return redirect(url_for('application.all'))

        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при обновлении профиля: {str(e)}', 'danger')
            logger.error(f'Ошибка при обновлении профиля {id}: {str(e)}')

    return render_template('user/update.html', form=form, user=user, is_admin=(current_user.role == "Admin"))


@user.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы!', 'success')
    return redirect('/')


@user.route('/user/<int:id>/delete', methods=['GET', 'POST'])
@login_required
def delete_user(id):
    if current_user.role != "Admin":
        abort(403)

    user = User.query.get(id)
    if not user:
        flash('Пользователь не найден.', 'danger')
        return redirect('/admin/users')

    if current_user.id == id:
        flash('Нельзя удалить свой аккаунт.', 'danger')
        return redirect('/admin/users')

    try:
        with db.session.begin_nested():
            transferred_apps = 0
            transferred_disinfections = 0
            new_owner_id = None

            if user.role == 'Doctor':
                alternate = User.query.filter(User.role == "Doctor", User.id != user.id).first()
                if alternate:
                    new_owner_id = alternate.id
                    transferred_apps = Application.query.filter_by(user_id=id).update(
                        {'user_id': alternate.id}, synchronize_session=False
                    )
            elif user.role == 'Disinfector':
                alternate = User.query.filter(User.role == "Disinfector", User.id != user.id).first()
                if alternate:
                    new_owner_id = alternate.id
                    transferred_disinfections = Disinfection.query.filter_by(user_id=id).update(
                        {'user_id': alternate.id}, synchronize_session=False
                    )

            log = UserAuditLog(
                user_id=current_user.id,
                action='delete_user',
                details={
                    'deleted_user_id': id,
                    'deleted_username': user.username,
                    'transferred_applications': transferred_apps,
                    'transferred_disinfections': transferred_disinfections,
                    'new_owner_id': new_owner_id
                }
            )
            db.session.add(log)
            db.session.delete(user)

        db.session.commit()
        flash('Пользователь успешно удален!', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при удалении пользователя: {str(e)}', 'danger')
        logger.error(f'Ошибка при удалении пользователя {id}: {str(e)}', exc_info=True)

    return redirect('/admin/users')


@user.route('/admin/users', methods=['POST', 'GET'])
@login_required
def users():
    if current_user.role != "Admin":
        abort(403)

    users = User.query.all()
    total_info = {
        'total_users': len(users),
        'count_admins': sum(1 for u in users if u.role == "Admin"),
        'count_doctors': sum(1 for u in users if u.role == "Doctor"),
        'count_disinfectors': sum(1 for u in users if u.role == "Disinfector"),
    }

    all_users = [
        {'id': u.id, 'username': u.username, 'role': u.role}
        for u in users
    ]

    return render_template('application/users.html', total_info=total_info, users=all_users)