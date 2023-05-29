import os, json, platform, time
from os.path import isdir
from typing import Optional, Tuple, List
from datetime import datetime
from dateutil import parser

import filetype, whatimage, filedate
from PIL import Image as ImagePIL
from exif import Image as ImageExif
from pillow_heif import register_heif_opener
from unidecode import unidecode
from progressbar import progressbar
from win32_setctime import setctime

VIEW_ONLY = False
PREVIEW_ONLY = False
FIX_FILE_EXTENSIONS = False
CONVERT_HEIC_TO_JPG = False


def __print_heic_warning(fname):
    print(f"""Cannot view heic metadata for file:
    {fname}
Run the script without the --view flag to automatically convert to jpg and
apply metadata to all files.
Skipping...
"""
    )


def __file_filter(fname: str) -> bool:
    is_file = os.path.isfile(fname)
    is_image = filetype.is_image(fname)
    is_video = filetype.is_video(fname)
    is_json = fname[-5:].lower() == ".json"
    return is_file and (is_image or is_video or is_json)


def __is_heic(img_fname: str) -> bool:
    with open(img_fname, "rb") as f:
        img_fmt = whatimage.identify_image(f.read())
    return img_fmt == "heic"


def __convert_heic_to_jpg(img_fname: str) -> Optional[str]:
    if not __is_heic(img_fname):
        return None
    dir_name, prefix, _ = get_file_details(img_fname)
    jpg_fname = f"{dir_name}/{prefix}.jpg"

    register_heif_opener()
    with ImagePIL.open(img_fname) as f:
        f.save(jpg_fname)

    os.remove(img_fname)
    return jpg_fname


def __fix_incorrect_extension(img_fname) -> Optional[str]:
    with open(img_fname, "rb") as f:
        img_fmt = whatimage.identify_image(f.read())
    dirname, prefix, ext = get_file_details(img_fname)

    if img_fmt and img_fmt.lower() == "jpeg":
        img_fmt = "jpg"
    if ext == ".jpeg":
        ext = ".jpg"

    if img_fmt and ext[1:].lower() != img_fmt.lower():
        new_fname = dirname + "/" + prefix + "." + img_fmt.lower()
        os.rename(img_fname, new_fname)
        _, new_prefix, new_ext = get_file_details(new_fname)
        _, old_prefix, old_ext = get_file_details(img_fname)
        print(f"Renamed: {old_prefix + old_ext} -> {new_prefix + new_ext}")
        return new_fname
    return None


def get_file_details(full_name: str) -> Tuple[str, str, str]:
    dir_name = os.path.dirname(full_name)
    basename = os.path.basename(full_name)
    prefix, ext = os.path.splitext(basename)
    return (dir_name, prefix, ext)


def print_metadata(img_fname: str, image = None):
    _, prefix, ext = get_file_details(img_fname)
    if __is_heic(img_fname):
        __print_heic_warning(prefix + ext)
        return
    if type(image) is not ImageExif:
        with open(img_fname, "rb") as img_f:
            image = ImageExif(img_f)
    all_attrs = image.get_all()
    print("NAME:", prefix + ext)
    print("# OF FIELDS:", len(all_attrs))
    for attr in all_attrs:
        print(f"{attr}: {image.get(attr)}")
    print()

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
        if VIEW_ONLY:
            if "images" in pair:
                for img in pair["images"]:
                    print_metadata(img)
        else:
            can_fix_extensions = FIX_FILE_EXTENSIONS and len(pair.get("images"))
            if CONVERT_HEIC_TO_JPG or can_fix_extensions:
                new_set = set()
                for img_fname in pair["images"]:
                    new_img_fname = None
                    if CONVERT_HEIC_TO_JPG:
                        new_img_fname = __convert_heic_to_jpg(img_fname)
                    elif can_fix_extensions:
                        new_img_fname = __fix_incorrect_extension(img_fname)
                    new_set.add(new_img_fname or img_fname)
                pair["images"] = new_set
            if len(pair) < 2:
                print(f"Cannot find pair for {key}. Skipping...")
                continue
            for img in pair["images"]:
                __apply_metadata(img, pair["json"])
                imgs_modified += 1
            # os.remove(pair["json"])
    return imgs_modified


if __name__ == "__main__":
    raise Exception("Do not run the program from this file. Instead, run the run.py file.")
