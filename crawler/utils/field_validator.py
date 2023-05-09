
from datetime import datetime, timedelta
from crawler.utils.re_treater import get_res

def validate_datetime_str(data_str:str):
    first_re, second_re = get_res(data_str)
    return second_re if not first_re else first_re

def validate_pub_time(data_str:str, datetime_str):
    first_re, second_re = get_res(data_str)
    return  (
            datetime.fromtimestamp(int(datetime_str.group())) - timedelta(hours=3)
            if (not first_re and second_re)
            else datetime.fromisoformat(datetime_str.group()) - timedelta(hours=3)
        )

def has_valid_re(data_str):
    first_re, second_re = get_res(data_str)
    return first_re or (not first_re and second_re)