#!/usr/bin/env python3

from revChatGPT.revChatGPT import Chatbot
import json
import sys
import os
import subprocess


CONFIG_PATH = 'config.json'
# config = {
    # "session_token": "<SESSION_TOKEN>",
    # #"proxy": "<HTTP/HTTPS_PROXY>"
# }

# load it
with open(CONFIG_PATH, 'r') as f:
    config = json.load(f)

chatbot = Chatbot(config, conversation_id=None)


# response = chatbot.get_chat_response("Hello world", output="text")
# print(response)

filename = sys.argv[1]

# load the whole file
with open(filename, 'r') as f:
    file_content = f.read()



def find_target_line(lines):
    for i, line in enumerate(lines):
        line = line.strip()
        if line.startswith('##') and lines[i+1] == '':
            return i


def get_file_content_until_target_line(lines):
    target_line_index = find_target_line(lines)
    return lines[:target_line_index + 1]



def extract_instruction(line):
    return line[2:]

def generate_code(file_content_until_target_line, instruction):
    prompt = ''
    prompt += 'I want you to implement the part of the program that is specified in the instruction. Just reply with code and nothing else. Do not write any plain text. Only reply with the lines you want to add, do not repeat any existing parts of the program.\n\n'
    prompt += ''.join(file_content_until_target_line) + '\n\n'
    prompt += 'Instruction:' + instruction
    print("prompt:", prompt)
    response = chatbot.get_chat_response(prompt, output="text")
    print("response:", response)
    return response['message']


def insert_code(lines, code):
    print("lines:", lines)
    lines = lines.copy()
    target_line_index = find_target_line(lines)
    # lines[target_line_index] = code
    # insert it after the target line
    lines.insert(target_line_index + 1, code)
    return lines



def write_lines_to_file(lines):
    with open(filename, 'w') as f:
        f.write('\n'.join(lines))



def get_output(program):
    stderr = None
    stdout = None

    # Run the program and capture its output
    with open(os.devnull, "w") as devnull:
        try:
            # Get the stderr and the stdout of the program program.
            stdout = subprocess.check_output(
                program, stderr=subprocess.STDOUT, shell=True
            ).decode("utf-8")
        except subprocess.CalledProcessError as e:
            stderr = e.output.decode("utf-8")

    return stdout, stderr

## check if there is a dockerfile named Dockerfile in the current directory


    # if not dockerfile_in_dir:
        # import colored
        # print(colored.stylize("No Dockerfile found in the current directory. Running without docker which might be unsafe.", colored.fg("red")))


def add_indendation(code, lines):
    target_line_index = find_target_line(lines)
    indentation = lines[target_line_index].split('##')[0]
    code_lines = code.split('\n')
    code_lines = [indentation + line for line in code_lines]
    return '\n'.join(code_lines)




lines_original = file_content.splitlines()
if not find_target_line(lines_original):
    print("No target line found")
    sys.exit(0)
file_content_until_target_line = get_file_content_until_target_line(lines_original)
instruction = extract_instruction(file_content_until_target_line[-1])

for i in range(10):
    print("i:", i)
    code = generate_code(file_content_until_target_line, instruction)
    print('====================')
    print("code:", code)
    print('====================')
    code = add_indendation(code, lines_original)
    print('====================')
    print("code:", code)
    print('====================')

    lines = insert_code(lines_original, code)
    write_lines_to_file(lines)
    stdout, stderr = get_output('python3 ' + filename)
    print("stdout:", stdout)
    print("stderr:", stderr)
    if not stderr:
        break

    instruction = ''
    instruction += '\n\n'
    instruction += stderr
    instruction += '\n\n'
    instruction += 'Please fix the error above.'

