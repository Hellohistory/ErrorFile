# ErrorFile/Detection/ImageInspector_precise.py

from PIL import Image

from ..report import TAG_CORRUPTED, TAG_INVALID_FORMAT, TAG_IO_ERROR, fail_finding, ok_finding


class ImageInspector:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def check_image(self, mode: str):
        """Check image integrity in fast or deep mode."""
        try:
            with Image.open(self.file_path) as img:
                img.verify()

            if mode == "fast":
                return ok_finding("Image fast check passed.")

            with Image.open(self.file_path) as img_load:
                img_load.load()

            return ok_finding("Image deep check passed.")
        except (IOError, SyntaxError, Image.DecompressionBombError) as exc:
            return fail_finding(
                f"Image file corrupted or invalid: {exc}",
                TAG_CORRUPTED,
                TAG_INVALID_FORMAT,
                error=str(exc),
            )
        except Exception as exc:
            return fail_finding(
                f"Image check failed with unexpected error: {exc}",
                TAG_IO_ERROR,
                error=str(exc),
            )

    def detailed_check_image(self):
        """Backwards-compatible deep check."""
        return self.check_image("deep")
