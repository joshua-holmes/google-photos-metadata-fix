import os, shutil

CUR_DIR = os.path.dirname(os.path.abspath(__file__))

def import_file(img_fname: str, unique_tag: str) -> str:
    root_dir = os.environ.get("ROOT_DIR")
    if not root_dir:
        raise Exception("Cannot find root directory!")
    new_location = f"{CUR_DIR}/{unique_tag}_{img_fname}"
    shutil.copy2(f"{root_dir}/test_assets/{img_fname}", new_location)
    return new_location


def remove_dir(path):
    if not os.path.exists(path):
        return
    for item in os.listdir(path):
        item_path = f"{path}/{item}"
        if os.path.isdir(item_path):
            remove_dir(item_path)
        else:
            os.remove(f"{path}/{item}")
    os.rmdir(path)
