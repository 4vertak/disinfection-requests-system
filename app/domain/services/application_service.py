

from datetime import datetime
from io import BytesIO
import io
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
    def _get_or_create_doctor(doctor_full_name: str, area_id: Optional[int] = None) -> Doctor:
        """
        Находит врача в справочнике или создаёт нового.
        """
        if not doctor_full_name or not area_id:
            return None  # type: ignore # не создаём врача без имени или участка

        # Ищем врача с таким ФИО и участком
        doctor = Doctor.query.filter_by(full_name=doctor_full_name.strip(), area_id=area_id).first()
        if doctor:
            return doctor

        # Создаём нового врача
        doctor = Doctor(full_name=doctor_full_name.strip(), area_id=area_id)
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
            # desc(Application.user_id == user_id),
            desc(Application.submission_date)
        ).all()

        return applications
    @staticmethod
    def create_application(form_data, user: User, doctor_obj: Optional[Doctor] = None):
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
                user_id=user.id,
                reason_application=form_data.reason_application.data,
                status="incompleted",
                doctor_id=doctor_obj.id if doctor_obj else (form_data.doctor_id.data if form_data.doctor_id.data != 0 else None),
                doctor_full_name=form_data.doctor_full_name.data if form_data.doctor_full_name.data else None,
                area_id=form_data.area_id.data,
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
    def update_application(application_id, form_data, user: User, doctor_obj: Optional[Doctor] = None):
        application = Application.query.get(application_id)
        if not application:
            raise ValueError("Application not found")

        if user.user_type == "doctor" and application.user_id != user.id:
            raise PermissionError("No rights to edit this application")

        try:
            # Основные поля
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
            application.user_id = user.id
            application.reason_application = form_data.reason_application.data

            # Госпитализация
            if form_data.reason_application.data == "hospitalization":
                application.hospitalization_date = form_data.hospitalization_date.data
                application.place_of_hospitalization = form_data.place_of_hospitalization.data
            else:
                application.hospitalization_date = None
                application.place_of_hospitalization = None

            # Врач и участок — только через doctor_obj
            if doctor_obj:
                application.doctor_id = doctor_obj.id
                application.doctor_full_name = doctor_obj.full_name
                application.area_id = doctor_obj.area_id
            else:
                # Если не выбран врач — сбрасываем поля
                application.doctor_id = None
                application.doctor_full_name = form_data.doctor_full_name.data if form_data.doctor_full_name.data else None
                application.area_id = form_data.area_id.data

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

        # Получаем эпидемический очаг и диагноз
        epid_focus = EpidemicFocus.query.get(application.focus_id)
        diagnosis = Diagnosis.query.get(application.diagnosis_id)

        # Получаем врача, если выбран из справочника
        doctor = Doctor.query.get(application.doctor_id) if application.doctor_id else None

        # Имя врача
        doctor_name = doctor.full_name if doctor else application.doctor_full_name or "-"

        # Название участка
        if doctor:
            # Через связь с Area, если она есть
            if hasattr(doctor, "area") and doctor.area:
                doctor_area = doctor.area.name_area
            else:
                # fallback по area_id
                area = Area.query.get(doctor.area_id)
                doctor_area = area.name_area if area else "-"
        else:
            doctor_area = application.doctor_area or "-"

        # Шаблон документа
        template_path = "app/templates_docs/application_template.docx"
        doc = DocxTemplate(template_path)

        context = {
            "focus_id": epid_focus.name if epid_focus else "-",
            "name_area": doctor_area,
            "id": str(application.id),
            "current_date": datetime.now().strftime("%d.%m.%Y"),
            "patient_full_name": application.patient_full_name,
            "birth_date": application.birth_date.strftime("%d.%m.%Y") if application.birth_date else "-",
            "address": application.address,
            "contact_phone": str(application.contact_phone or "-"),
            "relative_contact_phone": str(application.relative_contact_phone or "-"),
            "workplace": application.workplace or "-",
            "position": application.position or "-",
            "diagnosis_id": diagnosis.name if diagnosis else "-",
            "gdu": str(application.gdu or "-"),
            "registration_date": application.registration_date.strftime("%d.%m.%Y") if application.registration_date else "-",
            "doctor_name": doctor_name,
            "reason_application": (
                f"{application.hospitalization_date.strftime('%d.%m.%Y')} {application.place_of_hospitalization}"
                if application.reason_application == "hospitalization"
                and application.hospitalization_date
                else "посмертно"
            ),
        }

        doc.render(context)

        # Возвращаем поток документа
        doc_stream = io.BytesIO()
        doc.save(doc_stream)
        doc_stream.seek(0)
        return doc_stream

