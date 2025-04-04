
from ...domain.models.application.entities import Application, Diagnosis, EpidemicFocus
from ...utils.get_total_info import get_total_info
from ...utils.date_utils import get_period_dates
from flask import Blueprint, render_template, redirect, request, url_for, flash, abort, send_file
from flask_login import login_required, current_user
from datetime import datetime

from asyncio.log import logger

from ...domain.models.user.entities import Administrator, Doctor
from ...domain.services.application_service import ApplicationService
from ...domain.services.application_api_service import ApplicationApiService
from .forms import ApplicationForm
from ...core.extensions import db

application = Blueprint('application', __name__)


@application.route('/')
def index():
    if current_user.is_authenticated:
        return redirect('/all')
    return render_template('application/index.html')

@application.route('/all', methods=['GET'])
@login_required
def all():
    year = datetime.now().year
    start_date, end_date = get_period_dates('год', year)
    total_info = get_total_info(start_date, end_date)
        
    applications = ApplicationService.get_applications(current_user.id)
        
    return render_template('application/all.html', applications=applications, total_info=total_info)



@application.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if not isinstance(current_user, (Doctor, Administrator)):
        abort(403)
    
    form = ApplicationForm()
    form.diagnosis_id.choices = [(d.id, d.name)
                                     for d in Diagnosis.query.all()]
    form.focus_id.choices = [(f.id, f.name)
                                 for f in EpidemicFocus.query.all()]
    
    if form.validate_on_submit():
        try:
            ApplicationService.create_application(form, current_user.id)
            flash('Заявка успешно создана!', 'success')
            return redirect(url_for('application.all'))
        except Exception as e:
            flash(f'Ошибка при создании заявки: {str(e)}', 'danger')
            logger.error(f'Ошибка при создании заявки: {str(e)}')
    
    return render_template('application/create.html', form=form)


@application.route('/application/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update(id):
    if not isinstance(current_user, (Doctor, Administrator)):
        abort(403)
        
    application = Application.query.get(id)
    
    if isinstance(current_user, Doctor) and application.user_id != current_user.id:
        flash('У вас нет прав для редактирования этой заявки.', 'danger')
        return redirect(url_for('application.all'))
    
    
    
    if not application:
        flash('Заявка не найдена.', 'danger')
        return redirect(url_for('application.all'))
    
    form = ApplicationForm(obj=application)

    form.diagnosis_id.choices = [(d.id, d.name) for d in Diagnosis.query.all()]
    form.focus_id.choices = [(f.id, f.name) for f in EpidemicFocus.query.all()]

    if request.method == 'POST' and form.validate_on_submit():
        try:
            ApplicationService.update_application(id, form, current_user.id)

            db.session.commit()
            flash('Заявка успешно обновлена!', 'success')
            return redirect(url_for('application.all'))

        except Exception as e:
            db.session.rollback()
            flash(
                f'Произошла ошибка при обновлении заявки: {str(e)}', 'danger')
            logger.error(f'Ошибка при обновлении заявки {id}: {str(e)}')

    elif request.method == 'POST':
        flash('Пожалуйста, исправьте ошибки в форме.', 'danger')

    return render_template('application/update.html', application_id=application.id, form=form)


@application.route('/application/<int:id>/delete', methods=['GET', 'POST'])
@login_required
def delete_application(id):
    
    if not (isinstance(current_user, Doctor) or isinstance(current_user, Administrator)):
        abort(403)
    try:
        ApplicationService.delete_application(id, current_user)
        flash('Заявка успешно удалена!', 'success')
        
    except Exception as e:
        flash(f'Произошла ошибка при удалении заявки: {str(e)}', 'danger')
        logger.error(f'Ошибка при удалении заявки {id}: {str(e)}')

    return redirect(url_for('application.all') )


@application.route('/application/<int:id>/download', methods=['GET'])
@login_required
def download_application(id):
    
    doc_stream = ApplicationService.generate_application_doc(id)
    current_date = datetime.now().strftime("%Y-%m-%d")  # Формат даты
    filename = f'{id}_{current_date}.docx'

    return send_file(doc_stream, as_attachment=True, download_name=filename, mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document')

@application.route('/api/diagnoses')
def api_diagnoses():
    return ApplicationApiService.get_diagnoses()

@application.route('/api/gdu')
def api_gdu():
    return ApplicationApiService.get_gdu_list()