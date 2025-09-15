

from datetime import datetime
from io import BytesIO
from typing import Optional

from sqlalchemy import desc
from ..models.application.entities import Application, Diagnosis, Disinfection, EpidemicFocus, Area, Doctor
from ..models.audit.entities import ApplicationAuditLog
from ..models.user.entities import User
from ...core.extensions import db

from asyncio.log import logger
from docxtpl import DocxTemplate


class ApplicationService:
    @staticmethod
    def _get_or_create_doctor(doctor_full_name: str, doctor_area: Optional[str] = None) -> Doctor:
        """
        Находит врача в справочнике или создаёт нового.
        """
        if not doctor_full_name:
            return None  # type: ignore  # тут ок, так как метод возвращает Doctor, но None не дойдёт дальше

        doctor = Doctor.query.filter_by(full_name=doctor_full_name).first()
        if doctor:
            return doctor

        doctor = Doctor(full_name=doctor_full_name, dispensary_area=doctor_area or "")
        db.session.add(doctor)
        db.session.flush()  # чтобы id был доступен сразу
        return doctor

    @staticmethod
    def get_applications(user_id):
        """Запрос списка заявок"""
        query = (
            db.session.query(Application, Disinfection, Area, Doctor)
            .join(Disinfection, Disinfection.application_id == Application.id)
            .join(Doctor, Doctor.id == Application.doctor_id)
            .join(Area, Area.id == Doctor.area_id)
        )

        applications = query.order_by(
            desc(Application.user_id == user_id),
            desc(Application.submission_date)
        ).all()

        return applications

    @staticmethod
    def create_application(form_data, user: User):
        """Создание новой заявки"""
        try:
            doctor_obj = None
            doctor_full_name = getattr(form_data, "doctor_full_name", None)
            doctor_area = getattr(form_data, "doctor_area", None)

            if user.role == "Doctor" and doctor_full_name and doctor_full_name.data:
                doctor_obj = ApplicationService._get_or_create_doctor(
                    doctor_full_name.data.strip(),
                    doctor_area.data.strip() if doctor_area and doctor_area.data else None
                )

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
                user_id=user.id,
                reason_application=form_data.reason_application.data,
                status="incompleted",
                doctor_id=doctor_obj.id if doctor_obj else None,
                doctor_full_name=doctor_full_name.data if doctor_full_name else None,
                doctor_area=doctor_area.data if doctor_area else None,
            )

            if form_data.reason_application.data == "hospitalization":
                application.hospitalization_date = form_data.hospitalization_date.data
                application.place_of_hospitalization = form_data.place_of_hospitalization.data

            db.session.add(application)
            db.session.commit()
            return application
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating application: {str(e)}")
            raise

    @staticmethod
    def update_application(application_id, form_data, user: User):
        """Обновление заявки"""
        application = Application.query.get(application_id)
        if not application:
            raise ValueError("Application not found")

        if user.role == "Doctor" and application.user_id != user.id:
            raise PermissionError("No rights to edit this application")

        try:
            # обновляем основные поля
            application.patient_full_name = form_data.patient_full_name.data
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

            if form_data.reason_application.data == "hospitalization":
                application.hospitalization_date = form_data.hospitalization_date.data
                application.place_of_hospitalization = form_data.place_of_hospitalization.data
            else:
                application.hospitalization_date = None
                application.place_of_hospitalization = None

            # обработка врача
            doctor_obj = None
            doctor_full_name = getattr(form_data, "doctor_full_name", None)
            doctor_area = getattr(form_data, "doctor_area", None)

            if doctor_full_name and doctor_full_name.data:
                doctor_obj = ApplicationService._get_or_create_doctor(
                    doctor_full_name.data.strip(),
                    doctor_area.data.strip() if doctor_area else None
                )

            application.doctor_id = doctor_obj.id if doctor_obj else None
            application.doctor_full_name = doctor_full_name.data if doctor_full_name else None
            application.doctor_area = doctor_area.data if doctor_area and doctor_area.data else None

            db.session.commit()
            return application
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating application {application_id}: {str(e)}")
            raise
    
    @staticmethod
    def delete_application(application_id, current_user):
        """Удалить заявку"""
        application = Application.query.get(application_id)
        if not application:
            raise ValueError("Заявка не найдена")

        if current_user.role == "Doctor" and application.user_id != current_user.id:
            raise PermissionError("Нет прав на удаление этой заявки")

        db.session.delete(application)
        db.session.commit()
        
        
    @staticmethod
    def generate_application_doc(application_id):
        """Генерация документа заявки"""
        application = Application.query.get(application_id)
        if not application:
            raise ValueError("Application not found")

        epid_focus = EpidemicFocus.query.get(application.focus_id)
        diagnosis = Diagnosis.query.get(application.diagnosis_id)

        doctor = Doctor.query.get(application.doctor_id) if application.doctor_id else None
        doctor_name = doctor.full_name if doctor else application.doctor_full_name or "-"
        doctor_area = (
            doctor.dispensary_area if doctor else application.doctor_area or "-"
        )

        template_path = "app/templates_docs/application_template.docx"
        doc = DocxTemplate(template_path)

        context = {
            "focus_id": epid_focus.name if epid_focus else "-",
            "name_area": doctor_area,
            "id": str(application.id),
            "current_date": datetime.now().strftime("%d.%m.%Y"),
            "patient_full_name": application.patient_full_name,
            "birth_date": application.birth_date.strftime("%d.%m.%Y")
            if application.birth_date
            else "-",
            "address": application.address,
            "contact_phone": str(application.contact_phone or "-"),
            "relative_contact_phone": str(application.relative_contact_phone or "-"),
            "workplace": application.workplace,
            "position": application.position,
            "diagnosis_id": str(diagnosis.name if diagnosis else "-"),
            "gdu": str(application.gdu),
            "registration_date": application.registration_date.strftime("%d.%m.%Y")
            if application.registration_date
            else "-",
            "doctor_name": doctor_name,
            "reason_application": (
                f"{application.hospitalization_date.strftime('%d.%m.%Y')} {application.place_of_hospitalization}"
                if application.reason_application == "hospitalization"
                and application.hospitalization_date
                else "посмертно"
            ),
        }

        doc.render(context)
        doc_stream = BytesIO()
        doc.save(doc_stream)
        doc_stream.seek(0)

        return doc_stream
