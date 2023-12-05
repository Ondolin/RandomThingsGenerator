from aenum import Enum
import re
import random
import os

import yaml
from yaml import SafeLoader

from prompt_toolkit import PromptSession, prompt
from prompt_toolkit.completion import WordCompleter

from aenum import extend_enum

from functools import reduce
from copy import deepcopy

from os import walk

session = PromptSession()

table: list[str] = []

def add_table(path, file):
    f = open(path + "/" + file, "r")
    global table
    table += f.readlines()
    table += 2 * ["\n"]

for (dirpath, dirnames, filenames) in walk("./tables"):
    for file in filenames:
        if file.endswith(".txt"):
            add_table(dirpath, file)

# Open settings file
if not os.path.exists('settings.yaml'):
    open('settings.yaml', 'w').close()

stream = open('settings.yaml', 'r')
global_settings = yaml.load(stream, SafeLoader)

if global_settings == None:
    global_settings = dict()

def save_settings():
    global global_settings
    stream = open('settings.yaml', 'w')
    yaml.dump(global_settings, stream)

class TableType(str, Enum):
    _init_ = ""

completer = list()
def populate_enum():
    for line in table:
        if line.startswith("$"):
            r = re.sub(r"\[.*\]", "", line)
            extend_enum(TableType, str(r[1:-1]), r[1:-1])
            global completer
            completer.append(r[1:-1])

populate_enum()

# Get the index for a table form the table.tex
def get_table_index(t: TableType):
    for i, row in enumerate(table):
        if row == "$" + t + "\n" or row.startswith("$" + t + "["):
            return i
        
    print("The table \"" + t + "\" was not found.")
    exit(1)

def get_setting_variable_value(var, settings):
    if var in settings:
        return settings[var]
    
    return prompt('Enter Variable value for \'' + var + "\': ")

def parse_int_or_variable(s, settings):
    if s.isdigit():
        return int(s)
    return int(get_setting_variable_value(s, settings)) # TODO dont brake

def get_local_variable_name(index):
    variable = re.match(r".*\[(\D*)\]", table[index])
    if variable != None:
        return variable.group(1)
    return None

# Roll for a value of a table
def roll_table(table_type: TableType, constrains: str | None, settings: dict):

    index = get_table_index(table_type)
    dice_size = int(table[index + 1])

    modifier = 0
    
    start = 1
    end = dice_size

    if constrains != None:
        for constrain in constrains.split(','):
            if constrain.startswith("<"):
                c = parse_int_or_variable(constrain[1:], settings)
                if c <= dice_size:
                    end = c
            if constrain.startswith(">"):
                c = parse_int_or_variable(constrain[1:], settings)
                if c >= start:
                    start = c
            if constrain.startswith("+"):
                c = parse_int_or_variable(constrain[1:], settings)
                modifier += c
            if constrain.startswith("-"):
                c = parse_int_or_variable(constrain[1:], settings)
                modifier -= c

    value = random.randint(start, end) + modifier

    if value < start:
        value = start
    elif value > end:
        value = end


    result = find_result(index + 2, value)
    
    local_variable_name = get_local_variable_name(index)

    if local_variable_name != None and "inputvariable" in settings:
        result = re.sub("\\b" + local_variable_name + "\\b", settings["inputvariable"], result)

    # inline roll mechanic
    quick_roll_rolls = re.findall(r"\§(.*)\§", result)
    for quick in quick_roll_rolls:
        dice = re.match(r"(\d*)d(\d*)", quick)
        roll = ""
        if dice != None: # dice roll
            roll = str(reduce(lambda x, y: x + y, [random.randint(1, int(dice.group(2))) for _ in range(int(dice.group(1)))]))
        else: # Split roll
            split = quick.split(",")
            roll = split[random.randint(0, len(split) - 1)]

        result = re.sub("\§" + quick + "\§", roll, result, 1)

    sub_rolls = re.findall(r"\$([^\$]*)\$", result)

    for roll in sub_rolls:
        
        constrains = re.match(r"(?:(?P<mult>\d*)\|)?(?P<t>[^\|]*)(?:\|(?P<con>.*))?", roll)

        c = constrains.groupdict() # How often roll
        t = c["t"] # Table Name
        con = c["con"] # condition

        if c['mult'] == None:
            c['mult'] = 1

        s = list()
        
        while len(s) < int(c['mult']):
            
            settings_copy = deepcopy(settings)
            spl = t.split(";")
            if len(spl) > 1:
                t = spl[0]
                settings_copy["inputvariable"] = spl[1]

            r = roll_table(t, con, settings_copy)
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

        local_variable = text.split(";")
        
        settings = deepcopy(global_settings)
        if len(local_variable) > 1:
            text = local_variable[0]
            settings["inputvariable"] = local_variable[1]

        if text in TableType:
            print()
            print(" > " + roll_table(text, None, settings))
            print()
        if text == ".get":
            print(global_settings)
        if text.startswith(".set "):
            split = text.split(" ")
            if len(split) == 3:
                global_settings[split[1]] = split[2]
                save_settings()
            else:
                print("Set error!")
        if text == ".clear":
            global_settings = dict()
            save_settings()
        if text == "exit":
            exit(0)