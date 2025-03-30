
from datetime import date
from docx.shared import Pt
import os.path
import secrets
from PIL import Image

from flask import current_app
from sqlalchemy import func
from werkzeug.security import generate_password_hash

from ..domain.models.user.entities import Area, Doctor, Disinfector

from ..domain.models.application.entities import Application, Disinfection, EpidemicFocus

from ..core.extensions import db


def save_picture(picture):
    if picture:
        random_hex = secrets.token_hex(8)
        _, f_ext = os.path.splitext(picture.filename)
        picture_fn = random_hex + f_ext
        picture_path = os.path.join(
            current_app.config['SERVER_PATH'], picture_fn)
        output_size = (125, 125)
        i = Image.open(picture)
        i.thumbnail(output_size)
        i.save(picture_path)
    else:
        picture_fn = 'user.svg'
        picture_path = os.path.join(
            current_app.config['SERVER_PATH'], picture_fn)
    return picture_fn


def recursive_flatten_iterator(d):
    for k, v in d.items():
        if isinstance(v, list):
            yield v
        if isinstance(v, dict):
            yield from recursive_flatten_iterator(v)


def set_font_for_document(doc, font_name='Times New Roman', font_size=12):
    for paragraph in doc.paragraphs:
        for run in paragraph.runs:
            run.font.name = font_name
            run.font.size = Pt(12)

def get_monthly_data(model, date_field, start_date, end_date):
    return db.session.query(
        func.date_trunc('month', getattr(model, date_field)).label('month'),
        func.count(getattr(model, 'id')).label('total')
    ).filter(
        getattr(model, date_field).between(start_date, end_date)
    ).group_by('month').order_by('month').all()


def get_monthly_data_logs(model, date_field, start_date, end_date):
    months_ru = ["январь", "февраль", "март", "апрель", "май", "июнь",
                 "июль", "август", "сентябрь", "октябрь", "ноябрь", "декабрь"]

    monthly_data = db.session.query(
        func.date_trunc('month', getattr(model, date_field)).label('month'),
        getattr(model, 'change_type').label('change_type'),
        func.count(getattr(model, 'id')).label('total')
    ).filter(
        getattr(model, date_field).between(start_date, end_date)
    ).group_by('month', 'change_type').order_by('month').all()

    result = {
        f'{months_ru[month - 1]}': {'INSERT': 0, 'UPDATE': 0, 'DELETE': 0}
        for year in range(start_date.year, end_date.year + 1)
        for month in range(1, 13)
        if (year > start_date.year or month >= start_date.month) and (year < end_date.year or month <= end_date.month)
    }

    for entry in monthly_data:
        month_number = entry.month.month 
        month_name = months_ru[month_number - 1]
        if month_name in result:
            result[month_name][entry.change_type] = entry.total

    return result


def combine_monthly_data(monthly_app_data, monthly_dis_data, start_date, end_date):
    months_ru = ["январь", "февраль", "март", "апрель", "май", "июнь",
                 "июль", "август", "сентябрь", "октябрь", "ноябрь", "декабрь"]

    combined_data = {
        f'{months_ru[month - 1]}': {'applications': 0, 'disinfections': 0}
        for year in range(start_date.year, end_date.year + 1)
        for month in range(1, 13)
        if (year > start_date.year or month >= start_date.month) and (year < end_date.year or month <= end_date.month)
    }

    for row in monthly_app_data:
        month_number = row.month.month
        month_str = months_ru[month_number - 1]
        if month_str in combined_data:
            combined_data[month_str]['applications'] = row.total

    for row in monthly_dis_data:
        month_number = row.month.month
        month_str = months_ru[month_number - 1]
        if month_str in combined_data:
            combined_data[month_str]['disinfections'] = row.total

    return combined_data


def get_areas_data_applicates(start_date, end_date):
    return db.session.query(
        Area.name_area.label('area_name'),
        func.count(Application.id).label('total')
    ).join(Doctor, Doctor.area_id == Area.id)\
     .join(Application, Application.user_id == Doctor.id)\
     .filter(Application.submission_date.between(start_date, end_date))\
     .group_by(Area.name_area)\
     .order_by(Area.name_area)\
     .all()


def get_areas_data_disinfection(start_date, end_date):
    return db.session.query(
        Area.name_area.label('area_name'),
        func.count(Disinfection.disinfection_date).label('total')
    ).join(Doctor, Doctor.area_id == Area.id)\
     .join(Application, Application.user_id == Doctor.id)\
     .join(Disinfection, Disinfection.application_id == Application.id)\
     .filter(Disinfection.disinfection_date.between(start_date, end_date))\
     .group_by(Area.name_area)\
     .order_by(Area.name_area)\
     .all()


def initialize_combined_areas_data():
    return {area.name_area: {'applications': 0, 'disinfections': 0} for area in db.session.query(Area).all()}


def combine_areas_data(areas_data_applicates, areas_data_disinfection):
    combined_areas_data = initialize_combined_areas_data()
    for row in areas_data_applicates:
        combined_areas_data[row.area_name]['applications'] = row.total
    for row in areas_data_disinfection:
        combined_areas_data[row.area_name]['disinfections'] = row.total
    return combined_areas_data


def prepare_areas_labels_and_values(combined_areas_data):
    areas_labels = list(combined_areas_data.keys())
    areas_total_values = [data['applications']
                          for data in combined_areas_data.values()]
    areas_completed_values = [data['disinfections']
                              for data in combined_areas_data.values()]

    return areas_labels, areas_total_values, areas_completed_values


def get_focus_data(start_date, end_date):
    return db.session.query(
        EpidemicFocus.name.label('focus_name'),
        Area.name_area.label('area_name'),
        func.count(Application.id).label('total')
    ).join(Application, Application.focus_id == EpidemicFocus.id) \
     .join(Disinfection, Disinfection.application_id == Application.id) \
     .join(Doctor, Doctor.id == Application.user_id) \
     .join(Area, Area.id == Doctor.area_id) \
     .filter(Application.submission_date.between(start_date, end_date)) \
     .group_by(EpidemicFocus.name, Area.name_area) \
     .order_by(EpidemicFocus.name, Area.name_area).all()


def initialize_combined_focus_areas_data(focus_data):
    combined_focus_areas_data = {}
    for row in focus_data:
        if row.focus_name not in combined_focus_areas_data:
            combined_focus_areas_data[row.focus_name] = {}

        combined_focus_areas_data[row.focus_name][row.area_name] = row.total
    return combined_focus_areas_data


def prepare_labels_and_values(combined_focus_areas_data):
    """Подготавливаем метки и значения для графика."""
    focus_labels = list(combined_focus_areas_data.keys())

    area_labels = list(set(
        label for areas in combined_focus_areas_data.values() for label in areas.keys()))

    focus_total_values = {
        focus: [combined_focus_areas_data[focus].get(
            area, 0) for area in area_labels]
        for focus in focus_labels
    }

    return focus_labels, area_labels, focus_total_values


def prepare_data_for_chart(focus_total_values, focus_labels):
    return [focus_total_values[focus] for focus in focus_labels]

def get_top_disinfectors(start_date, end_date):
    query = db.session.query(
        Disinfector.id,
        Disinfector.name,
        func.count(Disinfection.id).label('disinfection_count'),
        func.coalesce(func.sum(Disinfection.area_size), 0).label('total_area')
    ).join(Disinfection, Disinfector.id == Disinfection.user_id)
    
    if start_date and end_date:
        query = query.filter(Disinfection.disinfection_date.between(start_date, end_date))
    
    return query.group_by(Disinfector.id, Disinfector.name)\
               .order_by(func.count(Disinfection.id).desc())\
               .all()