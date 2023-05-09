import re

def _get_treated(data_str:str):
    return data_str.replace('&quot;','"') if data_str.find('&quot;') else data_str

def get_res(data_str:str):
    first_re = re.search(r'(?<="listTime":").*?(?=.000Z")',_get_treated(data_str))
    second_re = re.search(r'(?<=origListTime":).*?(?=,)', _get_treated(data_str))
    return first_re, second_re