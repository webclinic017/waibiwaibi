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

import random

# listb = {1: '张三', 2: '李四', 3: '王五', 4: '赵六', 5: '王麻子', 6: '包子', 7: '豆浆'}
# lista = {1: '张三', 2: '李四', 3: '王五', 4: '赵六', 5: '王麻子', 6: '包子', 7: '豆浆'}
#
# for c in listb.keys():
#     a = random.sample(lista.keys(), 1)  # 随机一个字典中的key，第二个参数为限制个数
#     b = a[0]
#     print(lista[b]) # 打印随机抽取的值
#     del lista[b] # 删除已抽取的键值对
#     print(lista) # 打印剩余的键值对

activation_func_list = {'null': lambda x: x,
                        'relu': lambda x: x if x > 0 else 0,
                        'sigmoid': lambda x: 1 / (1 + (-x))}
print(random.sample(activation_func_list.keys(), 1))
