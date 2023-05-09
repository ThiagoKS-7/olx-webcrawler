import logging
import traceback
import pandas as pd
from contexttimer import Timer  
from crawler.utils.search_handler import search
from crawler.utils.thread_runner import run_thread
import crawler.config as config


MAX_PAGES = 1

def pega_lista(max_pages:str=MAX_PAGES):
    '''
        Roda loop do scrapper por pagina
    '''
    found_page = False
    for page in range(1, max_pages+1):
        found_page = search(page, config.headers)
        if not found_page: break
    return config.lista_produtos


def run():
    try:
        with Timer() as t:
            df_lista = pd.DataFrame(data=pega_lista())
            df_lista.to_csv("./results.csv", index=False,encoding="utf-8")
            logging.info(f'Tempo total das buscas: {t.elapsed}s')
    except:
        logging.error(traceback.format_exc())