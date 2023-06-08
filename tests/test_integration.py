import json
import shutil
import sys, os
from typing import Dict, Tuple

sys.path.append("../")

import run
import src.tests.tools_for_testing as tft
from src import lib

ROOT_DIR = "/".join(os.path.dirname(os.path.abspath(__file__)).split("/")[:-1])


def general_setup() -> Tuple[str, Dict]:
    asset_dir = f"{ROOT_DIR}/test_assets"
    test_dir = f"{ROOT_DIR}/test_integration"
    fnames = os.listdir(asset_dir)
    old_files = [f"{asset_dir}/{f}" for f in fnames if "TEST_HEIC" in f]
    new_files = [f"{test_dir}/{f}" for f in fnames if "TEST_HEIC" in f]
    tft.remove_dir(test_dir)
    os.mkdir(test_dir)

    for old, new in zip(old_files, new_files):
        shutil.copy2(old, new)

    os.chdir(ROOT_DIR)
    sys.argv = ["run.py", "./test_integration"]

    with open(f"{test_dir}/TEST_HEIC.HEIC.json") as f:
        json_data = json.load(f)
    return test_dir, json_data


class TestBasicIntegration:
    @classmethod
    def setup_class(cls):
        lib.CONVERT_HEIC_TO_JPG = False
        lib.FIX_FILE_EXTENSIONS = False
        cls.test_dir, cls.json_data = general_setup()
        run.main()

    @classmethod
    def test_json_deleted(cls):
        assert set(os.listdir(cls.test_dir)) == set(["TEST_HEIC.HEIC", "TEST_HEIC-edited.HEIC"])

    @classmethod
    def test_metadata_changed(cls):
        assert os.path.getmtime(f"{cls.test_dir}/TEST_HEIC.HEIC") == int(cls.json_data["photoTakenTime"]["timestamp"])

    @classmethod
    def teardown_class(cls):
        tft.remove_dir(cls.test_dir)

