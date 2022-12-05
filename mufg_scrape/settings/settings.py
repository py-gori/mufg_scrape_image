import os
import logging.config

ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.5304.62 Safari/537.36'
url = 'http://www.dc.tr.mufg.jp/?top'
file_dir = 'files'
gcp_project_id = os.getenv('GCP_PROJECT_ID')
selenium_chrome_url = os.getenv('SELENIUM_CHROME_URL')
mufg_uid = os.getenv('MUFG_UID')
mufg_pass = os.getenv('MUFG_PASS')
line_token = os.getenv('LINE_TOKEN')

log_config = {
    'version': 1,
    'formatters': {
        'baseFormatter': {
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
        }
    },
    'handlers': {
        'debugStreamHandlers': {
            'class': 'logging.StreamHandler',
            'formatter': 'baseFormatter',
            'level': logging.DEBUG
        },
        # 'debugFileHandlers': {
        #     'class': 'logging.FileHandler',
        #     'filename': '',
        #     'formatter': 'baseFormatter',
        #     'level': logging.DEBUG
        # },
        'infoStreamHandlers': {
            'class': 'logging.StreamHandler',
            'formatter': 'baseFormatter',
            'level': logging.INFO
        }
    },
    'root': {
        # 'handlers': ['debugFileHandlers', 'infoStreamHandlers'],
        'handlers': ['debugStreamHandlers'],
        'level': logging.DEBUG,
    },
    'loggers': {
        'models.mufg_scrape': {
            # 'handlers': ['debugFileHandlers'],
            'handlers': ['infoStreamHandlers'],
            'level': logging.DEBUG,
            'propagate': 0
        },
        'models.mufg_extract': {
            # 'handlers': ['debugFileHandlers'],
            'handlers': ['infoStreamHandlers'],
            'level': logging.DEBUG,
            'propagate': 0
        },
        'models.LINE': {
            # 'handlers': ['debugFileHandlers'],
            'handlers': ['infoStreamHandlers'],
            'level': logging.DEBUG,
            'propagate': 0
        },
    }
}