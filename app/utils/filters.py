from zoneinfo import ZoneInfo

def localtime_filter(dt, tz_name="Asia/Yakutsk"):
  if dt is None:
    return ""
  return (dt.replace(tzinfo=ZoneInfo("UTC")).astimezone(ZoneInfo(tz_name)).strftime("%d-%m-%Y %H:%M"))
