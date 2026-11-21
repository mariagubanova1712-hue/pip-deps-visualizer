"""Тесты разбора метаданных пакетов Python."""

import unittest

from depviz.pypi import (
    find_metadata_url,
    normalize,
    parse_metadata,
    parse_requirement,
)

METADATA = """Metadata-Version: 2.1
Name: demo
Version: 1.0
Requires-Dist: numpy>=1.25
Requires-Dist: python-dateutil>=2.7
Requires-Dist: pytest; extra == "test"

Описание пакета.
"""


class PypiTest(unittest.TestCase):
    """Проверка разбора зависимостей."""

    def test_normalize(self):
        """Имена приводятся к стандартному виду."""
        self.assertEqual(normalize("Typing_Extensions"), "typing-extensions")

    def test_parse_requirement(self):
        """Из строки зависимости берётся только имя."""
        cases = {
            "numpy>=1.25": "numpy",
            "idna<4,>=2.5": "idna",
            "PySocks!=1.5.7; extra == 'socks'": None,
            "colorama; sys_platform == 'win32'": "colorama",
            "zope.interface (>=5)": "zope-interface",
        }
        for line, expected in cases.items():
            self.assertEqual(parse_requirement(line), expected)

    def test_parse_metadata(self):
        """Строки Requires-Dist читаются из METADATA."""
        self.assertEqual(len(parse_metadata(METADATA)), 3)

    def test_find_metadata_url(self):
        """URL METADATA берётся у wheel-пакета."""
        files = [
            {"packagetype": "sdist", "url": "a.tar.gz"},
            {"packagetype": "bdist_wheel", "url": "a.whl",
             "core-metadata": {"sha256": "x"}},
        ]
        self.assertEqual(find_metadata_url(files), "a.whl.metadata")
        self.assertIsNone(find_metadata_url(files[:1]))


if __name__ == "__main__":
    unittest.main()
