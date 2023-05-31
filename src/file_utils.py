import os
from typing import Optional

import whatimage
from PIL import Image as ImagePIL
from pillow_heif import register_heif_opener

import utils

def is_heic(img_fname: str) -> bool:
    with open(img_fname, "rb") as f:
        img_fmt = whatimage.identify_image(f.read())
    return img_fmt == "heic"


def convert_heic_to_jpg(img_fname: str) -> Optional[str]:
    if not is_heic(img_fname):
        return None
    dir_name, prefix, _ = utils.get_file_details(img_fname)
    jpg_fname = f"{dir_name}/{prefix}.jpg"

    register_heif_opener()
    with ImagePIL.open(img_fname) as f:
        f.save(jpg_fname)

    os.remove(img_fname)
    return jpg_fname


def fix_incorrect_extension(img_fname) -> Optional[str]:
    with open(img_fname, "rb") as f:
        img_fmt = whatimage.identify_image(f.read())
    dirname, prefix, ext = utils.get_file_details(img_fname)

    if img_fmt and img_fmt.lower() == "jpeg":
        img_fmt = "jpg"
    if ext == ".jpeg":
        ext = ".jpg"

    if img_fmt and ext[1:].lower() != img_fmt.lower():
        new_fname = dirname + "/" + prefix + "." + img_fmt.lower()
        os.rename(img_fname, new_fname)
        _, new_prefix, new_ext = utils.get_file_details(new_fname)
        _, old_prefix, old_ext = utils.get_file_details(img_fname)
        print(f"Renamed: {old_prefix + old_ext} -> {new_prefix + new_ext}")
        return new_fname
    return None

if __name__ == "__main__":
    raise Exception("Do not run the program from this file. Instead, run the run.py file.")
