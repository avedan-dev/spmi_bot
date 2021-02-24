from datetime import date
import calendar


def week_number():
    today = date.today()
    return today.strftime("%W")


def get_prev_date(n):
    today = date.today()
    if today.isoweekday() != n:
        x = -today.isoweekday() + n
    else:
        return today
    if today.day + x > 0:
        if today.day + x<=calendar.monthrange(today.year, today.month)[1]:
          return today.replace(day=today.day + x)
        else:
          return today.replace(day=today.day + x-calendar.monthrange(today.year, today.month)[1],  month=today.month+1)
    else:
        return today.replace(day=calendar.monthrange(today.year, today.month-1)[1] + today.day + x, month=today.month-1)
