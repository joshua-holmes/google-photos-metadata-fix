import os, json
from typing import Tuple

import filetype, whatimage
from PIL import Image as ImagePIL
from exif import Image as ImageExif
from pillow_heif import register_heif_opener
from unidecode import unidecode
from progressbar import progressbar

VIEW_ONLY = False
PREVIEW_ONLY = False


def __file_filter(fname: str) -> bool:
    is_file = os.path.isfile(fname)
    is_image = filetype.is_image(fname)
    is_video = filetype.is_video(fname)
    is_json = fname[-5:].lower() == ".json"
    return is_file and (is_image or is_video or is_json)


def __apply_metadata(img_fname: str, json_fname: str):
    with open(json_fname) as json_f:
        md = json.load(json_f)

    with open(img_fname, "rb") as img_f:
        img_fmt = whatimage.identify_image(img_f.read())

    if img_fmt == "heic":
        jpg_fname = __convert_heic_to_jpg(img_fname)
        img_fname = jpg_fname

    with open(img_fname, "rb") as img_f:
        image = ImageExif(img_f)

    description = md.get("description")
    if description:
        image.image_description = unidecode(description)

    time = md.get("photoTakenTime", md.get("creationTime", {}))
    time_formatted = time.get("formatted")
    if time_formatted:
        image.datetime = unidecode(time_formatted)

    geo_data = md.get("geoData", md.get("geoDataExif", {}))
    latitude = geo_data.get("latitude")
    longitude = geo_data.get("longitude")
    if latitude and longitude:
        image.gps_latitude = latitude
        image.gps_longitude = longitude
        altitude = geo_data.get("altitude")
        if altitude:
            image.gps_altitude = altitude

    if PREVIEW_ONLY:
        print_metadata(img_fname, image)
    else:
        with open(img_fname, "wb") as img_f:
            img_f.write(image.get_file())


def __convert_heic_to_jpg(heic_fname: str) -> str:
    dir_name, prefix, _ = get_file_details(heic_fname)
    jpg_fname = f"{dir_name}/{prefix}.jpg"

    register_heif_opener()
    with ImagePIL.open(heic_fname) as f:
        f.save(jpg_fname)

    os.remove(heic_fname)
    return jpg_fname


def get_file_details(full_name: str) -> Tuple[str, str, str]:
    dir_name = os.path.dirname(full_name)
    basename = os.path.basename(full_name)
    prefix, ext = os.path.splitext(basename)
    return (dir_name, prefix, ext)


def print_metadata(img_fname: str, image = None):
    if type(image) is not ImageExif:
        with open(img_fname, "rb") as img_f:
            image = ImageExif(img_f)
    _, prefix, ext = get_file_details(img_fname)
    all_attrs = image.get_all()
    print("NAME:", prefix + ext)
    print("# OF FIELDS:", len(all_attrs))
    for attr in all_attrs:
        print(f"{attr}: {image.get(attr)}")
    print()


# Entry point for this script
def process_files_in_dir(folder_path: str):
    files = [f"{folder_path}/{f}" for f in os.listdir(folder_path)]
    files = list(filter(__file_filter, files))
    file_pairs = {}

    for fname in files:
        prefix = get_file_details(fname)[1]
        pair = file_pairs.setdefault(prefix, {})

        if fname[-5:].lower() == ".json":
            pair["json"] = fname
        else:
            if "image" in pair:
                _, prefix1, ext1 = get_file_details(fname)
                _, prefix2, ext2 = get_file_details(pair["image"])
                message = f"""
Oops! Found multiple images with the same prefix.
    {prefix1 + ext1}
    {prefix2 + ext2}
                """
                raise Exception(message)
            pair["image"] = fname

    for prefix in progressbar(file_pairs, redirect_stdout=True):
        pair = file_pairs[prefix]
        if VIEW_ONLY:
            print_metadata(pair["image"])
        else:
            if len(pair) < 2:
                print(f"Cannot find pair for {prefix}. Skipping...")
                continue
            __apply_metadata(pair["image"], pair["json"])


if __name__ == "__main__":
    raise Exception("Do not run the program from this file. Instead, run the run.py file.")
