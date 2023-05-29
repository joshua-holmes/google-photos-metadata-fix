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


def print_success_message(imgs_modified: str):
    print("Success! Metadata applied! Nothing else needs to be done.")
    print(f"{imgs_modified} images written to")
    print()
    print("Use the following example if you want to see the new metadata:")
    print("$ python3 run.py --view <path>")
    print()


def ask_questions():
    while True:
        print("Do you want to rename file extensions if images have incorrect extensions?")
        print("e.g. a JPG file is named \"myimage.HEIC\"")
        print("y,yes,n,no")
        answer = input()
        print()
        if answer.lower() in ["y", "yes"]:
            utils.FIX_FILE_EXTENSIONS = True
            break
        elif answer.lower() in ["n", "no"]:
            utils.FIX_FILE_EXTENSIONS = False
            break


def format_path(path):
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

    path = None
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
            path = format_path(arg)

    if not path:
        print_help_and_exit("Did not provide <path>")

    if not os.path.exists(path):
        print_help_and_exit(f"Directory: {path}\n does not exist.")

    return path

def main():
    path = set_attributes(sys.argv)
    real_run = not (utils.PREVIEW_ONLY or utils.VIEW_ONLY)
    if real_run:
        ask_questions()

    imgs_modified = utils.process_files_in_dir(path)
    if real_run:
        print_success_message(imgs_modified)


if __name__ == "__main__":
    main()
