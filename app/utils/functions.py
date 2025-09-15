
from datetime import date, datetime, time
from docx.shared import Pt
import os.path
import secrets
from PIL import Image

from flask import current_app
from sqlalchemy import func

from ..domain.models.user.entities import User

from ..domain.models.application.entities import Application, Disinfection, EpidemicFocus, Doctor, Area

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
    end_date_with_time = datetime.combine(end_date, time.max)
    
    group_by_day = (end_date - start_date).days <= 31
    
    if group_by_day:
        query = db.session.query(
            func.date(getattr(model, date_field)).label('date'),
            func.count(getattr(model, 'id')).label('count')
        ).filter(
            getattr(model, date_field) >= start_date,
            getattr(model, date_field) <= end_date_with_time
        ).group_by('date').order_by('date')
    else:
        query = db.session.query(
            func.date_trunc('month', getattr(model, date_field)).label('date'),
            func.count(getattr(model, 'id')).label('count')
        ).filter(
            getattr(model, date_field) >= start_date,
            getattr(model, date_field) <= end_date_with_time
        ).group_by('date').order_by('date')
    
    return query.all()


def get_monthly_data_logs(model, date_field, start_date, end_date):
    months_ru = ["январь", "февраль", "март", "апрель", "май", "июнь",
                "июль", "август", "сентябрь", "октябрь", "ноябрь", "декабрь"]
    
    end_date_with_time = datetime.combine(end_date, time.max) if isinstance(end_date, date) else end_date
    
    try:
        monthly_data = db.session.query(
            func.date_trunc('month', getattr(model, date_field)).label('month'),
            getattr(model, 'change_type'),
            func.count(getattr(model, 'id')).label('total')
        ).filter(
            getattr(model, date_field) >= start_date,
            getattr(model, date_field) <= end_date_with_time
        ).group_by('month', 'change_type').order_by('month').all()
        
        result = {}
        current_date = start_date.replace(day=1)
        
        while current_date <= end_date:
            month_str = f"{months_ru[current_date.month - 1]} {current_date.year}"
            result[month_str] = {'INSERT': 0, 'UPDATE': 0, 'DELETE': 0}
            
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
        
        for entry in monthly_data:
            month_str = f"{months_ru[entry.month.month - 1]} {entry.month.year}"
            if month_str in result and entry.change_type in result[month_str]:
                result[month_str][entry.change_type] = entry.total
                
        return result
    
    except Exception as e:
        return {f"{months_ru[start_date.month - 1]} {start_date.year}": 
               {'INSERT': 0, 'UPDATE': 0, 'DELETE': 0}}



def combine_monthly_data(monthly_app_data, monthly_dis_data, start_date, end_date):
    months_ru = ["январь", "февраль", "март", "апрель", "май", "июнь",
                 "июль", "август", "сентябрь", "октябрь", "ноябрь", "декабрь"]

    combined_data = {}
    current_date = start_date.replace(day=1)
    
    while current_date <= end_date:
        month_str = months_ru[current_date.month - 1]
        year_str = str(current_date.year)
        key = f"{month_str} {year_str}"
        combined_data[key] = {'applications': 0, 'disinfections': 0}
        
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)

    for date_obj, count in monthly_app_data:
        month_str = months_ru[date_obj.month - 1]
        year_str = str(date_obj.year)
        key = f"{month_str} {year_str}"
        if key in combined_data:
            combined_data[key]['applications'] = count

    for date_obj, count in monthly_dis_data:
        month_str = months_ru[date_obj.month - 1]
        year_str = str(date_obj.year)
        key = f"{month_str} {year_str}"
        if key in combined_data:
            combined_data[key]['disinfections'] = count

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
        User.id,
        User.username.label("name"),
        func.count(Disinfection.id).label("disinfection_count"),
        func.coalesce(func.sum(Disinfection.area_size), 0).label("total_area")
    ).join(Disinfection, User.id == Disinfection.user_id)\
     .filter(User.role == "Disinfector")

    if start_date and end_date:
        query = query.filter(Disinfection.disinfection_date.between(start_date, end_date))

    return (query.group_by(User.id, User.username)
                 .order_by(func.count(Disinfection.id).desc())
                 .all())