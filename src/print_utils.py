import sys

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


def print_success_message(imgs_modified: int):
    print("Success! Metadata applied! Nothing else needs to be done.")
    print(f"{imgs_modified} images written to")
    print()
    print("Use the following example if you want to see the new metadata:")
    print("$ python3 run.py --view <path>")
    print()


if __name__ == "__main__":
    raise Exception("Do not run the program from this file. Instead, run the run.py file.")
