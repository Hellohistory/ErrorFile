import bz2
import gzip
import json
import shutil
import tarfile
import tempfile
import unittest
import zipfile
from pathlib import Path

import py7zr
from ErrorFile import inspect_file
from PIL import Image
from PyPDF2 import PdfWriter
from docx import Document
from openpyxl import Workbook
from pptx import Presentation
from tests.good_xls_bytes import GOOD_XLS_BYTES
from tests.sample_binary_assets import (
    GOOD_FLAC_BYTES,
    GOOD_MP3_BYTES,
    GOOD_MP4_BYTES,
    GOOD_OGG_BYTES,
    GOOD_RAR_BYTES,
)

SVG_SAMPLE = (
    "<svg xmlns='http://www.w3.org/2000/svg' width='10' height='10'>"
    "<rect width='10' height='10' fill='red'/></svg>"
)


class TestFileInspector(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.mkdtemp(prefix="errorfile-tests-")
        cls.good_files = {}
        cls.bad_files = {}
        cls.image_extensions = [
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".bmp",
            ".webp",
            ".tiff",
            ".svg",
        ]
        cls._prepare_image_files()
        cls._prepare_pdf_files()
        cls._prepare_excel_files()
        cls._prepare_docx_files()
        cls._prepare_pptx_files()
        cls._prepare_zip_files()
        cls._prepare_rar_files()
        cls._prepare_compressed_files()
        cls._prepare_text_files()
        cls._prepare_media_files()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.temp_dir, ignore_errors=True)

    @classmethod
    def _register(cls, ext, good_path, bad_path):
        cls.good_files[ext] = str(good_path)
        cls.bad_files[ext] = str(bad_path)

    @classmethod
    def _prepare_image_files(cls):
        format_mapping = {
            ".jpg": "JPEG",
            ".jpeg": "JPEG",
            ".png": "PNG",
            ".gif": "GIF",
            ".bmp": "BMP",
            ".webp": "WEBP",
            ".tiff": "TIFF",
        }
        for ext in cls.image_extensions:
            good_path = Path(cls.temp_dir) / f"good_image{ext}"
            bad_path = Path(cls.temp_dir) / f"bad_image{ext}"
            if ext == ".svg":
                good_path.write_text(SVG_SAMPLE, encoding="utf-8")
                bad_path.write_text("not an svg", encoding="utf-8")
            else:
                image = Image.new("RGB", (10, 10), color="red")
                fmt = format_mapping[ext]
                if fmt == "GIF":
                    image = image.convert("P")
                image.save(good_path, format=fmt)
                bad_path.write_bytes(b"not a valid image file")
            cls._register(ext, good_path, bad_path)

    @classmethod
    def _prepare_pdf_files(cls):
        good_path = Path(cls.temp_dir) / "good.pdf"
        bad_path = Path(cls.temp_dir) / "bad.pdf"
        writer = PdfWriter()
        writer.add_blank_page(width=72, height=72)
        with open(good_path, "wb") as file:
            writer.write(file)
        bad_path.write_text("not a pdf", encoding="utf-8")
        cls._register(".pdf", good_path, bad_path)

    @classmethod
    def _prepare_excel_files(cls):
        # .xlsx
        good_xlsx = Path(cls.temp_dir) / "good.xlsx"
        bad_xlsx = Path(cls.temp_dir) / "bad.xlsx"
        workbook = Workbook()
        sheet = workbook.active
        sheet["A1"] = "ok"
        workbook.save(good_xlsx)
        bad_xlsx.write_text("not an xlsx", encoding="utf-8")
        cls._register(".xlsx", good_xlsx, bad_xlsx)

        # .xls
        good_xls = Path(cls.temp_dir) / "good.xls"
        bad_xls = Path(cls.temp_dir) / "bad.xls"
        good_xls.write_bytes(GOOD_XLS_BYTES)
        bad_xls.write_text("not an xls", encoding="utf-8")
        cls._register(".xls", good_xls, bad_xls)

    @classmethod
    def _prepare_docx_files(cls):
        good_path = Path(cls.temp_dir) / "good.docx"
        bad_path = Path(cls.temp_dir) / "bad.docx"
        document = Document()
        document.add_paragraph("hello world")
        document.save(good_path)
        bad_path.write_text("not a docx", encoding="utf-8")
        cls._register(".docx", good_path, bad_path)

    @classmethod
    def _prepare_pptx_files(cls):
        good_path = Path(cls.temp_dir) / "good.pptx"
        bad_path = Path(cls.temp_dir) / "bad.pptx"
        presentation = Presentation()
        slide_layout = presentation.slide_layouts[5]
        presentation.slides.add_slide(slide_layout)
        presentation.save(good_path)
        bad_path.write_text("not a pptx", encoding="utf-8")
        cls._register(".pptx", good_path, bad_path)

    @classmethod
    def _prepare_zip_files(cls):
        good_path = Path(cls.temp_dir) / "good.zip"
        bad_path = Path(cls.temp_dir) / "bad.zip"
        with zipfile.ZipFile(good_path, "w") as archive:
            archive.writestr("hello.txt", "zip ok")
        bad_path.write_text("not a zip", encoding="utf-8")
        cls._register(".zip", good_path, bad_path)

    @classmethod
    def _prepare_rar_files(cls):
        good_path = Path(cls.temp_dir) / "good.rar"
        bad_path = Path(cls.temp_dir) / "bad.rar"
        good_path.write_bytes(GOOD_RAR_BYTES)
        bad_path.write_text("not a rar", encoding="utf-8")
        cls._register(".rar", good_path, bad_path)

    @classmethod
    def _prepare_compressed_files(cls):
        gzip_good = Path(cls.temp_dir) / "good.gz"
        gzip_bad = Path(cls.temp_dir) / "bad.gz"
        with gzip.open(gzip_good, "wb") as gzip_file:
            gzip_file.write(b"gzip ok")
        gzip_bad.write_text("not a gzip", encoding="utf-8")
        cls._register(".gz", gzip_good, gzip_bad)

        bzip_good = Path(cls.temp_dir) / "good.bz2"
        bzip_bad = Path(cls.temp_dir) / "bad.bz2"
        with bz2.BZ2File(bzip_good, "wb") as bzip_file:
            bzip_file.write(b"bz2 ok")
        bzip_bad.write_text("not a bz2", encoding="utf-8")
        cls._register(".bz2", bzip_good, bzip_bad)

        seven_zip_good = Path(cls.temp_dir) / "good.7z"
        seven_zip_bad = Path(cls.temp_dir) / "bad.7z"
        payload_txt = Path(cls.temp_dir) / "archive_payload.txt"
        payload_txt.write_text("archive ok", encoding="utf-8")
        with py7zr.SevenZipFile(seven_zip_good, "w") as archive:
            archive.write(payload_txt, arcname="payload.txt")
        seven_zip_bad.write_text("not a 7z", encoding="utf-8")
        cls._register(".7z", seven_zip_good, seven_zip_bad)

        tar_payload = Path(cls.temp_dir) / "tar_payload.txt"
        tar_payload.write_text("tar ok", encoding="utf-8")

        tar_good = Path(cls.temp_dir) / "good.tar"
        tar_bad = Path(cls.temp_dir) / "bad.tar"
        cls._create_tar_archive(tar_good, "w", tar_payload)
        tar_bad.write_text("not a tar", encoding="utf-8")
        cls._register(".tar", tar_good, tar_bad)

        tar_gz_good = Path(cls.temp_dir) / "good.tar.gz"
        tar_gz_bad = Path(cls.temp_dir) / "bad.tar.gz"
        cls._create_tar_archive(tar_gz_good, "w:gz", tar_payload)
        tar_gz_bad.write_text("not a tar.gz", encoding="utf-8")
        cls._register(".tar.gz", tar_gz_good, tar_gz_bad)

        tar_bz2_good = Path(cls.temp_dir) / "good.tar.bz2"
        tar_bz2_bad = Path(cls.temp_dir) / "bad.tar.bz2"
        cls._create_tar_archive(tar_bz2_good, "w:bz2", tar_payload)
        tar_bz2_bad.write_text("not a tar.bz2", encoding="utf-8")
        cls._register(".tar.bz2", tar_bz2_good, tar_bz2_bad)

    @classmethod
    def _create_tar_archive(cls, path: Path, mode: str, payload: Path) -> None:
        with tarfile.open(path, mode) as tar:
            tar.add(payload, arcname="payload.txt")

    @classmethod
    def _prepare_media_files(cls):
        mp3_path = Path(cls.temp_dir) / "good.mp3"
        bad_mp3 = Path(cls.temp_dir) / "bad.mp3"
        mp3_path.write_bytes(GOOD_MP3_BYTES)
        bad_mp3.write_text("not an mp3", encoding="utf-8")
        cls._register(".mp3", mp3_path, bad_mp3)

        mp4_path = Path(cls.temp_dir) / "good.mp4"
        bad_mp4 = Path(cls.temp_dir) / "bad.mp4"
        mp4_path.write_bytes(GOOD_MP4_BYTES)
        bad_mp4.write_text("not an mp4", encoding="utf-8")
        cls._register(".mp4", mp4_path, bad_mp4)

        flac_path = Path(cls.temp_dir) / "good.flac"
        bad_flac = Path(cls.temp_dir) / "bad.flac"
        flac_path.write_bytes(GOOD_FLAC_BYTES)
        bad_flac.write_text("not a flac", encoding="utf-8")
        cls._register(".flac", flac_path, bad_flac)

        ogg_path = Path(cls.temp_dir) / "good.ogg"
        bad_ogg = Path(cls.temp_dir) / "bad.ogg"
        ogg_path.write_bytes(GOOD_OGG_BYTES)
        bad_ogg.write_text("not an ogg", encoding="utf-8")
        cls._register(".ogg", ogg_path, bad_ogg)

    @classmethod
    def _prepare_text_files(cls):
        json_good = Path(cls.temp_dir) / "good.json"
        json_bad = Path(cls.temp_dir) / "bad.json"
        json_good.write_text(json.dumps({"status": "ok", "value": 1}), encoding="utf-8")
        json_bad.write_text('{"status": }', encoding="utf-8")
        cls._register(".json", json_good, json_bad)

        xml_good = Path(cls.temp_dir) / "good.xml"
        xml_bad = Path(cls.temp_dir) / "bad.xml"
        xml_good.write_text("<root><item>ok</item></root>", encoding="utf-8")
        xml_bad.write_text("<root>", encoding="utf-8")
        cls._register(".xml", xml_good, xml_bad)

    def test_good_images(self):
        for ext in self.image_extensions:
            with self.subTest(ext=ext):
                is_ok, message = inspect_file(self.good_files[ext], mode="precise")
                self.assertTrue(is_ok, f"{ext} 图片应通过检查: {message}")

    def test_corrupted_images(self):
        for ext in self.image_extensions:
            with self.subTest(ext=ext):
                is_ok, message = inspect_file(self.bad_files[ext], mode="precise")
                self.assertFalse(is_ok, f"{ext} 损坏图片不应通过检查: {message}")

    def test_pdf_files(self):
        good_path = self.good_files[".pdf"]
        bad_path = self.bad_files[".pdf"]
        is_ok, message = inspect_file(good_path)
        self.assertTrue(is_ok, f"PDF 应通过检查: {message}")
        is_ok, message = inspect_file(bad_path)
        self.assertFalse(is_ok, "损坏的 PDF 不应通过检查")

    def test_excel_files(self):
        for ext in (".xlsx", ".xls"):
            with self.subTest(ext=ext):
                is_ok, message = inspect_file(self.good_files[ext])
                self.assertTrue(is_ok, f"{ext} 应通过检查: {message}")
                is_ok, message = inspect_file(self.bad_files[ext])
                self.assertFalse(is_ok, f"损坏的 {ext} 不应通过检查")

    def test_docx_files(self):
        is_ok, message = inspect_file(self.good_files[".docx"])
        self.assertTrue(is_ok, f"DOCX 应通过检查: {message}")
        is_ok, message = inspect_file(self.bad_files[".docx"])
        self.assertFalse(is_ok, "损坏的 DOCX 不应通过检查")

    def test_pptx_files(self):
        is_ok, message = inspect_file(self.good_files[".pptx"])
        self.assertTrue(is_ok, f"PPTX 应通过检查: {message}")
        is_ok, message = inspect_file(self.bad_files[".pptx"])
        self.assertFalse(is_ok, "损坏的 PPTX 不应通过检查")

    def test_zip_files(self):
        is_ok, message = inspect_file(self.good_files[".zip"])
        self.assertTrue(is_ok, f"ZIP 应通过检查: {message}")
        is_ok, message = inspect_file(self.bad_files[".zip"])
        self.assertFalse(is_ok, "损坏的 ZIP 不应通过检查")

    def test_rar_files(self):
        is_ok, message = inspect_file(self.good_files[".rar"])
        self.assertTrue(is_ok, f"RAR 应通过检查: {message}")
        is_ok, message = inspect_file(self.bad_files[".rar"])
        self.assertFalse(is_ok, "损坏的 RAR 不应通过检查")

    def test_compressed_files(self):
        for ext in (".gz", ".bz2", ".tar", ".tar.gz", ".tar.bz2", ".7z"):
            with self.subTest(ext=ext):
                is_ok, message = inspect_file(self.good_files[ext])
                self.assertTrue(is_ok, f"{ext} 应通过检查: {message}")
                is_ok, message = inspect_file(self.bad_files[ext])
                self.assertFalse(is_ok, f"损坏的 {ext} 不应通过检查")

    def test_text_files(self):
        for ext in (".json", ".xml"):
            with self.subTest(ext=ext):
                is_ok, message = inspect_file(self.good_files[ext])
                self.assertTrue(is_ok, f"{ext} 应通过检查: {message}")
                is_ok, message = inspect_file(self.bad_files[ext])
                self.assertFalse(is_ok, f"损坏的 {ext} 不应通过检查")

    def test_media_files(self):
        for ext in (".mp3", ".mp4", ".flac", ".ogg"):
            with self.subTest(ext=ext):
                is_ok, message = inspect_file(self.good_files[ext])
                self.assertTrue(is_ok, f"{ext} 应通过检查: {message}")
                is_ok, message = inspect_file(self.bad_files[ext])
                self.assertFalse(is_ok, f"损坏的 {ext} 不应通过检查")

    def test_invalid_mode(self):
        good_jpg = self.good_files[".jpg"]
        is_ok, message = inspect_file(good_jpg, mode="fast")
        self.assertFalse(is_ok)
        self.assertIn("仅支持", message)

    def test_non_existent_file(self):
        is_ok, message = inspect_file("non_existent_file_12345.xyz")
        self.assertFalse(is_ok)
        self.assertIn("文件未找到", message)


if __name__ == "__main__":
    unittest.main()
