import unittest
import os

from ErrorFile import inspect_file


class TestFileInspector(unittest.TestCase):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    FILES_DIR = os.path.join(BASE_DIR, 'files')

    def test_good_image(self):
        """测试一个完好的图片文件"""
        good_image_path = os.path.join(self.FILES_DIR, 'good_image.png')
        self.assertTrue(os.path.exists(good_image_path), "测试文件 good_image.png 不存在")
        is_ok, message = inspect_file(good_image_path, mode='precise')
        self.assertTrue(is_ok, f"一个完好的图片应该通过检查，但返回: {message}")

    def test_corrupted_image(self):
        """测试一个损坏的图片文件"""
        bad_image_path = os.path.join(self.FILES_DIR, 'TOM_损坏.jpg')
        self.assertTrue(os.path.exists(bad_image_path), "测试文件 TOM_损坏.jpg 不存在")
        is_ok, message = inspect_file(bad_image_path, mode='precise')
        self.assertFalse(is_ok, f"损坏的图片应该无法通过检查，但返回: {message}")

    def test_good_pdf(self):
        """测试一个完好的PDF文件"""
        good_pdf_path = os.path.join(self.FILES_DIR, 'good_document.pdf')
        self.assertTrue(os.path.exists(good_pdf_path), "测试文件 good_document.pdf 不存在")
        is_ok, message = inspect_file(good_pdf_path)
        self.assertTrue(is_ok, f"一个完好的PDF应该通过检查，但返回: {message}")

    def test_corrupted_excel(self):
        """测试一个损坏的Excel .xlsx文件"""
        bad_excel_path = os.path.join(self.FILES_DIR, '测试文件_损坏.xlsx')
        self.assertTrue(os.path.exists(bad_excel_path), "测试文件 测试文件_损坏.xlsx 不存在")
        is_ok, message = inspect_file(bad_excel_path)
        self.assertFalse(is_ok, "一个损坏的Excel文件应该无法通过检查")

    def test_non_existent_file(self):
        """测试一个不存在的文件"""
        is_ok, message = inspect_file('non_existent_file_12345.xyz')
        self.assertFalse(is_ok)
        self.assertIn("文件未找到", message)


if __name__ == '__main__':
    unittest.main()