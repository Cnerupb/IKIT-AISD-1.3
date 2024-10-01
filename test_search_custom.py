import unittest
import search


class TestSearchCustom(unittest.TestCase):
    def test_last(self):
        string = "asda"
        sub_string = "a"
        print(f"string: {string}; sub_string: {sub_string}")
        search._search_last(string, sub_string)