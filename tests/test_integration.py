import json
import shutil
import sys, os
from typing import Dict, Tuple

sys.path.append("../")

import run
from src import utils

ROOT_DIR = "/".join(os.path.dirname(os.path.abspath(__file__)).split("/")[:-1])


def remove_dir(path):
    if not os.path.exists(path):
        return
    for item in os.listdir(path):
        os.remove(f"{path}/{item}")
    os.rmdir(path)


def general_setup() -> Tuple[str, Dict]:
    asset_dir = f"{ROOT_DIR}/test_assets"
    test_dir = f"{ROOT_DIR}/test_integration"
    fnames = os.listdir(asset_dir)
    old_files = [f"{asset_dir}/{f}" for f in fnames if "TEST_HEIC" in f]
    new_files = [f"{test_dir}/{f}" for f in fnames if "TEST_HEIC" in f]
    remove_dir(test_dir)
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
        utils.CONVERT_HEIC_TO_JPG = False
        utils.FIX_FILE_EXTENSIONS = False
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
        remove_dir(cls.test_dir)


class TestIntegrationWithFixedExtensions:
    @classmethod
    def setup_class(cls):
        utils.CONVERT_HEIC_TO_JPG = False
        utils.FIX_FILE_EXTENSIONS = True
        cls.test_dir, cls.json_data = general_setup()
        run.main()

    @classmethod
    def test_fixing_extensions(cls):
        assert "TEST_HEIC-edited.jpg" in os.listdir(cls.test_dir)

    @classmethod
    def test_metadata_changed(cls):
        assert os.path.getmtime(f"{cls.test_dir}/TEST_HEIC.HEIC") == int(cls.json_data["photoTakenTime"]["timestamp"])

    @classmethod
    def teardown_class(cls):
        remove_dir(cls.test_dir)


class TestIntegrationWithConversion:
    @classmethod
    def setup_class(cls):
        utils.CONVERT_HEIC_TO_JPG = True
        utils.FIX_FILE_EXTENSIONS = False
        cls.test_dir, cls.json_data = general_setup()
        run.main()

    @classmethod
    def test_file_conversion(cls):
        assert "TEST_HEIC.jpg" in os.listdir(cls.test_dir)

    @classmethod
    def test_metadata_changed(cls):
        assert os.path.getmtime(f"{cls.test_dir}/TEST_HEIC.jpg") == int(cls.json_data["photoTakenTime"]["timestamp"])

    @classmethod
    def teardown_class(cls):
        remove_dir(cls.test_dir)

