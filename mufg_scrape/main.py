import logging.config
import sys
import time
import yaml
import traceback
from datetime import date
from flask import jsonify, Flask

from models import mufg_scrape, mufg_extract, model_exceptions, LINE
from settings import settings
# from utils.get_secret import get_secret

app = Flask(__name__)

try:
    logging.config.dictConfig(settings.log_config)
except AttributeError:
    print(settings.log_config)
    logging.basicConfig(level=logging.WARN)

logger = logging.getLogger(__name__)
TODAY = date.today().strftime('%Y-%m-%d')


# def get_config():
#     try:
#         with open(settings.env_filepath, 'r') as f:
#             config = yaml.load(f, Loader=yaml.SafeLoader)
#         return config
#     except FileNotFoundError as e:
#         raise Exception(e)
#     except AttributeError as e:
#         raise Exception(e)


def scraping():
    try:
        # mufg_uid = get_secret(settings.gcp_project_id, 'mufg_uid', 'latest')
        # mufg_pass = get_secret(settings.gcp_project_id, 'mufg_pass', 'latest')

        scrape = mufg_scrape.MufgScrape(settings.mufg_uid, settings.mufg_pass)
        logger.info('Scraping start')
        scrape.open_page()
        time.sleep(1)
        scrape.to_login_page()
        time.sleep(1)
        scrape.login()
        time.sleep(1)
        top_page_filepath = scrape.scrape_top_page()
        time.sleep(1)
        scrape.to_product_page()
        time.sleep(1)
        scrape.to_product_info_tab()
        time.sleep(1)
        product_page_filepath = scrape.scrape_product_page()
        time.sleep(1)
        scrape.logout()
        logger.info('Scraping success')
        return top_page_filepath, product_page_filepath
    except model_exceptions.ScrapeModelException as e:
        scrape.driver.save_screenshot(f'ng_image_{TODAY}.png')
        raise model_exceptions.ScrapeModelException(e)
    finally:
        scrape.driver_close()


def extract_scrape_data(top_page_filepath, product_page_filepath):
    try:
        extract = mufg_extract.MufgExtract(top_page_filepath, product_page_filepath)
        all_data = extract.extract_main()
        product_data = extract.extract_products()
        result = {
            'all_data': all_data,
            'products_data': product_data
        }
        return result
    except model_exceptions.ExtractModelException as e:
        raise Exception(e)


def make_message(data):
    message = f"""
{TODAY} 確定拠出年金レポート

全体利回り: {data['all_data']['yields']}%
資産評価額: {data['all_data']['valuation']}円
拠出金累計: {data['all_data']['contribution_amount']}円
評価損益: {data['all_data']['gain_loss']}円
"""
    for product in data['products_data']:
        message += f"""
商品名: {product['product_name']}
資産評価額: {product['valuation']}円
拠出金額累計: {product['contribution_amount']}円
損益: {product['gain_loss']}円
損益率: {product['gain_loss_rate']}%
"""
    return message


def send_line(message):
    # line_token = get_secret(settings.gcp_project_id, 'line_token', 'latest')
    line_token = settings.line_token
    # line = LINE.Line(config['LINE_TOKEN'])
    line = LINE.Line(line_token)
    r = line.send(message)

    if r.status_code != 200:
        logger.error(r.text)
        raise Exception('LINE送信に失敗しました')

    logger.info(f'LINE Send status: {r.status_code}')
    return r.status_code


@app.route("/", methods=['GET', 'POST'])
def main():
    try:
        logger.info('Mufg Scraping start')
        # config = get_config()
        top_page_filepath, product_page_filepath = scraping()
        result = extract_scrape_data(top_page_filepath, product_page_filepath)
        send_line(make_message(result))
        return 'success', 200
        # return jsonify({'result': 'success'}), 200
    except Exception:
        t, v, tb = sys.exc_info()
        logger.error(traceback.format_tb(tb))
        logger.error(t)
        send_line(f'{TODAY} Mufg Scrapingが失敗しました')
        return 'failed', 500
        # return jsonify({'result': 'failed'}), 500
    finally:
        logger.info('Mufg Scraping end')


if __name__ == '__main__':
    # main()
    app.run(debug=True, host="0.0.0.0", port=8080)
