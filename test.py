# @ last edit time 2021/11/5 10:39

from mak_sqlite import list_to_str, list_to_str_no_quote

list_num = [123, 12.45]
list_str = ['asf', 'reyr']
list_mix = list_num + list_str

print(list_num)
print(list_to_str(list_num))
print(list_to_str_no_quote(list_num))
print(f'in str {list_num}')
print(f'in str {list_to_str(list_num)}')
print(f'in str {list_to_str_no_quote(list_num)}')

print(list_str)
print(list_to_str(list_str))
print(list_to_str_no_quote(list_str))
print(f'in str {list_str}')
print(f'in str {list_to_str(list_str)}')
print(f'in str {list_to_str_no_quote(list_str)}')

print(list_mix)
print(list_to_str(list_mix))
print(list_to_str_no_quote(list_mix))
print(f'in str {list_mix}')
print(f'in str {list_to_str(list_mix)}')
print(f'in str {list_to_str_no_quote(list_mix)}')



