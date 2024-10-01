"""Search module"""

import argparse
import re
from typing import Union, Optional


def search(string: str,
           sub_string: Union[str, list[str]],
           case_sensitivity: bool = False,
           method: str = 'first',
           count: Optional[int] = None
           ) -> Optional[Union[tuple[int, ...], dict[str, tuple[int, ...]]]]:
    """Search function"""
    kmp_alg = KMPAlgorithm(string, sub_string, case_sensitivity, method, count)
    return kmp_alg.search()


class KMPAlgorithm:
    """Class uses Knuth-Morris-Pratt algorithm to search sub_strings in string"""
    def __init__(self,
                 string: str,
                 sub_string: Union[str, list[str]],
                 case_sensitivity: bool = False,
                 method: str = 'first',
                 count: Optional[int] = None):
        self._validate(string, sub_string, case_sensitivity, method, count)
        self._string = string
        self._sub_string = sub_string
        self._case_sensitivity = case_sensitivity
        self._method = method
        self._count = count

        if isinstance(sub_string, str):
            self._sub_string: list[str] = [sub_string]
        if not self._case_sensitivity:
            self._string = self._string.lower()
            self._sub_string = [sub_str.lower()
                                for sub_str in self._sub_string]

    def search(self) -> Optional[Union[tuple[int, ...], dict[str, tuple[int, ...]]]]:
        result = dict().fromkeys(self._sub_string)
        if self._method == 'first':
            for sub_str in self._sub_string:
                result[sub_str] = self._search_first(sub_str)
        else:
            for sub_str in self._sub_string:
                result[sub_str] = self._search_last(sub_str)
        result = self._convert_result(result)
        return result

    def _search_first(self, sub_string: str) -> Optional[tuple[int, ...]]:
        string_len = len(self._string)
        sub_string_len = len(sub_string)

        pi_list = self._get_pi_list(sub_string)
        result = []
        result_counter = 0
        # print(count)

        i = 0
        j = 0
        while (string_len - i) >= (sub_string_len - j):
            if sub_string[j] == self._string[i]:
                j += 1
                i += 1

            if j == sub_string_len:
                result.append(i - j)
                result_counter += 1
                if result_counter == self._count:
                    break
                j = pi_list[j - 1]
            elif i < string_len and sub_string[j] != self._string[i]:
                if j != 0:
                    j = pi_list[j - 1]
                else:
                    i += 1
        return tuple(result) if result else None

    def _search_last(self, sub_string: str) -> Optional[tuple[int, ...]]:
        string_len = len(self._string)
        sub_string_len = len(sub_string)

        pi_list = self._get_pi_list(sub_string)
        result = []
        result_counter = 0
        # print(count)

        i = 0
        j = 0
        while (string_len - i) >= (sub_string_len - j):
            if sub_string[sub_string_len - 1 - j] == self._string[string_len - 1 - i]:
                j += 1
                i += 1

            if j == sub_string_len:
                result.append(string_len - i)
                result_counter += 1
                if result_counter == self._count:
                    break
                j = pi_list[j - 1]
            elif i < string_len and sub_string[sub_string_len - 1 - j] != self._string[string_len - 1 - i]:
                if j != 0:
                    j = pi_list[j - 1]
                else:
                    i += 1
        return tuple(result) if result else None

    @staticmethod
    def _get_pi_list(sub_string: str) -> list[int]:
        sub_string_len = len(sub_string)
        pi_list = [0] * sub_string_len

        j = 0
        i = 1

        while i < sub_string_len:
            if sub_string[i] == sub_string[j]:
                j += 1
                pi_list[i] = j
                i += 1
            else:
                if j != 0:
                    j = pi_list[j - 1]
                else:
                    pi_list[i] = 0
                    i += 1
        return pi_list

    @staticmethod
    def _convert_result(result) -> Optional[Union[tuple[int, ...], dict[str, tuple[int, ...]]]]:
        if len(result) == 0:
            return None
        elif len(result) == 1:
            result = result[list(result.keys())[0]]
            if not result:
                return None
            return result
        else:
            all_are_none = all([sub_res is None
                                for sub_res in result.values()])
            if all_are_none:
                return None
            return result

    @staticmethod
    def _validate(string: str,
                  sub_string: Union[str, list[str]],
                  case_sensitivity: bool = False,
                  method: str = 'first',
                  count: Optional[int] = None):
        if not isinstance(string, str):
            raise TypeError('string must be of type str')

        if not isinstance(sub_string, str):
            if not isinstance(sub_string, (list, tuple)):
                raise TypeError('sub_string must be of type str')
            else:
                if not all([isinstance(sub_str, str)
                            for sub_str in sub_string]):
                    raise TypeError('sub_string list elements must be of type str')

        if not isinstance(case_sensitivity, bool):
            raise TypeError('case sensitivity must be of type bool')

        if not isinstance(method, str):
            raise TypeError('method must be of type str')
        if method not in ('first', 'last'):
            raise ValueError("method must be 'first' or 'last'")

        if not count is None:
            if not isinstance(count, int):
                raise TypeError('count must be of type int or None')
            if count < 1:
                raise ValueError("count must be greater than 0")


class _MyArgumentParser(argparse.ArgumentParser):
    """Class for parsing args from CLI"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_argument('string',
                          type=str,
                          help='String where search')
        self.add_argument('sub_string',
                          nargs='*',
                          type=str,
                          help='Substrings by which search')
        self.add_argument('-cs', '--case_sensitivity',
                          action='store_false',
                          help='Case sensitive search')
        self.add_argument('-m', '--method',
                          choices=('first', 'last'),
                          default='first',
                          type=str,
                          help='Search method')
        self.add_argument('-c', '--count',
                          type=self._check_count,
                          default=None,
                          help='How many results to return for each substring')

    @staticmethod
    def _check_string(value: str) -> str:
        if re.match(r'^(.+)\/([^\/]+)$', value):
            try:
                with open(value, 'r') as f:
                    return f.read()
            except FileNotFoundError:
                raise argparse.ArgumentTypeError('File not found')
            except PermissionError:
                raise argparse.ArgumentTypeError('Permission denied')
        return value

    @staticmethod
    def _check_count(value: Optional[str]) -> Optional[int]:
        if value is None:
            return value
        try:
            int_value = int(value)
            if int_value < 1:
                raise argparse.ArgumentTypeError("count must be greater than 0")
            return int_value
        except ValueError:
            raise argparse.ArgumentTypeError("count must be natural number or None")


if __name__ == '__main__':
    parser = _MyArgumentParser()
    args = parser.parse_args()

    print(search(args.string, args.sub_string, args.case_sensitivity, args.method, args.count))
