import sys, os
from typing import List

import utils


def print_help_and_exit(error_msg=None):
    if error_msg:
        print("ERROR!")
        print(error_msg)
        print()
    print("Usage:")
    print("$ python3 run.py [--view | --preview] <path>")
    print("<path> should be the directory that contains images and json files.")
    print()
    print("Example usage for fixing metadata:")
    print("$ python3 run.py my-google-takeout-path/")
    print()
    print("Example usage for viewing current metadata:")
    print("$ python3 run.py --view my-google-takeout-path/")
    print()
    print("Example usage for previewing changes in metadata without modifying any files:")
    print("$ python3 run.py --preview my-google-takeout-path/")
    print()
    sys.exit(1 if error_msg else 0)


def print_success_message():
    print("Success! Metadata applied! Nothing else needs to be done.")
    print()
    print("Use the following example if you want to see the new metadata:")
    print("$ python3 run.py --view <path>")
    print()


def format_folder_path(path):
    returned_path = path
    if path[0] != "/":
        returned_path = f"{os.getcwd()}/{returned_path}"
    if path[-1] == "/":
        returned_path = returned_path[:-1]
    return returned_path


def set_attributes(args: List[str]) -> str:
    if len(args) < 2:
        print_help_and_exit("Not enough arguments")
    elif len(args) > 3:
        print_help_and_exit("Too many arguments")

    folder_path = None
    for arg in args[1:]:
        if arg in ["--help", "-h"]:
            print_help_and_exit()
        elif arg == "--view":
            utils.VIEW_ONLY = True
        elif arg == "--preview":
            utils.PREVIEW_ONLY = True
        elif arg[0] == "-":
            print_help_and_exit(f"Unknown argument: {arg}")
        else:
            folder_path = format_folder_path(arg)

    if not folder_path:
        print_help_and_exit("Did not provide <path>")

    if not os.path.exists(folder_path):
        print_help_and_exit(f"Directory: {folder_path}\n does not exist.")
    elif os.path.isfile(folder_path):
        print_help_and_exit(f"Directory: {folder_path}\n is a file, not a directory.")

    return folder_path

def main():
    folder_path = set_attributes(sys.argv)
    utils.process_files_in_dir(folder_path)
    if not (utils.PREVIEW_ONLY or utils.VIEW_ONLY):
        print_success_message()


if __name__ == "__main__":
    main()
