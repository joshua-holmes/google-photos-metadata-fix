import sys, os
import tools_for_testing as tft
sys.path.append("../")
import file_utils

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

