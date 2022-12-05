import chromedriver_binary
import logging.config
import os
import time
from retry import retry
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common import exceptions

from models.model_exceptions import ScrapeModelException
from settings import settings

try:
    logging.config.dictConfig(settings.log_config)
except AttributeError:
    print(settings.log_config)
    logging.basicConfig(level=logging.WARN)

logger = logging.getLogger(__name__)


class MufgScrape:
    def __init__(self, uid, password):
        # self.config = config
        self.ua = settings.ua
        self.url = settings.url
        self.file_dir = settings.file_dir
        self.uid = uid
        self.password = password
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.driver = self.driver_init()

    def get_options(self):
        """ドライバーオプション取得"""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--user-agent=' + self.ua)
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1280x1696')
        options.add_argument('--hide-scrollbars')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--disable-dev-shm-usage')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        # options.add_argument('--remote-debugging-port=9222')
        return options

    def driver_init(self):
        # return webdriver.Chrome(options=self.get_options())
        # Seleniumコンテナで実行
        options = self.get_options()
        return webdriver.Remote(
            # command_executor='http://localhost:4444/wd/hub',
            # command_executor='https://selenium-run-lcsoken44q-an.a.run.app//wd/hub',
            # command_executor='https://mufg-selenium-chrome-lcsoken44q-an.a.run.app/wd/hub',
            command_executor=f'{settings.selenium_chrome_url}/wd/hub',
            options=options
        )

    def driver_close(self):
        # self.driver.close()
        # closeでは、セッションが残る為、quitする
        self.driver.quit()
        # windows = self.driver.window_handles
        # if not windows:
        #     return True
        # for window in windows:
        #     self.driver.switch_to.window(window)
        #     self.driver.close()

    def open_page(self):
        self.driver.get(self.url)

    @retry((exceptions.StaleElementReferenceException,
            exceptions.TimeoutException), tries=3, delay=3, logger=logger)
    def to_login_page(self):
        WebDriverWait(self.driver, 10).until(
            expected_conditions.element_to_be_clickable((By.CLASS_NAME, 'top_login_button'))
        )
        top_login_btn = self.driver.find_element(By.CLASS_NAME, 'top_login_button')
        top_login_btn.click()

    @retry((exceptions.StaleElementReferenceException,
            exceptions.TimeoutException), tries=2, delay=3, logger=logger)
    def login(self):
        windows = self.driver.window_handles
        # 別ウィンドウが立ち上がらなければ1度だけリトライ
        if len(windows) == 1:
            time.sleep(2)
            windows = self.driver.window_handles
        if len(windows) == 1:
            raise ScrapeModelException('login page can not open')
        self.driver.switch_to.window(windows[1])

        WebDriverWait(self.driver, 10).until(
            expected_conditions.visibility_of_element_located((By.ID, 'envUid')),
            expected_conditions.visibility_of_element_located((By.ID, 'envPass'))
        )
        login_id = self.driver.find_element(By.ID, 'envUid')
        login_id.send_keys(self.uid)

        login_pass = self.driver.find_element(By.ID, 'envPass')
        login_pass.send_keys(self.password)

        login_btn = self.driver.find_element(By.ID, 'loginButton')
        login_btn.click()
        logger.info('Login success')

    @retry((exceptions.StaleElementReferenceException,
            exceptions.TimeoutException), tries=2, delay=3, logger=logger)
    def modal_window_close(self):
        WebDriverWait(self.driver, 10).until(
            expected_conditions.element_to_be_clickable((By.XPATH, '//*[@id="syohinGuideBookAlert"]/div'))
        )
        self.driver.find_element(By.XPATH, '//*[@id="syohinGuideBookAlert"]/div').click()
        logger.info('ModalWindow closed')

    def scrape_top_page(self):
        try:
            self.modal_window_close()
        except exceptions.TimeoutException:
            logger.warning('ModalWindow not open')

        main_html = self.driver.page_source
        filepath = self.save_html('top_page.html', main_html)
        logger.info('ScrapeTopPage success')
        return filepath

    @retry((exceptions.StaleElementReferenceException,
            exceptions.TimeoutException), tries=2, delay=3, logger=logger)
    def to_product_page(self):
        WebDriverWait(self.driver, 10).until(
            expected_conditions.element_to_be_clickable((By.CLASS_NAME, 'linkReview'))
        )
        # 運用資産状況ページへ遷移
        self.driver.find_element(By.CLASS_NAME, 'linkReview').click()

    @retry((exceptions.StaleElementReferenceException,
            exceptions.TimeoutException), tries=2, delay=3, logger=logger)
    def to_product_info_tab(self):
        WebDriverWait(self.driver, 10).until(
            expected_conditions.visibility_of_element_located((By.XPATH, '//*[@class="review_tab"]/ul/li'))
        )
        # 運用資産タブ
        li_elems = self.driver.find_elements(By.XPATH, '//*[@class="review_tab"]/ul/li')
        # 運用商品別情報(タブ2番目)をクリック
        if len(li_elems) != 2:
            raise ScrapeModelException('product_info tab not found')
        li_elems[1].click()

    @retry((exceptions.StaleElementReferenceException,
            exceptions.TimeoutException), tries=2, delay=3, logger=logger)
    def scrape_product_page(self):
        WebDriverWait(self.driver, 10).until(
            expected_conditions.visibility_of_element_located((By.CLASS_NAME, 'asset_table'))
        )
        product_html = self.driver.page_source
        filepath = self.save_html('product_page.html', product_html)
        logger.info('ScrapeProductPage success')
        return filepath

    @retry((exceptions.StaleElementReferenceException,
            exceptions.TimeoutException), tries=2, delay=3, logger=logger)
    def logout(self):
        WebDriverWait(self.driver, 10).until(
            expected_conditions.element_to_be_clickable((By.ID, 'logOut'))
        )
        logout_btn = self.driver.find_element(By.ID, 'logOut')
        logout_btn.click()

    def save_html(self, filename, source):
        filepath = os.path.join(self.base_dir, self.file_dir, filename)
        try:
            with open(filepath, 'w') as f:
                f.write(source)
            return filepath
        except FileNotFoundError as e:
            raise FileNotFoundError(e)
