import logging.config
import requests
from datetime import date

from settings import settings

try:
    logging.config.dictConfig(settings.log_config)
except AttributeError:
    print(settings.log_config)
    logging.basicConfig(level=logging.WARN)

logger = logging.getLogger(__name__)


class Line:
    def __init__(self, token):
        self.url = 'https://notify-api.line.me/api/notify'
        # self.token = utils.get_secret('line_token', 'latest', gcp_project_id)
        # self.token = token
        self.headers = {'Authorization': 'Bearer ' + token}

    def send(self, message=None, image=None):
        file = {}
        if image:
            file = {'imageFile': open(image, 'rb')}

        payload = {'message': message}
        r = requests.post(self.url, headers=self.headers, params=payload, files=file)

        return r
