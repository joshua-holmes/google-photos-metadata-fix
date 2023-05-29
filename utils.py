import os, json
from os.path import isdir
from typing import Tuple, List

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


def __is_heic(img_fname: str) -> bool:
    with open(img_fname, "rb") as f:
        img_fmt = whatimage.identify_image(f.read())
    return img_fmt == "heic"



def __apply_metadata(img_fname: str, json_fname: str):
    with open(json_fname) as json_f:
        md = json.load(json_f)

    if __is_heic(img_fname):
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
        try:
            image.gps_latitude = latitude
            image.gps_longitude = longitude
        except AssertionError:
            # There's a bug with exif that throws an error here sometimes
            pass
        altitude = geo_data.get("altitude")
        if altitude:
            image.gps_altitude = altitude

    if PREVIEW_ONLY:
        print_metadata(img_fname, image)
    else:
        with open(img_fname, "wb") as img_f:
            img_f.write(image.get_file())
        os.remove(json_fname)


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
    _, prefix, ext = get_file_details(img_fname)
    if __is_heic(img_fname):
        message = f"""Cannot view heic metadata for file:
    {prefix + ext}
Run the script without the --view flag to automatically convert to jpg and
apply metadata to all files.
Skipping...
"""
        print(message)
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

# Entry point for this script
def process_files_in_dir(path: str):
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

    for key in progressbar(file_pairs, redirect_stdout=True):
        pair = file_pairs[key]
        if VIEW_ONLY:
            if "images" in pair:
                for img in pair["images"]:
                    print_metadata(img)
        else:
            if len(pair) < 2:
                print(f"Cannot find pair for {key}. Skipping...")
                continue
            for img in pair["images"]:
                __apply_metadata(img, pair["json"])


if __name__ == "__main__":
    raise Exception("Do not run the program from this file. Instead, run the run.py file.")
