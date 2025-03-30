
from asyncio.log import logger
import random
from flask import Blueprint, abort, jsonify, render_template, redirect, url_for, flash, request, send_file

from ..models.user import Doctor, Administrator, Area
from ..forms import ApplicationForm
from ..models.application import Application, Diagnosis, EpidemicFocus, Disinfection, ApplicationAuditLog
from ..extensions import db
from ..functions import get_period_dates, get_total_info

from flask_login import login_required, current_user
from io import BytesIO
from docxtpl import DocxTemplate

from werkzeug.security import generate_password_hash

from datetime import datetime, timedelta

application = Blueprint('application', __name__)


@application.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('application.all'))
    else:
        return render_template('application/index.html')


@application.route('/all', methods=['GET'])
@login_required
def all():
    year = datetime.now().year
    start_date, end_date = get_period_dates('год', year)
    total_info = get_total_info(start_date, end_date)

    query = (db.session.query(Application, Disinfection, Area, Doctor).join(Disinfection, Disinfection.application_id == Application.id).join(Doctor, Doctor.id == Application.user_id).join(Area, Area.id == Doctor.area_id))
    if isinstance(current_user, Doctor):
        applications = query.filter(Application.user_id == current_user.id).order_by(Application.submission_date.asc()).all()
    else:
        applications = query.order_by(Application.submission_date.asc()).all()

    return render_template(
        'application/all.html',
        applications=applications,
        total_info=total_info)


@application.route('/application/create', methods=['GET', 'POST'])
@login_required
def create():
    if isinstance(current_user, Doctor) or isinstance(current_user, Administrator):
        form = ApplicationForm()

        form.diagnosis_id.choices = [(d.id, d.name)
                                     for d in Diagnosis.query.all()]
        form.focus_id.choices = [(f.id, f.name)
                                 for f in EpidemicFocus.query.all()]

        if form.validate_on_submit():
            try:
                application = Application(
                    submission_date=datetime.now(),
                    patient_full_name=form.patient_full_name.data,
                    birth_date=form.birth_date.data,
                    address=form.address.data,
                    contact_phone=form.contact_phone.data,
                    relative_contact_phone=form.relative_contact_phone.data,
                    workplace=form.workplace.data,
                    position=form.position.data,
                    diagnosis_id=form.diagnosis_id.data,
                    gdu=form.gdu.data,
                    registration_date=form.registration_date.data,
                    focus_id=form.focus_id.data,
                    user_id=current_user.id,
                    reason_application=form.reason_application.data,
                    status='incompleted'
                )

                if form.reason_application.data == 'hospitalization':
                    application.hospitalization_date = form.hospitalization_date.data
                    application.place_of_hospitalization = form.place_of_hospitalization.data

                db.session.add(application)
                db.session.commit()
                flash('Заявка успешно создана!', 'success')
                return redirect('/all')
            except Exception as e:
                db.session.rollback()
                flash(f'Ошибка при создании заявки: {str(e)}', 'danger')
                logger.error('Ошибка при создании заявки: %s', str(e))

        return render_template('application/create.html', form=form)

    abort(403)


@application.route('/application/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update(id):
    application = Application.query.get(id)
    if not application:
        flash('Заявка не найдена.', 'danger')
        return redirect('/all')

    if not (isinstance(current_user, Doctor) or isinstance(current_user, Administrator)):
        abort(403)

    if isinstance(current_user, Doctor) and application.user_id != current_user.id:
        flash('У вас нет прав для редактирования этой заявки.', 'danger')
        return redirect('/all')

    form = ApplicationForm(obj=application)

    form.diagnosis_id.choices = [(d.id, d.name) for d in Diagnosis.query.all()]
    form.focus_id.choices = [(f.id, f.name) for f in EpidemicFocus.query.all()]

    if request.method == 'POST' and form.validate_on_submit():
        try:
            application.patient_full_name = form.patient_full_name.data
            application.birth_date = form.birth_date.data
            application.address = form.address.data
            application.contact_phone = form.contact_phone.data
            application.relative_contact_phone = form.relative_contact_phone.data
            application.workplace = form.workplace.data
            application.position = form.position.data
            application.diagnosis_id = form.diagnosis_id.data
            application.gdu = form.gdu.data
            application.registration_date = form.registration_date.data
            application.focus_id = form.focus_id.data
            application.reason_application = form.reason_application.data

            if form.reason_application.data == 'hospitalization':
                application.hospitalization_date = form.hospitalization_date.data
                application.place_of_hospitalization = form.place_of_hospitalization.data
            else:
                application.hospitalization_date = None
                application.place_of_hospitalization = None

            db.session.commit()
            flash('Заявка успешно обновлена!', 'success')
            return redirect('/all')

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
        
    application = Application.query.get(id)
    if not application:
        flash('Заявка не найдена.', 'danger')
        return redirect('/all')
    
    if isinstance(current_user, Doctor) and application.user_id != current_user.id:
        flash('У вас нет прав для удаления этой заявки.', 'danger')
        return redirect('/all')

    try:
        
        audit_log = ApplicationAuditLog(
            application_id=application.id,
            changed_by=current_user.id,
            change_type='DELETE',
            old_data=application.to_dict(), 
            new_data=None 
        )
        db.session.add(audit_log)
        db.session.flush()  

        db.session.delete(application)
        db.session.commit()

        flash('Заявка успешно удалена!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Произошла ошибка при удалении заявки: {str(e)}', 'danger')
        logger.error(f'Ошибка при удалении заявки {id}: {str(e)}')

    return redirect(url_for('application.all') )


@application.route('/application/<int:id>/download', methods=['GET'])
@login_required
def download_application(id):
    application = Application.query.get(id)
    if application is None:
        flash('Заявка не найдена', 'danger')
        return redirect(url_for('application.all'))

    epid_focus = EpidemicFocus.query.get(application.focus_id)
    doctor = Doctor.query.get(application.user_id)
    area = Area.query.get(doctor.area_id)
    diagnosis = Diagnosis.query.get(application.diagnosis_id)
    template_path = 'app/templates_docs/application_template.docx'

    doc = DocxTemplate(template_path)
    context = {
        'focus_id': epid_focus.name,
        'name_area': area.name_area,
        'id': str(application.id),
        'current_date': datetime.now().strftime("%d.%m.%Y"),
        'patient_full_name': application.patient_full_name,
        'birth_date': application.birth_date.strftime('%d.%m.%Y'),
        'address': application.address,
        'contact_phone': str(application.contact_phone),
        'relative_contact_phone': str(application.relative_contact_phone),
        'workplace': application.workplace,
        'position': application.position,
        'diagnosis_id': str(diagnosis.name),
        'gdu': str(application.gdu),
        'registration_date': application.registration_date.strftime('%d.%m.%Y'),
        'doctor_name': doctor.name,
        'reason_application': (
            f"{application.hospitalization_date.strftime('%d.%m.%Y')} {application.place_of_hospitalization}"
            if application.reason_application == 'hospitalization'
            else 'посмертно')
    }

    doc.render(context)
    doc_stream = BytesIO()
    doc.save(doc_stream)
    doc_stream.seek(0)

    current_date = datetime.now().strftime("%Y-%m-%d") 
    filename = f'{application.id}_{current_date}.docx'

    return send_file(doc_stream, as_attachment=True, download_name=filename, mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document')


@application.route('/api/diagnoses')
def api_diagnoses():
    diagnoses = Diagnosis.query.all()
    results = [{'id': d.id, 'text': d.name} for d in diagnoses]
    return jsonify(results)

@application.route('/api/gdu')
def api_gdu():
    groups = db.session.query(Application.gdu).distinct().all()
    results = [{'id': group[0], 'text': group[0]} for group in groups if group[0]]
    return jsonify(results)

@application.route('/api/gdu', methods=['POST'])
@login_required
def add_gdu():
    data = request.get_json()
    new_gdu = data.get('gdu_select')
    
    if not new_gdu:
        return jsonify({'error': 'GDU is required'}), 400
    
    try:
        
        return jsonify({'id': new_gdu, 'text': new_gdu}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---------------Для тестового заполнения таблицы заявок

@application.route('/application/fill', methods=['GET', 'POST'])
@login_required
def fill():
    if isinstance(current_user, Administrator):
        for i in range(1, 50):
            
            n = random.randint(2, 12)
            application = Application(
                patient_full_name=f"Тестов{i} Тест Тестович",
                birth_date=datetime.now() - timedelta(days=18250 + i),
                address=f"г.Тестовое, ул. Тестовая, д.1, кв.{i}" if i % 10 == 0 else f"г.Тестовое, ул. Тестовая, д.{i % 10}, кв.{i}",
                contact_phone=f"8912345678{i % 10}",
                relative_contact_phone=f"8912345678{i % 10 + 1}",
                workplace='ООО "Тестовое"',
                position=f"Тестер{i}",
                diagnosis_id=random.randint(1, 42),
                focus_id=random.randint(1, 6),
                gdu= 'I',
                user_id= 219 + n,
                reason_application='hospitalization',
                registration_date=datetime.now() - timedelta(days=i * 10),
                submission_date=datetime.now() + timedelta(days=i * 2),
                hospitalization_date=datetime.now() - timedelta(days=i * 10),
                place_of_hospitalization='клиника 1'
            )
            try:
                db.session.add(application)
                db.session.commit()
                flash('Заявка успешно создана!', 'success')
            except Exception as e:
                db.session.rollback()
                flash(
                    'Произошла ошибка при создании заявки. Пожалуйста, попробуйте еще раз.', 'danger')

        return redirect('/all')
    else:
        abort(403)


@application.route('/add/<int:count>/doctors', methods=['GET', 'POST'])
@login_required
def user_doctor_fill(count):
    if not isinstance(current_user, Administrator):
        abort(403)
    
    total_areas = 12
    
    success_count = 0
    errors = []
    
    for i in range(1, count + 1):

        area_id = (i - 1) % total_areas + 1
        
        user = Doctor(
            name=f"doctor{i}",
            login=f"doctor{i}",
            password_hash=generate_password_hash('123qweASD'),
            area_id=area_id,
            user_type='doctor'
        )
        
        try:
            db.session.add(user)
            db.session.commit()
            success_count += 1
        except Exception as e:
            db.session.rollback()
            errors.append(f"Ошибка при создании врача {i}: {str(e)}")
    
    if success_count > 0:
        flash(f'Успешно создано {success_count} врачей!', 'success')
    if errors:
        flash('Некоторые врачи не были созданы. Подробности в логах.', 'danger')
 
    
    return redirect('/admin/users')

