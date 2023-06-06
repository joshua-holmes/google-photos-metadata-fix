import os, sys, json, shutil, pathlib
from datetime import datetime

import filedate, platform, pytest
from dateutil import parser
from tests.tools_for_testing import CUR_DIR

import tools_for_testing as tft

sys.path.append("../")

import lib

class TestApplyMetadata:
    @classmethod
    def setup_class(cls):
        cls.img_path = tft.import_file("TEST_JPG.jpg", "TestApplyMetadata")
        cls.json_path = tft.import_file("TEST_JPG.jpg.json", "TestApplyMetadata")

        with open(cls.json_path) as f:
            cls.json = json.load(f)
        assert os.path.getctime(cls.img_path) != float(cls.json["photoTakenTime"]["timestamp"])
        assert os.path.getmtime(cls.img_path) != float(cls.json["photoTakenTime"]["timestamp"])
        lib.apply_metadata(cls.img_path, cls.json_path)

    def test_apply_modified_time(self):
        assert os.path.getmtime(self.img_path) == float(self.json["photoTakenTime"]["timestamp"])

    def test_apply_created_time(self):
        # Linux's "creation" date is an after-thought and sometimes doesn't work
        if platform.system() == "Windows":
            assert os.path.getctime(self.img_path) == float(self.json["photoTakenTime"]["timestamp"])

    def test_apply_exif_data(self):
        test_date = filedate.File(self.img_path).get()["modified"]
        correct_date = datetime.fromtimestamp(int(self.json["photoTakenTime"]["timestamp"]))
        assert test_date == correct_date

    @classmethod
    def teardown_class(cls):
        for fname in [cls.img_path, cls.json_path]:
            if os.path.exists(fname):
                os.remove(fname)


class TestGroupFilesByName:
    def test_edited_images(self):
        files = ["COOLNAME.jpg", "COOLNAME-edited.jpg"]
        result = lib.group_files_by_name(files)
        assert result[""]["COOLNAME"]["images"] == set(files)

    def test_images_with_different_names(self):
        files = ["COOLNAME.jpg", "OTHERNAME.jpg"]
        result = lib.group_files_by_name(files)
        assert result[""]["COOLNAME"]["images"] == set([files[0]])
        assert result[""]["OTHERNAME"]["images"] == set([files[1]])

    def test_image_groups_with_json(self):
        files = ["COOLNAME.jpg", "COOLNAME.jpg.json", "OTHERNAME.jpg"]
        result = lib.group_files_by_name(files)
        assert result[""]["COOLNAME"] == {
            "images": {"COOLNAME.jpg"},
            "json": "COOLNAME.jpg.json"
        }

    def test_images_from_different_directories(self):
        files = ["/some/directory/COOLNAME.jpg", "/another/directory/COOLNAME.jpg.json"]
        result = lib.group_files_by_name(files)
        assert result["/some/directory"]["COOLNAME"] == {
            "images": {"COOLNAME.jpg"}
        }
        assert result["/another/directory"]["COOLNAME"] == {
            "json": "COOLNAME.jpg.json"
        }

    def test_file_renaming_in_group(self, mocker):
        lib.CONVERT_HEIC_TO_JPG = True
        mocker.patch("file_utils.convert_heic_to_jpg", return_value="TEST_HEIC.jpg")
        mocker.patch("file_utils.is_heic", return_value=True)
        file_structure = { "": { "TEST_HEIC": {
            "images": {"TEST_HEIC.HEIC"}
        }}}
        lib.apply_image_fixes(file_structure)
        lib.CONVERT_HEIC_TO_JPG = False # cleanup
        assert file_structure == { "": { "TEST_HEIC": {
            "images": {"TEST_HEIC.jpg"}
        }}}


class TestGetFiles:
    @classmethod
    def setup_class(cls):
        cls.zip_prefix = "TEST_takeout"
        tft.remove_dir(f"{CUR_DIR}/{cls.zip_prefix}")
        tft.remove_dir(f"{CUR_DIR}/zipthis")

        jpg_path = tft.import_file("TEST_JPG.jpg", "TestGetFiles")
        heic_path = tft.import_file("TEST_HEIC.HEIC", "TestGetFiles")
        jpg_dir = f"{CUR_DIR}/zipthis/Takeout/Google Photos/JPGs"
        heic_dir = f"{CUR_DIR}/zipthis/Takeout/Google Photos/HEICs"

        pathlib.Path(jpg_dir).mkdir(parents=True)
        pathlib.Path(heic_dir).mkdir(parents=True)

        os.rename(jpg_path, f"{jpg_dir}/TEST_JPG.jpg")
        os.rename(heic_path, f"{heic_dir}/TEST_HEIC.HEIC")
        
        cls.zip_path = shutil.make_archive(f"{CUR_DIR}/{cls.zip_prefix}", "zip", f"{CUR_DIR}/zipthis")

        tft.remove_dir(f"{CUR_DIR}/zipthis")

        # Run tested script
        cls.file_paths = lib.get_file_paths(cls.zip_path)

    def test_get_files_paths_from_zip(self):
        assert self.file_paths == [
            f"{CUR_DIR}/{self.zip_prefix}/Takeout/Google Photos/JPGs/TEST_JPG.jpg",
            f"{CUR_DIR}/{self.zip_prefix}/Takeout/Google Photos/HEICs/TEST_HEIC.HEIC"
        ]

    @classmethod
    def teardown_class(cls):
        os.remove(cls.zip_path)
        tft.remove_dir(f"{CUR_DIR}/{cls.zip_prefix}")

