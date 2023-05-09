import re
import logging
import concurrent.futures   
from bs4 import BeautifulSoup
import crawler.config as config 
from crawler.utils.dict_builder import build_dict

def append_prod_list( detalhes, url_produto:str, page:str|int):
    '''
        Salva resultado da request  lista
    '''
    config.lista_produtos.append(build_dict(detalhes, url_produto, page))

def run_thread(produtos, page):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for produto in produtos:
            produto:BeautifulSoup
            try:
                detalhes = [i.find("span")["aria-label"] or '-' for i in produto.find("ul", {"aria-label": "detalhes do anúncio"})]                    
                url_produto = produto.find("a")["href"]
            except TypeError:
                logging.debug(f"URL nao encontrada em: \n{produto}\n\n")
                continue

            try:
                titulo_anuncio = produto.findAll("h2")[0].contents[0]
                titulo_anuncio = re.sub(r'<.*>', '', titulo_anuncio).rstrip()
                logging.info(f'\tPÁGINA {str(page)} - Título: {titulo_anuncio}') 
            except TypeError:
                logging.info(f"Título não encontrado na página")
            executor.submit(append_prod_list, detalhes,url_produto,page) # Executa paralelizado
    return True