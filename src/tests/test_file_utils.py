import sys, os, shutil, pathlib
import tools_for_testing as tft
sys.path.append("../")
import file_utils

from tests.tools_for_testing import CUR_DIR


class TestConvertHeicToJpg:
    @classmethod
    def setup_class(cls):
        cls.img_path = tft.import_file("TEST_HEIC.HEIC", "TestConvertHeicToJpg")

    @classmethod
    def test_convert_heic_to_jpg(cls):
        assert file_utils.is_heic(cls.img_path)
        cls.new_img_path = file_utils.convert_heic_to_jpg(cls.img_path)
        assert not file_utils.is_heic(cls.new_img_path)

    @classmethod
    def teardown_class(cls):
        if os.path.exists(cls.img_path):
            os.remove(cls.img_path)
        if hasattr(cls, "new_img_path") and os.path.exists(cls.new_img_path):
            os.remove(cls.new_img_path)

class TestFixExtension:
    @classmethod
    def setup_class(cls):
        cls.right_img_path = tft.import_file("TEST_JPG.jpg", "TestFixExtension")
        cls.wrong_img_path = cls.right_img_path[:-3] + "png"
        os.rename(cls.right_img_path, cls.wrong_img_path)

    @classmethod
    def test_fix_extension(cls):
        result = file_utils.fix_incorrect_extension(cls.wrong_img_path)
        assert result == cls.right_img_path

    @classmethod
    def teardown_class(cls):
        for img_path in [cls.wrong_img_path, cls.right_img_path]:
            if os.path.exists(img_path):
                os.remove(img_path)

class TestGroupFilesByName:
    def test_edited_images(self):
        files = ["COOLNAME.jpg", "COOLNAME-edited.jpg"]
        result = file_utils.group_files_by_name(files)
        assert result[""]["COOLNAME"]["images"] == set(files)

    def test_images_with_different_names(self):
        files = ["COOLNAME.jpg", "OTHERNAME.jpg"]
        result = file_utils.group_files_by_name(files)
        assert result[""]["COOLNAME"]["images"] == set([files[0]])
        assert result[""]["OTHERNAME"]["images"] == set([files[1]])

    def test_image_groups_with_json(self):
        files = ["COOLNAME.jpg", "COOLNAME.jpg.json", "OTHERNAME.jpg"]
        result = file_utils.group_files_by_name(files)
        assert result[""]["COOLNAME"] == {
            "images": {"COOLNAME.jpg"},
            "json": "COOLNAME.jpg.json"
        }

    def test_images_from_different_directories(self):
        files = ["/some/directory/COOLNAME.jpg", "/another/directory/COOLNAME.jpg.json"]
        result = file_utils.group_files_by_name(files)
        assert result["/some/directory"]["COOLNAME"] == {
            "images": {"COOLNAME.jpg"}
        }
        assert result["/another/directory"]["COOLNAME"] == {
            "json": "COOLNAME.jpg.json"
        }


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
        cls.file_paths = file_utils.get_file_paths(cls.zip_path)

    def test_get_files_paths_from_zip(self):
        assert self.file_paths == [
            f"{CUR_DIR}/{self.zip_prefix}/Takeout/Google Photos/JPGs/TEST_JPG.jpg",
            f"{CUR_DIR}/{self.zip_prefix}/Takeout/Google Photos/HEICs/TEST_HEIC.HEIC"
        ]

    @classmethod
    def teardown_class(cls):
        os.remove(cls.zip_path)
        tft.remove_dir(f"{CUR_DIR}/{cls.zip_prefix}")

