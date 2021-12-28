from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
import datetime
import requests
import pandas as pd
import sys
import time


def get_html_from_selennium():
    '''Open site,agree disclaimer,click search take url and click next page '''
    driver = webdriver.Firefox()
    driver.get('https://www.eaa.labour.gov.hk/en/search.html') #GO to webside
    time.sleep(5)
    driver.find_element_by_id('button-i-accept').click() # Accept disclaimer alert
    time.sleep(5)
    driver.find_element_by_id('button-i-accept').click() # Accept disclaimer alert
    time.sleep(5)
    driver.find_element_by_id('listAllBtn').click() # Click Search
    time.sleep(5)
    print('Starting collecting url...')
    urls = []
    switch = True
    while switch == True:
        try:
            list_url = driver.find_elements_by_class_name('result')
            for x in list_url:
                urls.append(x.find_element_by_class_name('button-default').get_attribute('href'))
            WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//*[@title='Next Page']"))).click() # Click next page
            time.sleep(2)
        except:
            switch = False
    driver.quit()
    return urls

def get_cookies():
    '''Get fresh cookies'''
    url = 'https://www.eaa.labour.gov.hk/en/search.html'
    cookies = session.post(url, headers=HEADERS, data=PARAMS, timeout=10).cookies
    return cookies


HEADERS = {
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0',
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
'Accept-Language': 'en-US,en;q=0.5',
'Accept-Encoding':'gzip, deflate, br',
'Content-Type': 'application/x-www-form-urlencoded',
'Content-Length': '217',
'Origin': 'https://www.eaa.labour.gov.hk',
'DNT': '1',
'Connection': 'keep-alive',
'Referer': 'https://www.eaa.labour.gov.hk/en/result.html',
'Upgrade-Insecure-Requests': '1',
'Sec-Fetch-Dest': 'document',
'Sec-Fetch-Mode': 'navigate',
'Sec-Fetch-Site': 'same-origin',
'Sec-Fetch-User': '?1',
'TE': 'trailers'}
PARAMS = 'en-name=&tc-name=&sc-name=&en-addr=&tc-addr=&sc-addr=&tel-no=&fax-no=&email=&types=&region=&location=&district=&search=SQ&filter-by=&page-no=1&row-per-page=10&sort-by=EN_NAME_ASC'
DATA = []
LINKS = get_html_from_selennium()

session = requests.session() #Create seesions
cookies = get_cookies()

i = 0
start_timer = datetime.datetime.now()
for link in LINKS:
    i+=1
    sys.stdout.write(f"\r Parse company {i} for {len(LINKS)}")
    sys.stdout.flush()
    c = True
    while c == True:
        try:
            page = session.post(link, headers=HEADERS, cookies=cookies, data=PARAMS, timeout=10).text
            soup = BeautifulSoup(page,features='lxml')
            table = soup.find('div',class_='main-content').find_all('p')
            try:
                e_name = soup.find('h2',class_='en-name').text
            except:
                e_name = ''
            try:
                c_name = soup.find('h2',class_='chi-name').text
            except:
                c_name = ''
            valid_since = table[1].text
            distr = table[3].text
            address = table[5].text
            tel = table[7].text
            fax = table[9].text
            email = table[11].text
            p_type = table[13].text
            DATA.append({
                'English Company Name':e_name,
                'Chinese Company Name':c_name,
                'Valid Licence since':valid_since,
                'District':distr,
                'Address':address,
                'Telephone No':tel,
                'FAX':fax,
                'Email':email,
                'Placement Type':p_type
            })
            c = False
        except:
            cookies = get_cookies()

df = pd.DataFrame(DATA)
df.to_csv('Employment_Agency_Data_'+datetime.datetime.now().strftime('%d_%m_%y')+'.csv')
print('Time work -- ',datetime.datetime.now()-start_timer)

