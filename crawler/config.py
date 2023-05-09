lista_produtos = []
headers =  {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}
url = 'https://www.olx.com.br/autos-e-pecas/carros-vans-e-utilitarios?o='
regex_list = [
    r'(?<=\"subject\":\").*?(?=\")',
    r'(?<=\"price\":\"R\$ ).*?(?=\")',
    r'(?<=\"Município\",\"value\":\").*?(?=\")',
    r'(?<=\"Bairro\",\"value\":\").*?(?=\")'
]