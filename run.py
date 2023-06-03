import sys, os
from typing import List

from src import print_utils, lib


def ask_if_fix_extensions():
    while True:
        print("Do you want to rename images if images have incorrect extensions?")
        print("If you consent, it will rename selected images, even if metadata cannot be applied later in the process.")
        print('e.g. a JPG file named "myimage.HEIC" would be renamed "myimage.jpg"')
        print("y,yes,n,no")
        answer = input()
        print()
        if answer.lower() in ["y", "yes"]:
            lib.FIX_FILE_EXTENSIONS = True
            break
        elif answer.lower() in ["n", "no"]:
            lib.FIX_FILE_EXTENSIONS = False
            break


def ask_if_convert():
    while True:
        print("Do you want to convert all HEIC images to JPG?")
        print("JPG is a more common file type than HEIC and will be viewable on almost any device.")
        print("y,yes,n,no")
        answer = input()
        print()
        if answer.lower() in ["y", "yes"]:
            lib.CONVERT_HEIC_TO_JPG = True
            break
        elif answer.lower() in ["n", "no"]:
            lib.CONVERT_HEIC_TO_JPG = False
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
        print_utils.print_help_and_exit("Not enough arguments")
    elif len(args) > 3:
        print_utils.print_help_and_exit("Too many arguments")

    path = None
    for arg in args[1:]:
        if arg in ["--help", "-h"]:
            print_utils.print_help_and_exit()
        elif arg[0] == "-":
            print_utils.print_help_and_exit(f"Unknown argument: {arg}")
        else:
            path = format_path(arg)

    if not path:
        print_utils.print_help_and_exit("Did not provide <path>")
    elif not os.path.exists(path):
        print_utils.print_help_and_exit(f"Directory: {path}\n does not exist.")

    return path or "" # The LSP hates it when I don't include the 'or ""' bit

def main():
    path = set_attributes(sys.argv)

    if type(lib.FIX_FILE_EXTENSIONS) is not bool:
        ask_if_fix_extensions()
    if type(lib.CONVERT_HEIC_TO_JPG) is not bool:
        ask_if_convert()

    imgs_modified = lib.process_files_in_dir(path)
    print_utils.print_success_message(imgs_modified)


if __name__ == "__main__":
    main()
