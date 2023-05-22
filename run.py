import sys, os, json

import filetype
from exif import Image

def print_help_and_exit(error_msg=None):
    if error_msg:
        print(error_msg, "\n")
    print("Usage:")
    print("$ python3 run.py <path>")
    print("<path> should be the directory that contains images and json files.")
    print()
    sys.exit(1 if error_msg else 0)

def process_files_in_dir(folder_path: str):
    files = os.listdir(folder_path)
    file_pairs = {}
    for fname in files:
        is_file = os.path.isfile(fname)
        is_image = filetype.is_image(fname)
        is_video = filetype.is_video(fname)
        if not (is_file and (is_image or is_video)):
            continue
        pair = file_pairs.setdefault(os.path.basename(fname), {})
        if fname[-5] == ".json":
            pair["json"] = fname
        else:
            if "image" in pair:
                message = f"""Oops! Already found image with same prefix name.
    {fname}
    {pair["image"]}"""
                raise Exception(message)
            pair["image"] = fname

    for basename in file_pairs:
        pair = file_pairs[basename]
        if len(pair) < 2:
            print(f"Cannot find pair for {basename}. Skipping...")
            continue
        
        apply_metadata(pair["image"], pair["json"])

def apply_metadata(image_file: str, json_file: str):
    pass

def main():
    print(sys.argv)
    if len(sys.argv) < 2:
        print_help_and_exit("Not enough arguments")
    elif sys.argv[1] in ["--help", "-h"]:
        print_help_and_exit()

    folder_path = sys.argv[1]
    if os.path.exists(folder_path):
        print_help_and_exit(f"Directory: {folder_path}\n does not exist.")
    elif os.path.isfile(folder_path):
        print_help_and_exit(f"Directory: {folder_path}\n is a file, not a directory.")
    
    process_files_in_dir(folder_path)




if __name__ == "__main__":
    main()
