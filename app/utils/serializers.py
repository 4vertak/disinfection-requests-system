from datetime import datetime, date

def json_serializer(obj):
    """Сериализует объекты datetime и date в строки."""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")