import os
import re
import sys
import locale
import asyncio
import logging
import requests
import traceback
import subprocess
import pandas as pd
import concurrent.futures   
from bs4 import BeautifulSoup
from contexttimer import Timer  
from datetime import datetime, timedelta

MAX_PAGES = 10


def configure_defaults() -> None:
    '''
        Roda configurações de locale e timezone
    '''
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    logging.getLogger("urllib3.connectionpool").setLevel(logging.INFO)
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def install_requirements(requirements_file) ->None:
    '''
        Instala requirements
    '''
    subprocess.check_output([sys.executable, "-m", "pip", "install", "-r", requirements_file])
    
    
    
class OlxScrapper():
    def __init__(self, lista_produtos=[], headers={}) -> None:
       self.lista_produtos = lista_produtos
       self.headers =  {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}

    def run(self,max_pages:str=MAX_PAGES):
        '''
            Roda loop do scrapper por pagina
        '''

        found_page = False
        for page in range(1, max_pages+1):
            found_page = self.search(page, self.headers)
            if not found_page: break
        return self.lista_produtos
    
    def search(self, page:str|int, headers:str):
        '''
            Chama a ThreadPool responsavel pelas requests e salva resultados na lista
        '''
        
        
        url = 'https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios?o='+str(page)
        
        request = requests.get(url, headers=headers)
        soup = BeautifulSoup(request.content, "lxml") #"html.parser"
        produtos = soup.find('ul', {"id": ["ad-list"]})
        if produtos == None or len(produtos)== 0:
            logging.info(f'\t\t\tNenhum resultado na página {str(page)}')
            return False
        produtos = produtos.findAll('li',recursive=False)
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for produto in produtos:
                produto:BeautifulSoup

                try:
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

                executor.submit(self._append_prod_list, url_produto,page) # Executa paralelizado
        return True
    
    def _append_prod_list(self, url_produto:str, page:str|int):
        self.lista_produtos.append(self._build_dict(url_produto,page))

    def _build_dict(self, url_produto:str, page:str|int):
        '''
            Monta dicionario de cada item scrappado
        '''
        try:
            page_produto = requests.get(url_produto, headers=self.headers)
            soup_produto = BeautifulSoup(page_produto.content, "lxml")

            dados_str = str(soup_produto.find('script', {"id": "initial-data"}))
            if dados_str.find('&quot;'):
                dados_str = dados_str.replace('&quot;','"')
            datetime_str = re.search(r'(?<="listTime":").*?(?=.000Z")',dados_str)

            if datetime_str:                
                data_hora_post = datetime.fromisoformat(datetime_str.group()) - timedelta(hours=3)
            if not datetime_str:
                datetime_str = re.search(r'(?<=origListTime":).*?(?=,)', dados_str)
                if datetime_str:
                    data_hora_post = datetime.fromtimestamp(int(datetime_str.group())) - timedelta(hours=3)
                else:
                    logging.error(f"Não encontrou a data de publicação do produto: {url_produto}/n{dados_str}/n/n")
                    return
            logging.debug(f'Data/hora de publicação: {data_hora_post}')

            regex_list = [
                r'(?<=\"subject\":\").*?(?=\")',
                r'(?<=\"price\":\"R\$ ).*?(?=\")',
                r'(?<=\"Município\",\"value\":\").*?(?=\")',
                r'(?<=\"Bairro\",\"value\":\").*?(?=\")'
            ]
            async def search_and_extract(pattern:re.Pattern, string:str):
                match = re.search(pattern, string)
                return match.group() if match else ''
            async def run_searchs():
                tasks = [asyncio.create_task(search_and_extract(regex, dados_str)) for regex in regex_list]
                return await asyncio.gather(*tasks)                
            titulo_anuncio, preco_post, cidade_post, bairro_post = asyncio.run(run_searchs())

            preco_post = float(preco_post.replace('.','')) if preco_post else 0.0
            estado_post = url_produto[8:10].upper()

            dic_produtos = {'pagina': str(page),
                            'titulo': titulo_anuncio,
                            'preco': preco_post,
                            'estado': estado_post,
                            'cidade': cidade_post,
                            'bairro': bairro_post,
                            'url': url_produto,
                            'data_publicacao': data_hora_post,
                            'data_pesquisa': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            return dic_produtos

        except Exception:
            logging.error(traceback.format_exc())

    

requirements_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),"requirements.txt")
configure_defaults()
install_requirements(requirements_file)



if __name__ == '__main__':
    
    try:
        with Timer() as t:
            df_lista = pd.DataFrame(data=OlxScrapper().run())
            df_lista.to_csv("./results.csv", index=False,encoding="utf-8")
            logging.info(f'Tempo total das buscas: {t.elapsed}s')
    except:
        logging.error(traceback.format_exc())