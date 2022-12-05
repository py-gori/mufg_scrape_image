import logging.config
from bs4 import BeautifulSoup

from models.model_exceptions import ExtractModelException
from settings import settings

try:
    logging.config.dictConfig(settings.log_config)
except AttributeError:
    print(settings.log_config)
    logging.basicConfig(level=logging.WARN)

logger = logging.getLogger(__name__)


class MufgExtract:
    def __init__(self, main_html, product_html):
        self.main_soup = self.html_to_soup(main_html)
        self.product_soup = self.html_to_soup(product_html)

    def html_to_soup(self, html):
        with open(html, 'r') as f:
            source = f.read()
        return BeautifulSoup(source, 'html.parser')

    def extract_main(self):
        yields = self.main_soup.find(id='reviewGroup03').find('span').string.strip()
        valuation = self.main_soup.find(id='assetBlanceInfo').find_all('tr')[1].find_all('em')[0].string.strip()
        contribution_amount = self.main_soup.find(id='assetBlanceInfo').find_all('tr')[1].find_all('em')[1].string.strip()
        gain_loss = self.main_soup.find(id='assetBlanceInfo').find_all('tr')[1].find_all('em')[2].string.strip()
        all_data = {
            'yields': yields,
            'valuation': valuation,
            'contribution_amount': contribution_amount,
            'gain_loss': gain_loss,
        }
        logger.info(f'all data: {all_data}')
        return all_data

    def extract_products(self):
        asset_table = self.product_soup.find(class_='asset_table')
        product_elems = asset_table.find_all('a')
        products = []
        for elem in product_elems:
            product_name = elem.string.strip()
            products.append({
                'product_name': product_name,
            })

        products_info = asset_table.find_all('em')
        for i in range(len(products)):
            products[i]['valuation'] = products_info[(i*4)].string.strip()
            products[i]['contribution_amount'] = products_info[(i*4)+1].string.strip()
            products[i]['gain_loss'] = products_info[(i*4)+2].string.strip()
            products[i]['gain_loss_rate'] = products_info[(i*4)+3].string.strip()
        logger.info(f'products data: {products}')
        return products
