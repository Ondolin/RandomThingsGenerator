from aenum import Enum
import re
import random
import os

import yaml
from yaml import SafeLoader

from prompt_toolkit import PromptSession, prompt
from prompt_toolkit.completion import WordCompleter

from aenum import extend_enum

session = PromptSession()

f = open("table.txt", "r")
table = f.readlines()

# Open settings file
if not os.path.exists('settings.yaml'):
    open('settings.yaml', 'w').close()

stream = open('settings.yaml', 'r')
settings = yaml.load(stream, SafeLoader)

if settings == None:
    settings = dict()

def save_settings():
    global settings
    stream = open('settings.yaml', 'w')
    yaml.dump(settings, stream)

class TableType(str, Enum):
    _init_ = ""


completer = list()
def populate_enum():
    for line in table:
        if line.startswith("$"):
            extend_enum(TableType, str(line[1:-1]), line[1:-1])
            global completer
            completer.append(line[1:-1])

populate_enum()

def get_table_index(t: TableType):
    try:
        return table.index("$" + t + "\n")
    except:
        print("The table \"" + t + "\" was not found.")
        exit(1)

def quick_roll(l):
    return l[random.randint(0, len(l) - 1)]

def get_setting_variable_value(var):
    if var in settings:
        return settings[var]
    
    return prompt('Enter Variable value for \'' + var + "\': ")

def parse_int_or_variable(s):
    if s.isdigit():
        return int(s)
    return int(get_setting_variable_value(s)) # TODO dont brake

def roll_table(table_type: TableType, constrains: str | None):
    index = get_table_index(table_type)
    dice_size = int(table[index + 1])

    modifier = 0
    
    start = 1
    end = dice_size

    if constrains != None:
        for constrain in constrains.split(','):
            if constrain.startswith("<"):
                c = parse_int_or_variable(constrain[1:])
                if c <= dice_size:
                    end = c
            if constrain.startswith(">"):
                c = parse_int_or_variable(constrain[1:])
                if c >= start:
                    start = c
            if constrain.startswith("+"):
                c = parse_int_or_variable(constrain[1:])
                modifier += c
            if constrain.startswith("-"):
                c = parse_int_or_variable(constrain[1:])
                modifier -= c

    value = random.randint(start, end) + modifier

    if value < start:
        value = start
    elif value > end:
        value = end


    result = find_result(index + 2, value)

    quick_roll_rolls = re.findall(r"\§(.*)\§", result)
    for quick in quick_roll_rolls:
        result = re.sub("\§" + quick + "\§", quick_roll(quick.split(",")), result, 1)

    sub_rolls = re.findall(r"\$([^\$]*)\$", result)

    for roll in sub_rolls:
        
        constrains = re.match(r"(?:(?P<mult>\d*)\|)?(?P<t>[^\|]*)(?:\|(?P<con>.*))?", roll)

        c = constrains.groupdict()
        t = c["t"]
        con = c["con"]

        if c['mult'] == None:
            c['mult'] = 1

        s = list()
        
        while len(s) < int(c['mult']):
            r = roll_table(t, con)
            if not r in s:
                s.append(r)

        sub = ""
        for i in s:
            sub += i + ", "
        
        sub = sub[:-2]

        result = re.sub(re.escape("$" + roll + "$"), sub, result, 1)

        
    return result


def find_result(index, result):

    line_range_regex = r"(\d+)-(\d+)(\D.*)"
    line_regex = r"(\d+)(\D.*)"

    while index < len(table) and table[index] != "\n":
        m = re.match(line_range_regex, table[index])
        
        if m != None and int(m.group(1)) <= result and result <= int(m.group(2)):
            return m.group(3).strip()
        
        m = re.match(line_regex, table[index])

        if m != None and result == int(m.group(1)):
            return m.group(2).strip()
        
        index += 1

    print("Index out of bound!!")
    exit(1)

# Add contoll codes
completer.append("exit")
completer.append(".set")
completer.append(".get")
completer.append(".clear")

if __name__=="__main__":
    while True:
        text = session.prompt('Enter the table you want to roll: ', completer=WordCompleter(completer))
        if text in TableType:
            print()
            print(" > " + roll_table(text, None))
            print()
        if text == ".get":
            print(settings)
        if text.startswith(".set "):
            split = text.split(" ")
            if len(split) == 3:
                settings[split[1]] = split[2]
                save_settings()
            else:
                print("Set error!")
        if text == ".clear":
            settings = dict()
            save_settings()
        if text == "exit":
            exit(0)