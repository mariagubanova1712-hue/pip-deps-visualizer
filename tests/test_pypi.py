"""Тесты разбора зависимостей пакетов Python."""

import unittest

from depviz.pypi import normalize, parse_requirement


class PypiTest(unittest.TestCase):
    """Проверка разбора строк зависимостей."""

    def test_normalize(self):
        """Имена приводятся к одному виду."""
        self.assertEqual(normalize("Typing_Extensions"), "typing-extensions")
        self.assertEqual(normalize("zope.interface"), "zope-interface")

    def test_parse_requirement(self):
        """Из строки зависимости берётся только имя."""
        cases = {
            "numpy>=1.25": "numpy",
            "idna<4,>=2.5": "idna",
            "PySocks!=1.5.7; extra == 'socks'": None,
            "colorama; sys_platform == 'win32'": "colorama",
            "zope.interface (>=5)": "zope-interface",
            "pydantic-extra-types>=2": "pydantic-extra-types",
        }
        for line, expected in cases.items():
            self.assertEqual(parse_requirement(line), expected)


if __name__ == "__main__":
    unittest.main()
