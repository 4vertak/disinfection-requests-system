from datetime import datetime
import json

from ..audit.entities import ApplicationAuditLog
from ....utils.serializers import json_serializer
from sqlalchemy.orm import relationship
from sqlalchemy import event
from ....core.extensions import db


class Diagnosis(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    mkb_code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    applications = db.relationship(
        'Application', backref='diagnosis', lazy=True)

class EpidemicFocus(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    applications = db.relationship(
        'Application', backref='epidemic_focus', lazy=True)


class Application(db.Model):
    __tablename__ = 'application'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    submission_date = db.Column(db.DateTime, default=datetime.now)
    patient_full_name = db.Column(db.String(255), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    address = db.Column(db.String(255), nullable=False)
    contact_phone = db.Column(db.String(20), nullable=True)
    relative_contact_phone = db.Column(db.String(20))
    workplace = db.Column(db.String(255))
    position = db.Column(db.String(100))
    registration_date = db.Column(db.Date)
    diagnosis_id = db.Column(db.Integer, db.ForeignKey('diagnosis.id'))
    gdu = db.Column(db.String(20))
    focus_id = db.Column(db.Integer, db.ForeignKey('epidemic_focus.id'))
    reason_application = db.Column(
        db.String(255), nullable=False, default='hospitalization')
    status = db.Column(db.String(20), default='incompleted', nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'doctor.id', ondelete='SET NULL'), nullable=True)
    hospitalization_date = db.Column(db.Date, nullable=True)
    place_of_hospitalization = db.Column(
        db.String(255), nullable=True)

    disinfection = relationship(
        'Disinfection', back_populates='application', cascade='all, delete-orphan')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        new_disinfection = Disinfection(
            application=self)
        self.disinfection.append(new_disinfection)

    def to_dict(self):
        data = {
            'id': self.id,
            'submission_date': self.submission_date,
            'patient_full_name': self.patient_full_name,
            'birth_date': self.birth_date,
            'address': self.address,
            'contact_phone': self.contact_phone,
            'relative_contact_phone': self.relative_contact_phone,
            'workplace': self.workplace,
            'position': self.position,
            'registration_date': self.registration_date,
            'diagnosis_id': self.diagnosis_id,
            'gdu': self.gdu,
            'focus_id': self.focus_id,
            'reason_application': self.reason_application,
            'status': self.status,
            'user_id': self.user_id,
            'hospitalization_date': self.hospitalization_date,
            'place_of_hospitalization': self.place_of_hospitalization
        }
        return json.loads(json.dumps(data, ensure_ascii=False, default=json_serializer))


class Disinfection(db.Model):
    __tablename__ = 'disinfection'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    application_id = db.Column(db.Integer, db.ForeignKey(
        'application.id'), nullable=False)
    rejection_reason = db.Column(db.String(255))
    disinfection_date = db.Column(db.DateTime)
    area_size = db.Column(db.Float)
    volume_size = db.Column(db.Float)
    spraying_time = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey(
        'disinfector.id', ondelete='SET NULL'), nullable=True)

    application = relationship('Application', back_populates='disinfection')


@event.listens_for(Application, 'after_insert')
def log_application_insert(mapper, connection, target):
    audit_log = ApplicationAuditLog(application_id=target.id,changed_by=target.user_id,change_type='INSERT',new_data=target.to_dict())
    db.session.add(audit_log)
    
    
@event.listens_for(Application, 'after_update')
def log_application_update(mapper, connection, target):
    previous_state = {}
    for key, value in db.inspect(target).attrs.items():
        if key != 'id' and key != 'user_id':
            previous_state[key] = value.history.unchanged[0] if value.history.unchanged else None
    
    audit_log = ApplicationAuditLog(application_id=target.id, change_type='UPDATE', old_data=json.loads(json.dumps(previous_state, default=json_serializer)),new_data=target.to_dict() )
    if target.user_id:
        audit_log.changed_by= target.user_id 
    else:  
        audit_log.changed_by = 104
    db.session.add(audit_log)
        
    
    
    # @event.listens_for(Application, 'after_delete')
    # def log_application_delete(mapper, connection, target):
    #     audit_log = ApplicationAuditLog(
    #         application_id=target.id,
    #         changed_by=target.user_id,
    #         change_type='DELETE',
    #         old_data=target.to_dict()
    #     )
    #     db.session.add(audit_log)




