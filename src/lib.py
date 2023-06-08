import os, json, platform, zipfile
from typing import Tuple, List, Dict
from datetime import datetime

import filetype, filedate
from progressbar import progressbar
from win32_setctime import setctime
from exif import Image as ImageExif

import file_utils

FIX_FILE_EXTENSIONS = None
CONVERT_HEIC_TO_JPG = None


def __file_filter(fname: str) -> bool:
    is_file = os.path.isfile(fname)
    is_image = filetype.is_image(fname)
    is_video = filetype.is_video(fname)
    is_json = fname[-5:].lower() == ".json"
    return is_file and (is_image or is_video or is_json)


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


def __apply_exif(img_fname: str, dt: datetime):
    fmt = "%Y:%m:%d %H:%M:%S"
    dt_str = dt.strftime(fmt)

    try:
        with open(img_fname, "rb") as f:
            image = ImageExif(f)
        try:
            image.datetime = dt_str
            image.datetime_original = dt_str
            image.datetime_digitized = dt_str
        except:
            pass
        with open(img_fname, "wb") as f:
            f.write(image.get_file())
    except Exception as e:
        pass


def __apply_os_metadata(img_fname: str, dt: datetime):
    fmt = "%Y.%m.%d %H:%M:%S"
    dt_str = dt.strftime(fmt)

    fdate = filedate.File(img_fname)
    fdate.set(
        created = dt_str,
	    modified = dt_str,
	    accessed = dt_str
    )


def __search_dir_for_files(dirname: str) -> List[str]:
    if not os.path.isdir(dirname):
        raise Exception(f'"{dirname}" is not a directory')
    list_of_file_paths = []
    stack = [dirname]
    while stack:
        cur = stack.pop()
        if os.path.isdir(cur):
            for item in os.listdir(cur):
                stack.append(f"{cur}/{item}")
        else:
            list_of_file_paths.append(cur)
    return list_of_file_paths


def group_files_by_name(files: List[str]) -> Dict:
    file_pairs = {}

    for fname in files:
        dirname, prefix, ext = get_file_details(fname)
        key = __get_key(fname)
        pair = file_pairs.setdefault(dirname, {}).setdefault(key, {})

        if fname[-5:].lower() == ".json":
            pair["json"] = prefix + ext
        else:
            images = pair.setdefault("images", set())
            images.add(prefix + ext)

    return file_pairs


def get_file_paths(path: str) -> List[str]:
    if os.path.isdir(path):
        return __search_dir_for_files(path)
    elif zipfile.is_zipfile(path):
        dirname, prefix, _ = get_file_details(path)
        extracted_path = f"{dirname}/{prefix}"
        print("Extracting...")
        with zipfile.ZipFile(path, "r") as zip_obj:
            zip_obj.extractall(extracted_path)
        return __search_dir_for_files(extracted_path)
    else:
        raise Exception("Only directories and zip files are allowed to be entered as an arg to this script")


def get_file_details(full_name: str) -> Tuple[str, str, str]:
    dir_name = os.path.dirname(full_name)
    basename = os.path.basename(full_name)
    prefix, ext = os.path.splitext(basename)
    return (dir_name, prefix, ext)


def apply_metadata(img_path: str, json_path: str):
    with open(json_path) as json_f:
        md = json.load(json_f)

    times = md.get("photoTakenTime", md.get("creationTime", {}))
    time_num = int(times.get("timestamp"))
    if not time_num:
        return
    dt = datetime.fromtimestamp(time_num)

    __apply_exif(img_path, dt)
    __apply_os_metadata(img_path, dt)


def apply_image_fixes(file_pairs):
    for dirname in progressbar(file_pairs, redirect_stdout=True):
        print("Applying file fixes for directory:", dirname)
        for key in file_pairs[dirname]:
            pair = file_pairs[dirname][key]
            can_fix_extensions = FIX_FILE_EXTENSIONS and len(pair.get("images", set()))
            if CONVERT_HEIC_TO_JPG or can_fix_extensions:
                new_set = set()
                for img_fname in pair.get("images", set()):
                    img_path = f"{dirname}/{img_fname}"
                    new_img_path = None
                    can_convert = CONVERT_HEIC_TO_JPG and file_utils.is_heic(img_path)
                    if can_convert:
                        new_img_path = file_utils.convert_heic_to_jpg(img_path)
                    elif can_fix_extensions:
                        new_img_path = file_utils.fix_incorrect_extension(img_path)
                    if new_img_path:
                        _, new_prefix, new_ext = get_file_details(new_img_path)
                        new_img_fname = new_prefix + new_ext
                    else:
                        new_img_fname = None
                    new_set.add(new_img_fname or img_fname)
                pair["images"] = new_set


# Entry point for this script
def process_files_in_dir(path: str) -> int:
    files = get_file_paths(path)
    file_pairs = group_files_by_name(files)

    if FIX_FILE_EXTENSIONS or CONVERT_HEIC_TO_JPG:
        apply_image_fixes(file_pairs)

    imgs_modified = 0
    print("Applying metadata...")
    for dirname in progressbar(file_pairs, redirect_stdout=True):
        for key in file_pairs[dirname]:
            pair = file_pairs[dirname][key]
            if len(pair) < 2:
                continue
            for img in pair["images"]:
                apply_metadata(f"{dirname}/{img}", f"{dirname}/{pair['json']}")
                imgs_modified += 1
            os.remove(f"{dirname}/{pair['json']}")
    return imgs_modified


if __name__ == "__main__":
    raise Exception("Do not run the program from this file. Instead, run the run.py file.")
