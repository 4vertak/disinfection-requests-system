from flask import Blueprint, abort, render_template, redirect, url_for, flash

from ...domain.models.user.entities import User
from .forms import DisinfectionForm
from ...domain.models.application.entities import Application, Disinfection
from ...core.extensions import db
from flask_login import current_user, login_required


disinfection = Blueprint('disinfection', __name__)


@disinfection.route('/<int:id>/add/disinfection/data/', methods=['GET', 'POST'])
@login_required
def add_data(id):
    application = Application.query.get(id)

    if application is None:
        flash('Заявка не найдена.', 'error')
        return redirect(url_for('application.all'))

    disinfection = db.session.query(Disinfection).filter(
        Disinfection.application_id == id
    ).one_or_none()

    form = None   # <-- добавил сюда

    if current_user.user_type == "doctor":
        if disinfection is None:
            disinfection = Disinfection(application_id=id)
            db.session.add(disinfection)

        disinfection.rejection_reason = None
        form = DisinfectionForm(obj=disinfection)   # теперь точно будет
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
                return redirect(url_for('application.all'))
            except Exception:
                db.session.rollback()
                flash('Произошла ошибка при добавлении записи. Попробуйте ещё раз.', 'error')
    else:
        abort(403)

    return render_template('application/add_data.html', application=application, form=form)

