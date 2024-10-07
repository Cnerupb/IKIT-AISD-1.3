"""Search module"""

import argparse
import os
import random
import time
from typing import Union, Optional

from rich.console import Console

def time_of_function(function):
    """
    Counts time of function runtime in seconds
    :param function: function to count
    :return: None
    """
    def wrapped(*args):
        start_time = time.perf_counter_ns()
        res = function(*args)
        end_time = time.perf_counter_ns()
        run_time = (end_time - start_time) / 10**9
        print(f'Run time: {run_time:.9f} seconds')
        return res
    return wrapped


@time_of_function
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
        """Search function. Uses KMP algorithm"""
        result = {}.fromkeys(self._sub_string)
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
            elif (i < string_len
                  and sub_string[sub_string_len - 1 - j] != self._string[string_len - 1 - i]):
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
        if len(result) == 1:
            result = result[list(result.keys())[0]]
            if not result:
                return None
            return result

        all_are_none = all(sub_res is None for sub_res in result.values())
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
            if not all(isinstance(sub_str, str) for sub_str in sub_string):
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
    """Class used for parsing args from CLI"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_argument('string',
                          type=self._check_string,
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
        print(value)
        if os.path.isabs(value):
            try:
                with open(value, 'r', encoding='utf-8') as f:
                    return f.read()
            except FileNotFoundError as exc:
                raise argparse.ArgumentTypeError('File not found') from exc
            except PermissionError as exc:
                raise argparse.ArgumentTypeError('Permission denied') from exc
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
        except ValueError as exc:
            raise argparse.ArgumentTypeError("count must be natural number or None") from exc


class _ResultPrinter:
    """Class used for printing colored result."""

    def __init__(self,
                 result: Optional[Union[tuple[int, ...], dict[str, tuple[int, ...]]]],
                 string: str,
                 sub_string: Union[str, list[str]]):
        self._result = result
        self._string = string
        self._sub_string = sub_string

        if isinstance(self._sub_string, str):
            self._sub_string: list[str] = [self._sub_string]

    def print(self):
        """Prints colored result to Console."""
        if self._result is None:
            self._print_none()
        if isinstance(self._result, tuple):
            self._print_tuple()
        if isinstance(self._result, dict):
            self._print_dict()

    def _print_none(self):
        console = Console()
        console.print(self._result)

    def _print_tuple(self):
        text_list = list(self._string)
        color = self.generate_colors(1)[0]
        for i in self._result:
            start_index = i
            end_index = i + len(self._sub_string) - 1
            text_list[start_index] = f'[{color}]{text_list[start_index]}'
            text_list[end_index] = f'{text_list[end_index]}[/{color}]'
        text = ''.join(text_list)
        first_10_lines = 'First 10 lines:\n'
        first_10_lines += '\n'.join(text.split('\n')[:10])
        console = Console()
        console.print(first_10_lines)

    def _print_dict(self):
        colors = (color
                  for color in self.generate_colors(len(self._result)))
        index_pairs_tuple = []
        # Считаем что нету подстрок, которые являются подстроками других подстрок
        for sub_str, index_tuple in self._result.items():
            sub_str_len = len(sub_str)
            if index_tuple:
                index_pairs_tuple.append(tuple((i, i + sub_str_len - 1)
                                                for i in index_tuple))
            else:
                index_pairs_tuple.append(tuple())
        index_pairs_tuple = tuple(index_pairs_tuple)

        text_list = list(self._string)
        for pairs_tuple, color in zip(index_pairs_tuple, colors): # print colorized
            for pair in pairs_tuple:
                start_index = pair[0]
                end_index = pair[1]
                text_list[start_index] = f'[{color}]{text_list[start_index]}'
                text_list[end_index] = f'{text_list[end_index]}[/{color}]'
        text = ''.join(text_list)
        first_10_lines = 'First 10 lines:\n'
        first_10_lines += '\n'.join(text.split('\n')[:10])
        console = Console()
        console.print(first_10_lines)

    @staticmethod
    def generate_colors(number_of_colors: int) -> list[str]:
        """
        Generates colors list of HEX format.
        :param number_of_colors: number of colors to generate. Maximus is 1.7 million
        :return: list of colors in string format
        """
        if not isinstance(number_of_colors, int):
            raise TypeError('number_of_colors must be of type int')
        if number_of_colors > 1_700_000:
            raise ValueError("Number of colors must be less than 1.7 million")
        color_list = ["#" + ''.join([random.choice('0123456789ABCDEF')
                                     for j in range(6)])
                      for i in range(number_of_colors)]
        return color_list


if __name__ == '__main__':
    parser = _MyArgumentParser()
    args = parser.parse_args()

    result = search(args.string, args.sub_string, args.case_sensitivity, args.method, args.count)

    result_printer = _ResultPrinter(result, args.string, args.sub_string)
    result_printer.print()
