import os
import sys
import locale
import logging
import crawler

def configure_defaults() -> None:
    '''
        Roda configurações de locale e timezone
    '''
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    logging.getLogger("urllib3.connectionpool").setLevel(logging.INFO)
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

requirements_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),"requirements.txt")    



configure_defaults()
os.system(f"{sys.executable} -m pip install -r {requirements_file}")

if __name__ == "__main__":
    crawler.run()