from pandas.tseries.holiday import *
from pandas.tseries.offsets import Day, CustomBusinessDay

class ProjectCalendar(AbstractHolidayCalendar):
    rules = [
        Holiday('New Years Day', month=1, day=1),
        EasterMonday,
        Holiday('Labour Day', month=5, day=1),
        Holiday('Christmas Day', month=12, day=25),
        Holiday('Boxing Day', month=12, day=26, observance=next_monday)
    ]