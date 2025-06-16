"""Tests to ensure proper development of py-allotax."""

import os

from py_allotax.generate_svg import generate_svg


def test_generation():
    generate_svg(
        os.path.join("example_data", "boys_1895.json"),  # 1st
        os.path.join("example_data", "boys_1968.json"),  # 2nd
        os.path.join("tests", "test.pdf"),               # 3rd
        "0.17",                                          # 4th
        "Baby boy names 1895",                           # 5th
        "Baby boy names 1968",                           # 6th
        "pdf"                                            # 7th - desired_format
    )

    pdf_path = os.path.join("tests", "test.pdf")
    html_path = os.path.join("tests", "test.html")

    assert os.path.exists(pdf_path)
    assert os.path.exists(html_path)