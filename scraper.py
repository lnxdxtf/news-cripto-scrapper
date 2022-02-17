import json
import requests
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.service import Service
#from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.keys import Keys
#from os import path
import os
import time
from dotenv import load_dotenv
from selenium.webdriver.common.by import By

load_dotenv()

#main_folder = path.join(path.expanduser("~"), r"AppData\Local\Mozilla Firefox\firefox.exe")
#options = webdriver.FirefoxOptions()
#options.binary_location = main_folder

firefoxOptions = webdriver.FirefoxOptions()
firefoxOptions.log.level = "trace"
firefoxOptions.add_argument("-remote-debugging-port=9224")
firefoxOptions.add_argument("-headless")
firefoxOptions.add_argument("-disable-gpu")
firefoxOptions.add_argument("-no-sandbox")
firefoxBinaryENV = FirefoxBinary(os.getenv('FIREFOX_BIN'))

#urlAPP ="http://127.0.0.1:8000"
urlAPP = "https://cripto-service.herokuapp.com"
urlSCRAPTarget = "https://coinmarketcal.com/en/"

geckoDriverPath = os.getenv('GECKODRIVER_PATH')
serV = Service(geckoDriverPath)

class Scraper():
    def __init__(self):
        self.driver = webdriver.Firefox(service=serV,
                                        options=firefoxOptions,
                                        firefox_binary=firefoxBinaryENV,
                  
                                          )
    def start(self):
        self.driver.get(urlSCRAPTarget)
        self.criptoObjectList = []

    def startingSearch(self,coin):
        coin= coin.upper()
        try:
            time.sleep(3)
            inputSearch = self.driver.find_element(By.ID, 'form_keyword')
            inputSearch.clear()
            inputSearch.send_keys(coin)
            inputSearch.send_keys(Keys.RETURN)
            time.sleep(5)
            return self.getingNews(coin)
        except Exception as e:
            print(e)
            self.driver.quit()
    
    def getingNews(self, coin):
        articleCards = self.driver.find_elements(By.XPATH, "//*[@class='card__body']")
        
        #print(articleCards)
        for card in articleCards:
            coinSymbolName = card.find_element(By.XPATH,".//*[@class='card__coins']").find_element(By.XPATH,".//*[@class='link-detail']").text
            #print(coinSymbolName)
            eventDate = card.find_element(By.XPATH,".//*[@class='card__date mt-0']").text
            #print(eventDate)
            titleEvent = card.find_element(By.XPATH,".//*[@class='card__title mb-0 ellipsis']").text
            #print(titleEvent)
            content = card.find_element(By.XPATH,".//*[@class='card__description']").text
            #print(content)
            confident = card.find_element(By.XPATH,".//*[@class='progress__votes']").text
            #print(confident)
            sealList = []
            
            newNews = {
               "title":titleEvent,
               "criptoName":coinSymbolName,
               "symbol":coin,
               "content":content,
               "eventDate":eventDate,
               "confident":confident,
               "seal":sealList
           }
            self.criptoObjectList.append(newNews)

        #print(self.criptoObjectList)

    def disconnect(self):
        self.driver.quit()
        #print(self.criptoObjectList)
        objectNewsList = self.criptoObjectList
        return objectNewsList


def getCriptoUserGENERAL():
    allcriptosUSERS = []
    #urlAPP = "https://cripto-service.herokuapp.com"
    token = os.getenv('BEARER_TOKEN')
    getUsersURL = urlAPP+'/adm/users'
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(getUsersURL, headers=headers).json()
    for user in response:
        for coin in user['criptoCoins']:
            if coin in allcriptosUSERS:
                continue
            allcriptosUSERS.append(coin)
    return allcriptosUSERS

# TEST
def main():
    while True:
        scrp = Scraper()
        criptos = getCriptoUserGENERAL()
        scrp.start()
        for cripto in criptos:
            #print(cripto)
            scrp.startingSearch(cripto)
        objectNews = scrp.disconnect()
        #print(objectNews)

        urlPOST = urlAPP+'/cripto/new/news'

        for new in objectNews:
            newBody = json.dumps(new, indent=4)
            requests.post(urlPOST, newBody)
            print(f"NOTÍCIA ADICIONADA: {new['title']} -- {new['symbol']}")
        print(f"Número de notícias adicionadas: {len(objectNews)}")
        time.sleep(3600)
if __name__ == "__main__":
    main()