import os
import sys
import pandas as pd
from pyparsing import *


def get_commands():
    df = pd.read_csv('data/commands.csv', delimiter=',',
                     dtype=object, usecols=['Команды', 'Код команды'])
    # df = df.replace({'-': None})
    df = df.applymap(
        lambda s: s.lower() if type(s) == str else s
    )
    df['Код команды'] = df['Код команды'].apply(
        lambda v: '{:{fill}{width}x}'.format(int(v, 2), fill='0', width=len(v)//4)
    )
    df.set_index('Команды', inplace=True)
    return df['Код команды'].to_dict()


def get_gprs():
    df = pd.read_csv('data/gpr.csv', delimiter=',', dtype=object)
    df = df.applymap(
        lambda s: s.lower() if type(s) == str else s
    )
    df['Код регистра'] = df['Код регистра'].apply(
        lambda v: '{:x}'.format(int(v, 2))
    )
    return df['Код регистра'].to_dict()


def parse_code(fn: str):
    with open(fn, 'r', encoding='utf8') as content_file:
        lines = content_file.read().strip().lower().split("\n")

    commands = get_commands()
    gprs = get_gprs()

    comment = Regex(r";.*")
    c_name = Word(alphas)
    gpr_name = Word(alphas, nums)
    memory_address = Word(hexnums, exact=4)
    c_arg = (memory_address | gpr_name)
    command = c_name + Optional(delimitedList(c_arg))
    bgasm_line = Optional(command)
    bgasm_line.ignore(comment)

    out = str()
    for i in range(len(lines)):
        parse_res = bgasm_line.parseString(lines[i]).asList()
        n = len(parse_res)
        if n == 0:
            continue
        arg0 = parse_res[0]
        line = commands[arg0]
        if n == 2:
            arg1 = parse_res[1]
            arg1 = gprs[arg1] if arg1 in gprs else arg1
            line += arg1
        if n == 3:
            arg1 = parse_res[1]
            arg2 = parse_res[2]
            arg1 = gprs[arg1] if arg1 in gprs else arg1
            arg2 = gprs[arg2] if arg2 in gprs else arg2
            line += arg1 + arg2
        # line = '{message:{fill}{align}{width}}'.format(
        #     message=line,
        #     fill='0',
        #     align='<',
        #     width=6,
        # )
        out += '0x' + line + '\n'

    return out


def main(argv, argc) -> None:
    if argc != 2:
        return
    fn, fext = os.path.splitext(argv[1])
    fext = '.bgasm' if fext == '' else fext
    code = parse_code(fn + fext)
    with open(fn + '.binastxt', 'w', encoding='utf8') as out:
        out.write(code)
    return


if __name__ == '__main__':
    main(sys.argv, len(sys.argv))
