import json
from typing import Union


class Column:
    def __init__(self, s):
        self.s = s

    def __str__(self):
        return self.s


class Value:
    def __init__(self, s):
        self.s = s

    def __str__(self):
        if isinstance(self.s, str):
            return f"'{self.s}'"
        else:
            return str(self.s)


class Where:
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

    def columns(self):
        _cols = []
        if isinstance(self.left, Column):
            _cols += [self.left.s]
        elif isinstance(self.left, Where):
            _cols += self.left.columns()

        if isinstance(self.right, Column):
            _cols += [self.right.s]
        elif isinstance(self.right, Where):
            _cols += self.right.columns()

        return _cols

    def __str__(self):
        return f"({self.left} {self.operator} {self.right})"


class Select:
    def __init__(self, columns):
        self.columns = columns

    def __str__(self):
        return ", ".join(self.columns)


def make_unnest_dictionary(schema: dict):
    unnest_dictionary = {}
    for v in schema["fields"]:
        if v["type"] != "RECORD":
            continue

        for field in v["fields"]:
            unnest_dictionary[field["name"]] = v["name"]
    return unnest_dictionary


class Query:
    def __init__(self, table: str):
        self.table = table
        schema = json.load(open("schema.json", "r"))["schema"]
        self.unnest_dict = make_unnest_dictionary(schema)

    def translate(self, select: Select, where: Where):
        from_components = [self.table]
        for c in where.columns():
            if c in self.unnest_dict:
                from_components += [f"unnest({self.unnest_dict.get(c)})"]

        from_clause = ", ".join(from_components)
        return f"SELECT {select} FROM {from_clause} WHERE {where}"
