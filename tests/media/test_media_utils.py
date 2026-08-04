from __future__ import annotations

from app.media.utils import calculate_sha256, detect_extension, detect_mime_type, sanitize_filename


def test_hash_calculation() -> None:
    assert calculate_sha256(b"bertele2") == "2e4e1a344e19d56797eb25bfff7718eceb046fa3f68fb963431aa0059faecc22"


def test_mime_detection_from_filename_and_content() -> None:
    assert detect_mime_type("image.png") == "image/png"
    assert detect_mime_type(content=b"%PDF-1.7") == "application/pdf"


def test_extension_detection() -> None:
    assert detect_extension("archive.tar.gz") == "gz"
    assert detect_extension(None, "image/jpeg") in {"jpg", "jpeg"}


def test_filename_sanitization() -> None:
    assert sanitize_filename("../My Report!.pdf") == "My_Report_.pdf"
    assert sanitize_filename("CON") == "CON_file"
    assert sanitize_filename("") == "media"
