from os import devnull, replace
import os.path
import subprocess
import json
import glob
import sys


def remove_glob(pathname, recursive=True):
    for p in glob.glob(pathname, recursive=recursive):
        if os.path.isfile(p):
            os.remove(p)


json_file_name = "default.json"

if (len(sys.argv) == 2):
    json_file_name = sys.argv[1]

with open(json_file_name, 'r') as json_open:
    json_object = json.load(json_open)

with open('UniqueValue.h', mode='w') as f2:
    print("Init")

binName = 'fireworks-robot'
binPath = 'BUILD/NUCLEO_F303K8/ARMC6/'

remove_glob(binPath + '*.bin')
compile_fail_list = []

with open('UniqueValue.h', mode='r', encoding='utf_8') as f:
    # original_file = f.read()
    original_file_line = f.readlines()
    for i in range(len(json_object['robot'])):
        robot = json_object['robot'][i]

        data_lines = ['#define MOVE_LENGTH @\n', '#define REPLACE_MOVE @\n',
                      '#define COLOR_LENGTH @\n', '#define REPLACE_COLOR @\n']

        data_lines[0] = data_lines[0].replace('@', str(len(robot['move'])))

        move_string = '{'
        for direction in robot['move']:
            move_string += '"' + direction + '",'
        move_string = move_string.rstrip(',')
        move_string += '}'
        data_lines[1] = data_lines[1].replace('@', move_string)

        data_lines[2] = data_lines[2].replace('@', str(len(robot['color'])))

        color_string = '{'
        for data in robot['color']:
            color_string += '{'
            for element in data:
                color_string += str(element) + ','
            color_string = color_string.rstrip(',')
            color_string += '},'
        color_string = color_string.rstrip(',')
        color_string += '}'
        data_lines[3] = data_lines[3].replace('@', color_string)

        with open('UniqueValue.h', mode='w') as f2:
            f2.writelines(data_lines)

        subprocess.run(
            ['mbed', 'compile', '-m', 'NUCLEO_F303K8', '-t' 'ARMC6'], shell=True)

        if os.path.exists(binPath + binName + '.bin'):
            os.rename(binPath + binName + '.bin',
                      binPath + binName + str(i) + '.bin')

        if os.path.exists(binPath + binName + str(i) + '.bin'):
            print('ロボット' + str(i) + 'のコンパイルに成功しました')
        else:
            print('ロボット' + str(i) + 'のコンパイルに失敗しました')
            compile_fail_list.append(i)

print('すべてのコンパイルが終了しました')

if not len(compile_fail_list) == 0:
    print('コンパイルに失敗したリスト:{}'.format(compile_fail_list))
