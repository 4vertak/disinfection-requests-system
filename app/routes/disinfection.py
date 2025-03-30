from flask import Blueprint, abort, render_template, redirect, url_for, flash

from ..models.user import Disinfector
from ..forms import DisinfectionForm
from ..models.application import Application, Disinfection
from ..extensions import db
from flask_login import current_user, login_required

disinfection = Blueprint('disinfection', __name__)


@disinfection.route('/<int:id>/add/disinfection/data/', methods=['GET', 'POST'])
@login_required
def add_data(id):
    application = Application.query.get(id)

    if application is None:
        flash('Заявка не найдена.', 'error')
        return redirect('/all')

    disinfection = db.session.query(Disinfection).filter(
        Disinfection.application_id == id).one_or_none()

    if isinstance(current_user, Disinfector):
        disinfection.rejection_reason = None
        form = DisinfectionForm(obj=disinfection)
        form.disinfection_date.data = application.submission_date
        
        if form.validate_on_submit():
            disinfection.disinfection_date = form.disinfection_date.data
            disinfection.area_size = form.area_size.data
            disinfection.volume_size = form.volume_size.data
            disinfection.spraying_time = form.spraying_time.data
            disinfection.user_id = current_user.id

            if form.rejection_reason.data and form.rejection_reason.data != 'completed':
                disinfection.rejection_reason = form.rejection_reason.data
                application.status = 'refusal'
            else:
                disinfection.rejection_reason = 'completed'
                application.status = 'completed'

            try:
                db.session.commit()
                flash('Данные о дезинфекции успешно добавлены!', 'success')
                return redirect('/all')
            except Exception as e:
                db.session.rollback()
                flash(
                    'Произошла ошибка при добавлении записи. Пожалуйста, попробуйте еще раз.', 'error')
    else:
        abort(403)

    return render_template('application/add_data.html', application=application, form=form)
