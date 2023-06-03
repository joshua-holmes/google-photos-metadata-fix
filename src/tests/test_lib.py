import os, sys, json
from datetime import datetime

import filedate, platform
from dateutil import parser

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
    def test_edited_image_groups_up_with_regular(self):
        files = ["COOLNAME.jpg", "COOLNAME-edited.jpg"]
        result = lib.group_files_by_name(files)
        assert result["COOLNAME"]["images"] == set(files)

    def test_images_with_different_name_do_not_group_up(self):
        files = ["COOLNAME.jpg", "OTHERNAME.jpg"]
        result = lib.group_files_by_name(files)
        assert result["COOLNAME"]["images"] == set([files[0]])
        assert result["OTHERNAME"]["images"] == set([files[1]])

    def test_image_groups_with_json(self):
        files = ["COOLNAME.jpg", "COOLNAME.jpg.json", "OTHERNAME.jpg"]
        result = lib.group_files_by_name(files)
        assert result["COOLNAME"] == {
            "images": {"COOLNAME.jpg"},
            "json": "COOLNAME.jpg.json"
        }

    def test_file_renaming_in_pairs_dict(self, mocker):
        lib.CONVERT_HEIC_TO_JPG = True
        mocker.patch("file_utils.convert_heic_to_jpg", return_value="TEST_HEIC.jpg")
        mocker.patch("file_utils.is_heic", return_value=True)
        pairs = {
            "TEST_HEIC": {
                "images": {"TEST_HEIC.HEIC"}
            }
        }
        lib.apply_fixes(pairs)
        assert pairs == {
            "TEST_HEIC": {
                "images": {"TEST_HEIC.jpg"}
            }
        }

