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

with open('parameter.json', 'r') as json_open:
    parameter_object = json.load(json_open)

binName = 'fireworks-robot'
binPath = 'BUILD/NUCLEO_F303K8/ARMC6/'

remove_glob(binPath + '*.bin')
compile_fail_list = []

for robot in json_object['robot']:

    data_lines = []

# moveの設定
    data_lines.append('#define MOVE_LENGTH ' + str(len(robot['move'])) + '\n')

    move_string = '{'
    for direction in robot['move']:
        move_string += '"' + direction + '",'
    move_string = move_string.rstrip(',')
    move_string += '}'
    data_lines.append('#define REPLACE_MOVE ' + move_string + '\n')

# colorの設定
    data_lines.append('#define COLOR_LENGTH ' +
                      str(len(robot['color'])) + '\n')

    color_string = '{'
    for data in robot['color']:
        color_string += '{'
        for element in data:
            color_string += str(element) + ','
        color_string = color_string.rstrip(',')
        color_string += '},'
    color_string = color_string.rstrip(',')
    color_string += '}'
    data_lines.append('#define REPLACE_COLOR ' + color_string + '\n')


# その他
    if str(robot['number']) in parameter_object:
        parameter = parameter_object[str(robot['number'])]
    else:
        parameter = parameter_object['default']

    data_lines.append('#define COLOR_THRESHOLD ' +
                      str(parameter['colorThreshold']) + 'f\n')

    data_lines.append('#define TURN_LEFT_WHEEL_LEFT_PWM ' +
                      str(parameter['turnLeftWheelLeftPwm']) + 'f\n')

    data_lines.append('#define TURN_LEFT_WHEEL_RIGHT_PWM ' +
                      str(parameter['turnLeftWheelRightPwm']) + 'f\n')

    data_lines.append('#define TURN_LEFT_SLEEP_MS ' +
                      str(parameter['turnLeftSleepMs']) + 'ms\n')

    data_lines.append('#define TURN_RIGHT_WHEEL_LEFT_PWM ' +
                      str(parameter['turnRightWheelLeftPwm']) + 'f\n')

    data_lines.append('#define TURN_RIGHT_WHEEL_RIGHT_PWM ' +
                      str(parameter['turnRightWheelRightPwm']) + 'f\n')

    data_lines.append('#define TURN_RIGHT_SLEEP_MS ' +
                      str(parameter['turnRightSleepMs']) + 'ms\n')

    with open('UniqueValue.h', mode='w') as f2:
        f2.writelines(data_lines)

    subprocess.run(
        ['mbed', 'compile', '-m', 'NUCLEO_F303K8', '-t' 'ARMC6'], shell=True)

    if os.path.exists(binPath + binName + '.bin'):
        os.rename(binPath + binName + '.bin',
                  binPath + binName + str(robot['number']) + '.bin')

    if os.path.exists(binPath + binName + str(robot['number']) + '.bin'):
        print('ロボット' + str(robot['number']) + 'のコンパイルに成功しました\n')
    else:
        print('ロボット' + str(robot['number']) + 'のコンパイルに失敗しました\n')
        compile_fail_list.append(robot['number'])

print('\nすべてのコンパイルが終了しました')

if not len(compile_fail_list) == 0:
    print('コンパイルに失敗したリスト:{}'.format(compile_fail_list))
