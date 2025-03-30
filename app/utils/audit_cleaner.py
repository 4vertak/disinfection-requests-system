from datetime import datetime, timedelta
from ..core.extensions import db
from ..domain.models.audit.entities import ApplicationAuditLog


def cleanup_old_audit_logs():
    one_year_ago = datetime.now() - timedelta(days=365)
    ApplicationAuditLog.query.filter(
        ApplicationAuditLog.change_time < one_year_ago).delete()
    db.session.commit()