from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import requests
import re
import cv2
from skimage import io

def get_keyword_html_table(keyword):
    driver = webdriver.Chrome()
    driver.get("http://image-net.org/")

    elem = driver.find_element_by_name('q')
    elem.clear()
    elem.send_keys(keyword)
    elem.send_keys(Keys.RETURN)

    source = driver.find_element_by_class_name('search_result')
    return source.get_attribute('innerHTML')

def get_wnids(source):
    matches = re.findall('(synset\?wnid=n[\d]{8})', source)

    unique_wnids = set()

    for match in matches:
        re1 = re.search('n[\d]{8}', match)
        unique_wnids.add(re1.group())

    return list(unique_wnids)

def get_split_urls_from_wnids(unique_wnids, test_size = 0.8):
    uri_prefix = 'http://www.image-net.org/api/text/imagenet.synset.geturls?wnid='

    train_urls, test_urls = [], []

    for wnid in unique_wnids:
        page = requests.get(f'{uri_prefix}{wnid}')
        uri_list = page.text.split('\r\n')

        split_index = int(len(uri_list) * test_size)

        train_urls.extend(uri_list[:split_index])
        test_urls.extend(uri_list[split_index:])

    return list(set(train_urls)), list(set(test_urls))

def get_image_name(url):
    return url.rsplit('/', 1)[-1]

def download_urls_in_foler(folder_name, urls, max_files = -1):
    stored = 0
    for url in urls:
        if stored <= max_files or max_files == -1:
            try:
                img = io.imread(url)
                cv2.imwrite(f'./{folder_name}/{get_image_name(url)}', cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
                stored = stored + 1
            except Exception:
                pass


html = get_keyword_html_table('dog')
wnids = get_wnids(html)
train_urls, test_urls = get_split_urls_from_wnids(wnids)

download_urls_in_foler('train', train_urls)
download_urls_in_foler('test', test_urls)
