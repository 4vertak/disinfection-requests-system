from datetime import datetime, time
from ..domain.models.application.entities import Application


def get_total_info(start_date, end_date):
    
    if isinstance(end_date, datetime):
        end_date_with_time = end_date
    else:
        end_date_with_time = datetime.combine(end_date, time.max)
    
    base_query = Application.query.filter(
        Application.submission_date >= start_date,
        Application.submission_date <= end_date_with_time
    )
    
    total = base_query.count()
    
    completed = base_query.filter(
        Application.status == 'completed'
    ).count()
    
    refusal = base_query.filter(
        Application.status == 'refusal'
    ).count()
    
    in_progress = total - completed - refusal
    
    return {
        'total': total,
        'completed': completed,
        'in_progress': in_progress,
        'refusal': refusal
    }