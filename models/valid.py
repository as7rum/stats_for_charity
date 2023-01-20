import re 
from datetime import datetime, date

def is_valid(pattern, input: str):
    valid = re.compile(pattern, re.U)
    valid_match = valid.match(input)
    try:
        return valid_match.group(1), valid_match.group(2), valid_match.group(3)
    except:
        return valid_match

def valid_date(dd: int, mm: int, yyyy: int) -> bool:
    if 1<=int(dd)<=31 and 1<=int(mm)<=12 and 1970<=int(yyyy)<=2022:
        return not not dd

def age(birthdate: str) -> int:
    try:
        today = date.today()
        birthdate = datetime.strptime(birthdate, '%d.%m.%Y').date()
        one_or_zero = ((today.month, today.day) < (birthdate.month, birthdate.day))
        year_difference = today.year - birthdate.year
        return year_difference - one_or_zero
    except:
        return


# print(valid_date(*(is_valid(r'^(\d{2})\.(\d{2})\.(\d{4})$', '32.10.1998'))))
# print(is_valid(r'^(\d{2})\.(\d{2})\.(\d{4})$', '22.10.1998'))
# print(type(age('22.10.1998')))
# print(age('22.10.1998'))