import os
import json
import shutil
from subprocess import PIPE, run
import sys

GAME_DIR_PATTERN = "game"
GAME_CODE_EXTENSION = ".go"
GAME_COMPILE_COMMAND = ["go", "build"]
GAME_RUN_COMMAND = ["go", "run"]

def find_all_game_dirs(source):
    game_paths = []

    for root, dirs, files in os.walk(source):
        for directory in dirs:
            if GAME_DIR_PATTERN in directory.lower():
                path = os.path.join(source, directory)
                game_paths.append(path)
        break
    return game_paths

def create_dir(path):
    if not os.path.exists(path):
        os.mkdir(path)

def get_name_from_path(paths, to_strip):
    new_names = []
    for path in paths:
        _, dir_name = os.path.split(path)
        new_dir_name = dir_name.replace(to_strip, "")
        new_names.append(new_dir_name)
    return new_names

def copy_and_overwrite(source, dest):
    if os.path.exists(dest):
        shutil.rmtree(dest)   #Recursive delete the existing destination folder
    shutil.copytree(source, dest)

def make_json_file(path, game_dirs):
    data={
        "gameNames": game_dirs,
        "numberOfGames": len(game_dirs)
    }

    with open(path, "w") as f:
        json.dump(data, f)

def run_command(command, path):
    cwd = os.getcwd()
    os.chdir(path)
    result = run(command, stdout=PIPE, stdin=PIPE, universal_newlines=True)
    print("Result", result)
    os.chdir(cwd)


def compile_game_code(path):
    code_file_name = None
    for root, dirs, files in os.walk(path):
        for file in files:
            if GAME_CODE_EXTENSION in file:
                code_file_name =  file
                break
        break
    
    if code_file_name is None:
        return
    
    command = GAME_COMPILE_COMMAND + [code_file_name]
    run_command(command, path)

def run_game_code(path):
    code_file_name = None
    for root, dirs, files in os.walk(path):
        for file in files:
            if GAME_CODE_EXTENSION in file:
                code_file_name =  file
                break
        break

    if code_file_name is None:
        return

    command = GAME_RUN_COMMAND + [code_file_name]
    run_command(command, path)


def main(source, target):
    cwd = os.getcwd()  #Get current working directory
    source_path = os.path.join(cwd, source) #Get source path
    target_path = os.path.join(cwd, target) #Get target path
    game_paths = find_all_game_dirs(source_path)
    new_game_dirs = get_name_from_path(game_paths, "_game")
    create_dir(target_path)

    for src, dest in zip(game_paths, new_game_dirs): 
        dest_path = os.path.join(target_path, dest)
        copy_and_overwrite(src, dest_path)
        compile_game_code(dest_path)
        run_game_code(dest_path)

    json_path = os.path.join(target_path, "json_path")
    make_json_file(json_path, new_game_dirs)

#Execute the main script only if running this python file directly
if __name__ == "__main__":
    args = sys.argv
    if len(args) != 3:
        raise Exception("You must pass a source and target directory only")
    
    source, target = args[1:]
    main(source, target)