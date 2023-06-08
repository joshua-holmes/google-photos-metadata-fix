import os, sys, json
from datetime import datetime

import filedate, platform

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

class TestApplyFileFixes:
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

