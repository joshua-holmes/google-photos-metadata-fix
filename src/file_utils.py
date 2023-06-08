import os
from typing import Optional

import whatimage
from PIL import Image as ImagePIL
from pillow_heif import register_heif_opener

import lib


def is_heic(img_path: str) -> bool:
    with open(img_path, "rb") as f:
        img_fmt = whatimage.identify_image(f.read())
    return img_fmt == "heic"


def convert_heic_to_jpg(img_path: str) -> str:
    dir_name, prefix, ext = lib.get_file_details(img_path)
    jpg_path = f"{dir_name}/{prefix}.jpg"

    register_heif_opener()
    with ImagePIL.open(img_path) as f:
        f.save(jpg_path)
    os.remove(img_path)

    _, jpg_prefix, jpg_ext = lib.get_file_details(jpg_path)
    print(f"Converted: {prefix + ext} -> {jpg_prefix + jpg_ext}")
    return jpg_path


def fix_incorrect_extension(img_path) -> Optional[str]:
    with open(img_path, "rb") as f:
        img_fmt = whatimage.identify_image(f.read())
    dirname, prefix, ext = lib.get_file_details(img_path)

    if img_fmt and img_fmt.lower() == "jpeg":
        img_fmt = "jpg"
    if ext == ".jpeg":
        ext = ".jpg"

    if img_fmt and ext[1:].lower() != img_fmt.lower():
        new_img_path = dirname + "/" + prefix + "." + img_fmt.lower()
        os.rename(img_path, new_img_path)
        _, new_prefix, new_ext = lib.get_file_details(new_img_path)
        _, old_prefix, old_ext = lib.get_file_details(img_path)
        print(f"Renamed: {old_prefix + old_ext} -> {new_prefix + new_ext}")
        return new_img_path
    return None

if __name__ == "__main__":
    raise Exception("Do not run the program from this file. Instead, run the run.py file.")
