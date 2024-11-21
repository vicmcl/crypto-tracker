from dateutil.relativedelta import relativedelta
from dateutil.parser import parse


def moving_window(start_date, end_date):
    if start_date is not None and end_date is not None:
        start, end = parse(start_date), parse(end_date)
        window = []

        while start < end:
            previous_month = end - relativedelta(months=1)
            if previous_month < start:
                previous_month = start
            window.append(
                (
                    str(previous_month.date().strftime("%d-%m-%Y")),
                    str(end.date().strftime("%d-%m-%Y")),
                )
            )
            end = previous_month
        return window
    else:
        return [(None, None)]
