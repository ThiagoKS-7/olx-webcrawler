import logging
import requests
from bs4 import BeautifulSoup
from crawler.utils.thread_runner import run_thread
import crawler.config as config

def search(page:str|int, headers:str):
    '''
        Chama a ThreadPool responsavel pelas requests e salva resultados na lista
    '''
    
    url = config.url+str(page)
    request = requests.get(url, headers=headers)
    soup = BeautifulSoup(request.content, "lxml") #"html.parser"
    produtos = soup.find('ul', {"id": ["ad-list"]})
    if produtos == None or len(produtos)== 0:
        logging.info(f'\t\t\tNenhum resultado na página {str(page)}')
        return False
    produtos = produtos.findAll('li',recursive=False)
    run_thread(produtos,page)