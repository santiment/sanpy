import datetime

def today():
    return datetime.date.today()

def two_days_ago():
    return (today() - datetime.timedelta(days=2)).isoformat()

def four_days_ago():
    return (today() - datetime.timedelta(days=4)).isoformat()

def month_ago():
    return (today() - datetime.timedelta(days=30)).isoformat()

class TestResponse:
    def __init__(self, **kwargs):
        self.status_code = kwargs['status_code']
        if 'errors' in kwargs['data']:
            self.data = kwargs['data']
        else:
            self.data = {'data': kwargs['data']}

    def json(self):
        return self.data

    def status_code(self):
        return self.status_code
