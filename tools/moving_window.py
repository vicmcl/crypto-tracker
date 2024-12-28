from dateutil.relativedelta import relativedelta
from dateutil.parser import parse


# function to split the date range into moving windows of 1 month
def moving_window(start_date, end_date):
    start_date = parse(start_date, dayfirst=True)
    end_date = parse(end_date, dayfirst=True)
    while start_date < end_date:
        if start_date + relativedelta(months=1) > end_date:
            break
        yield (
            start_date.strftime("%d-%m-%Y"),
            (start_date + relativedelta(months=1)).strftime("%d-%m-%Y"),
        )
        start_date = start_date + relativedelta(months=1)
    yield (start_date.strftime("%d-%m-%Y"), end_date.strftime("%d-%m-%Y"))
