from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import SubmitField, DateField, FloatField, TextAreaField
from wtforms.validators import DataRequired, Optional


class DisinfectionForm(FlaskForm):
    area_size = FloatField('Площадь помещения (кв.м.)',
                           validators=[Optional()], default=0)
    rejection_reason = TextAreaField('Причина отказа', validators=[
                                     Optional()], default='completed')
    disinfection_date = DateField(
        'Дата проведения дезинфекции', format='%Y-%m-%d', validators=[DataRequired()], default=datetime.now())

    volume_size = FloatField('Объем помещения (куб.м.)',
                             validators=[Optional()])
    spraying_time = TextAreaField('Время раcпыления', validators=[
                                  Optional()])
    submit = SubmitField('Добавить')
