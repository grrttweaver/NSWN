import datetime
import pytz

date_str ='2019-04-01T04:06:05-05:00'

date_str = date_str.replace('+00:00', '+0000')
dt = datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S%z")

print(dt)