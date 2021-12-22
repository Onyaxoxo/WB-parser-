import requests
import bs4
import logging
import collections  # namedtuple
import csv

# конфиг логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('wb')

ParseResult = collections.namedtuple(
    'ParseResult',
    (
        'brand_name',
        'goods_name',
        'url',
    ),
)

HEADERS = (
    'Бренд',
    'Товар',
    'Ссылка',
)

class Client:

    def __init__(self):
        # session для сохраниения состояния cookies/заголовков
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/5 37.36 (KHTML, like Gecko) '
                          'Chrome/89.0.4389.82 Safari/537.36',
            'Accept-Language': 'ru',
        }
        # список для сохранения в файл
        self.result = []

    # метод для загрузки страницы
    def load_page(self, page: int = None):
        url = 'https://www.wildberries.ru/catalog/aksessuary/golovnye-ubory'
        # скачиваем страницу
        res = self.session.get(url=url)
        # проверка статуса кода ответа
        res.raise_for_status()
        return res.text  # возвращаем текст стрницы в HTML

    # метод парсинга страницы
    def parse_page(self, text: str):
        soup = bs4.BeautifulSoup(text, 'lxml')
        container = soup.select('div.dtList.i-dtList.j-card-item')
        for block in container:
            self.parse_block(block=block)

    # принимает не сырой текст, а объект bs4
    def parse_block(self, block):
        url_block = block.select_one('a.ref_goods_n_p.j-open-full-product-card')
        if not url_block:
            logger.error('no url_block')
            return

        # достаем атрибут блока (ссылка)
        url = url_block.get('href')
        # href = url.get('href')
        # if href:
        #     url = 'https://www.wildberries.ru/ + href'

        if not url:
            logger.error('no href')
            return
        # блок названия
        name_block = block.select_one('div.dtlist-inner-brand-name')
        if not name_block:
            logger.error(f'no name_block on {url}')
            return
        # бренд
        brand_name = name_block.select_one('strong.brand-name.c-text-sm')
        if not brand_name:
            logger.error(f'no brand_name on url {url}')
            return
        # Wrangler /
        brand_name = brand_name.text
        brand_name = brand_name.replace('/', '').strip()

        # название продукта
        goods_name = name_block.select_one('span.goods-name.c-text-sm')
        if goods_name:
            logger.error(f'no goods_name on {url}')
            return

        goods_name = goods_name.text.strip()

        self.result.append(ParseResult(
            url=url,
            brand_name=brand_name,
            goods_name=goods_name,
        ))

        logger.debug('%s, %s', '$s', url, brand_name, goods_name)
        logger.debug('- ' * 100)

    def run(self):
        text = self.load_page()
        self.parse_page(text=text)
        logger.info(f'Получено результатов: {len(self.result)} ')

    def save_results(self):
        path = 'D:\Google Drive\PyCharm\Parsing\wb.csv'
        with open(path, 'w') as f:
            writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
            writer.writerow(HEADERS)
            for item in self.result:
                writer.writerow(item)

# запуск проверки
if __name__ == '__main__':
    parser = Client()
    parser.run()
