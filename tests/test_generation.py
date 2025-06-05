"""Tests to ensure proper development of py-allotax."""

import os

from py_allotax.generate_svg import generate_svg


def test_generation():
    generate_svg(
        os.path.join("example_data", "boys_2022.json"),
        os.path.join("example_data", "boys_2023.json"),
        os.path.join("tests", "test.pdf"),
        "0.17",
        "Boys 2022",
        "Boys 2023"
    )

    pdf_path = os.path.join("tests", "test.pdf")
    html_path = os.path.join("tests", "test.html")

    assert(os.path.exists(pdf_path))
    assert(os.path.exists(html_path))
