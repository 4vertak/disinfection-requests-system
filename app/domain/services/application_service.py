from datetime import datetime
from io import BytesIO
from ..models.application.entities import Application, Diagnosis, Disinfection, EpidemicFocus
from ..models.audit.entities import ApplicationAuditLog
from ..models.user.entities import Area, Disinfector, Doctor
from ...core.extensions import db
# from ..utils.logger import logger
from asyncio.log import logger
from docxtpl import DocxTemplate

class ApplicationService:
    @staticmethod
    def get_applications(user_id):
        """Запрос списка заявок"""
        query = (db.session.query(Application, Disinfection, Area, Doctor).join(Disinfection, Disinfection.application_id == Application.id).join(Doctor, Doctor.id == Application.user_id).join(Area, Area.id == Doctor.area_id))
        if isinstance(user_id, Doctor):
            applications = query.filter(Application.user_id == user_id).order_by(Application.submission_date.asc()).all()
        else:
            applications = query.order_by(Application.submission_date.asc()).all()

        return applications

    @staticmethod
    def create_application(form_data, user_id):
        """Создание новой заявки"""
        try:
            application = Application(
                submission_date=datetime.now(),
                patient_full_name=form_data.patient_full_name.data,
                birth_date=form_data.birth_date.data,
                    address=form_data.address.data,
                    contact_phone=form_data.contact_phone.data,
                    relative_contact_phone=form_data.relative_contact_phone.data,
                    workplace=form_data.workplace.data,
                    position=form_data.position.data,
                    diagnosis_id=form_data.diagnosis_id.data,
                    gdu=form_data.gdu.data,
                    registration_date=form_data.registration_date.data,
                    focus_id=form_data.focus_id.data,
                user_id=user_id,
                reason_application=form_data.reason_application.data,
                    status='incompleted'
            )
            if form_data.reason_application.data == 'hospitalization':
                    application.hospitalization_date = form_data.hospitalization_date.data
                    application.place_of_hospitalization = form_data.place_of_hospitalization.data
            
            db.session.add(application)
            db.session.commit()
            return application
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error creating application: {str(e)}')
            raise

    @staticmethod
    def update_application(application_id, form_data, user):
        """Обновление заявки"""
        application = Application.query.get(application_id)
        if not application:
            raise ValueError("Application not found")
        
        # Проверка прав доступа
        if isinstance(user, Doctor) and application.user_id != user.id:
            raise PermissionError("No rights to edit this application")

        try:
            application.patient_full_name = form_data.patient_full_name.data
            # обновление остальных полей...
            application.birth_date = form_data.birth_date.data
            application.address = form_data.address.data
            application.contact_phone = form_data.contact_phone.data
            application.relative_contact_phone = form_data.relative_contact_phone.data
            application.workplace = form_data.workplace.data
            application.position = form_data.position.data
            application.diagnosis_id = form_data.diagnosis_id.data
            application.gdu = form_data.gdu.data
            application.registration_date = form_data.registration_date.data
            application.focus_id = form_data.focus_id.data
            application.reason_application = form_data.reason_application.data

            if form_data.reason_application.data == 'hospitalization':
                application.hospitalization_date = form_data.hospitalization_date.data
                application.place_of_hospitalization = form_data.place_of_hospitalization.data
            else:
                application.hospitalization_date = None
                application.place_of_hospitalization = None
            
            db.session.commit()
            return application
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error updating application {application_id}: {str(e)}')
            raise

    @staticmethod
    def delete_application(application_id, user):
        """Удаление заявки"""
        application = Application.query.get(application_id)
        if not application:
            raise ValueError("Application not found")
        
        if isinstance(user, Doctor) and application.user_id != user.id or isinstance(user, Disinfector):
            raise PermissionError("No rights to delete this application")

        try:
            # Логирование удаления
            audit_log = ApplicationAuditLog(
                application_id=application.id,
                changed_by=user.id,
                change_type='DELETE',
                old_data=application.to_dict()
            )
            db.session.add(audit_log)
            db.session.flush()  # Принудительно фиксируем добавление записи в application_audit_log
            db.session.delete(application)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error deleting application {application_id}: {str(e)}')
            raise

    @staticmethod
    def generate_application_doc(application_id):
        """Генерация документа заявки"""
        application = Application.query.get(application_id)
        if not application:
            raise ValueError("Application not found")
        
        epid_focus = EpidemicFocus.query.get(application.focus_id)
        doctor = Doctor.query.get(application.user_id)
        area = Area.query.get(doctor.area_id)
        diagnosis = Diagnosis.query.get(application.diagnosis_id)

        template_path = 'app/templates_docs/application_template.docx'
        # Загружаем шаблон документа
        doc = DocxTemplate(template_path)

        # Подготавливаем данные для контекста
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
        
        return doc_stream