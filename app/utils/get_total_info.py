from ..domain.models.application.entities import Application


def get_total_info(start_date, end_date):
    total = Application.query.filter(Application.submission_date.between(start_date, end_date)).count()
    completed = Application.query.filter(Application.submission_date.between(start_date, end_date), Application.status == 'completed').count()
    refusal = Application.query.filter(Application.submission_date.between(start_date, end_date), Application.status == 'refusal').count()
    in_progress = total - completed - refusal
    return {
        'total': total,
        'completed': completed,
        'in_progress': in_progress,
        'refusal': refusal
    }