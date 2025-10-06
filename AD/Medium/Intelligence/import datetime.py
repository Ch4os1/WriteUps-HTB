from datetime import datetime, timedelta

current_date = datetime(2020, 1, 1)
end_date = datetime.now()

while current_date.date() < end_date.date():
    print(current_date.strftime("%Y-%m-%d"))
    current_date += timedelta(days=1)