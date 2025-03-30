import json
from ....utils.serializers import json_serializer
from sqlalchemy import event
from .entities import Application, ApplicationAuditLog
from ....core.extensions import db


@event.listens_for(Application, 'after_insert')
def log_application_insert(mapper, connection, target):
    audit_log = ApplicationAuditLog(
        application_id=target.id,
        changed_by=target.user_id,
        change_type='INSERT',
        new_data=target.to_dict()  
    )
    db.session.add(audit_log)


@event.listens_for(Application, 'after_update')
def log_application_update(mapper, connection, target):
    previous_state = {}
    for key, value in db.inspect(target).attrs.items():
        if key != 'id' and key != 'user_id':
            previous_state[key] = value.history.unchanged[0] if value.history.unchanged else None

    audit_log = ApplicationAuditLog(
        application_id=target.id,
        change_type='UPDATE',
        old_data=json.loads(json.dumps(
            previous_state, default=json_serializer)),
        new_data=target.to_dict() 
    )
    if target.user_id:
        audit_log.changed_by= target.user_id 
    else:  
        audit_log.changed_by = 104
    db.session.add(audit_log)
    


@event.listens_for(Application, 'after_delete')
def log_application_delete(mapper, connection, target):
    audit_log = ApplicationAuditLog(
        application_id=target.id,
        changed_by=target.user_id,
        change_type='DELETE',
        old_data=target.to_dict()
    )
    db.session.add(audit_log)