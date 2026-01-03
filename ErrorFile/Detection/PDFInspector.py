# ErrorFile/Detection/PDFInspector.py

import PyPDF2
from PyPDF2.errors import PdfReadError

from ..report import (
    TAG_CORRUPTED,
    TAG_ENCRYPTED,
    TAG_INVALID_FORMAT,
    TAG_IO_ERROR,
    fail_finding,
    ok_finding,
)


class PDFInspector:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def _fast_check(self):
        try:
            with open(self.file_path, "rb") as file:
                header = file.read(5)
                if header != b"%PDF-":
                    return fail_finding(
                        "PDF header invalid.",
                        TAG_INVALID_FORMAT,
                    )

                reader = PyPDF2.PdfReader(file, strict=False)
                if reader.is_encrypted:
                    return fail_finding(
                        "PDF is encrypted; cannot inspect contents.",
                        TAG_ENCRYPTED,
                    )
                if len(reader.pages) == 0:
                    return fail_finding(
                        "PDF has no pages; file may be corrupted.",
                        TAG_CORRUPTED,
                    )

            return ok_finding("PDF fast check passed.")
        except PdfReadError as exc:
            return fail_finding(
                f"PDF read error: {exc}",
                TAG_CORRUPTED,
                error=str(exc),
            )
        except Exception as exc:
            return fail_finding(
                f"PDF fast check failed: {exc}",
                TAG_IO_ERROR,
                error=str(exc),
            )

    def _deep_check(self):
        try:
            with open(self.file_path, "rb") as file:
                reader = PyPDF2.PdfReader(file, strict=True)

                if reader.is_encrypted:
                    return fail_finding(
                        "PDF is encrypted; cannot inspect contents.",
                        TAG_ENCRYPTED,
                    )

                if len(reader.pages) == 0:
                    return fail_finding(
                        "PDF has no pages; file may be corrupted.",
                        TAG_CORRUPTED,
                    )

                for page in reader.pages:
                    page.get_contents()

        except PdfReadError as exc:
            lowered = str(exc).lower()
            if "encrypted" in lowered or "password" in lowered:
                return fail_finding(
                    f"PDF is encrypted and requires a password: {exc}",
                    TAG_ENCRYPTED,
                    error=str(exc),
                )
            if "xref" in lowered:
                return fail_finding(
                    f"PDF xref corrupted: {exc}",
                    TAG_CORRUPTED,
                    error=str(exc),
                )
            if "file has not been decrypted" in lowered:
                return fail_finding(
                    "PDF requires decryption to read contents.",
                    TAG_ENCRYPTED,
                )
            return fail_finding(
                f"PDF structure corrupted: {exc}",
                TAG_CORRUPTED,
                error=str(exc),
            )
        except Exception as exc:
            return fail_finding(
                f"PDF deep check failed: {exc}",
                TAG_IO_ERROR,
                error=str(exc),
            )

        return ok_finding("PDF deep check passed.")

    def check_pdf(self, mode: str):
        """Check PDF in fast or deep mode."""
        if mode == "fast":
            return self._fast_check()
        return self._deep_check()
