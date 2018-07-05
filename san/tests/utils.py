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
