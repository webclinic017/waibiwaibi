# @ last edit time 2022/1/27 16:46

import importlib


def dict_save(dir_dict: str, data: dict):
    fp = open(dir_dict, 'w')
    fp.write('\ndata = ')
    depth = 0
    for char in str(data):
        if char == ',':
            fp.write(',\n' + '    ' * depth)
        elif char in ['{', '[', '(']:
            depth += 1
            fp.write(char)
            fp.write('\n' + '    ' * depth)
        elif char in [']', '}', ')']:
            depth -= 1
            fp.write(char)
        elif char == ':':
            fp.write(': ')
        elif char == ' ':
            pass
        else:
            fp.write(char)

    fp.write('\n')
    fp.close()


def dict_load(dir_dict: str):
    dir_dict = dir_dict[:-3].replace('/', '.')
    print(dir_dict)
    return importlib.import_module(dir_dict).data


if __name__ == '__main__':
    dd = {'a': 123, 'b': {'c': 'cc', 'd': [1, 2]}, 2: 246}
    print(str(dd))
    dict_save('dict_test.py', dd)
    print(dict_load('dict_test.py'))



