import os, json, platform
from typing import Tuple, List

import filetype, filedate
from progressbar import progressbar
from win32_setctime import setctime

import file_utils

FIX_FILE_EXTENSIONS = False
CONVERT_HEIC_TO_JPG = False


def __file_filter(fname: str) -> bool:
    is_file = os.path.isfile(fname)
    is_image = filetype.is_image(fname)
    is_video = filetype.is_video(fname)
    is_json = fname[-5:].lower() == ".json"
    return is_file and (is_image or is_video or is_json)


def __get_files(path: str) -> List[str]:
    if os.path.isdir(path):
        files = [f"{path}/{f}" for f in os.listdir(path)]
    else:
        key = __get_key(path)
        dirname = get_file_details(path)[0]
        files = [f"{dirname}/{f}" for f in os.listdir(dirname) if key in f]
    files = list(filter(__file_filter, files))
    return files


def __get_key(fname: str) -> str:
    # -- Assumes this structure --
    # Image:
    #   filename1.HEIC
    # Json:
    #   filename1.HEIC.json
    # So 'key' should be:
    #   filename1
    _, prefix, ext = get_file_details(fname)
    if ext == ".json":
        key = os.path.splitext(prefix)[0]
    elif "-edited" in prefix:
        key = prefix.split("-edited")[0]
    else:
        key = prefix
    return key


def __apply_metadata(img_fname: str, json_fname: str):
    with open(json_fname) as json_f:
        md = json.load(json_f)


    time = md.get("photoTakenTime", md.get("creationTime", {}))
    time_num = int(time.get("timestamp"))
    if not time_num:
        return

    # Set modified date
    os.utime(img_fname, (time_num, time_num))

    # Set created date
    if platform.uname().system == "Windows":
        setctime(img_fname, time_num)
    else:
        fdate = filedate.File(img_fname)
        modified_date = fdate.get()["modified"].strftime("%Y.%m.%d %H:%M:%S")
        fdate.set(
            created=modified_date,
        )


def get_file_details(full_name: str) -> Tuple[str, str, str]:
    dir_name = os.path.dirname(full_name)
    basename = os.path.basename(full_name)
    prefix, ext = os.path.splitext(basename)
    return (dir_name, prefix, ext)


# Entry point for this script
def process_files_in_dir(path: str) -> int:
    file_pairs = {}
    files = __get_files(path)

    for fname in files:
        key = __get_key(fname)
        pair = file_pairs.setdefault(key, {})

        if fname[-5:].lower() == ".json":
            pair["json"] = fname
        else:
            images = pair.setdefault("images", set())
            images.add(fname)

    imgs_modified = 0
    for key in progressbar(file_pairs, redirect_stdout=True):
        pair = file_pairs[key]
        can_fix_extensions = FIX_FILE_EXTENSIONS and len(pair.get("images"))
        if CONVERT_HEIC_TO_JPG or can_fix_extensions:
            new_set = set()
            for img_fname in pair["images"]:
                new_img_fname = None
                can_convert = CONVERT_HEIC_TO_JPG and file_utils.is_heic(img_fname)
                if can_convert:
                    new_img_fname = file_utils.convert_heic_to_jpg(img_fname)
                elif can_fix_extensions:
                    new_img_fname = file_utils.fix_incorrect_extension(img_fname)
                new_set.add(new_img_fname or img_fname)
            pair["images"] = new_set
        if len(pair) < 2:
            print(f"Cannot find pair for {key}. Skipping...")
            continue
        for img in pair["images"]:
            __apply_metadata(img, pair["json"])
            imgs_modified += 1
        os.remove(pair["json"])
    return imgs_modified


if __name__ == "__main__":
    raise Exception("Do not run the program from this file. Instead, run the run.py file.")
