import re
import logging
import asyncio
import requests
import traceback
from bs4 import BeautifulSoup
import crawler.utils.field_validator as fv
import crawler.config as config
from datetime import datetime


        


def _pega_hora_post(data_str:str, url_str:str) -> datetime:
    '''
        Retorna a data de publicação do produto, depois de tratar a string
    '''
    datetime_str = fv.validate_datetime_str(data_str)
    if (fv.has_valid_re(data_str)):
        pub_time = fv.validate_pub_time(data_str, datetime_str)
    else:
        logging.error(f"Não encontrou a data de publicação do produto: {url_str}/n{data_str}/n/n")
        return
    logging.debug(f'Data/hora de publicação: {pub_time}')
    
    return pub_time

def build_dict(detalhes, url_produto:str, page:str|int):
    '''
        Monta dicionario de cada item scrappado
    '''
    try:
        page_produto = requests.get(url_produto, headers=config.headers)
        soup_produto = BeautifulSoup(page_produto.content, "lxml")

        dados_str = str(soup_produto.find('script', {"id": "initial-data"}))
        data_hora_post = _pega_hora_post(dados_str, url_produto)
        
        async def search_and_extract(pattern:re.Pattern, string:str):
            match = re.search(pattern, string)
            return match.group() if match else ''
        async def run_searchs():
            tasks = [asyncio.create_task(search_and_extract(regex, dados_str)) for regex in config.regex_list]
            return await asyncio.gather(*tasks)                
        
        # guarda keys encontradas em variaveis
        titulo_anuncio, preco_post, cidade_post, bairro_post = asyncio.run(run_searchs())
        preco_post = float(preco_post.replace('.','')) if preco_post else 0.0
        estado_post = url_produto[8:10].upper()

        dict_produto = {'pagina': str(page) or '-',
                'titulo': titulo_anuncio or '-',
                'preco': preco_post or '-',
                'estado': estado_post or '-',
                'cidade': cidade_post or '-',
                'bairro': bairro_post or '-',
                'quilometragem (km)': detalhes[0].split(" ")[0] if detalhes != None else '-',
                'ano':detalhes[1].split(" ")[1] if (detalhes != None and len(detalhes) > 1)  else '-',
                'combustivel':detalhes[2].split(" ")[1]   if (detalhes != None and len(detalhes) > 2) else '-',
                'cambio':detalhes[3].split(" ")[1] if (detalhes != None and len(detalhes) > 3) else '-',
                'url': url_produto if len(url_produto) > 5 else '-',
                'data_publicacao': data_hora_post if data_hora_post != None else '-',
                'data_pesquisa': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        print(f"DICT PRODUTO {dict_produto}")
        return dict_produto
    
    except Exception:
        logging.error(traceback.format_exc())