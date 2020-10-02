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


class Condition:
    def __init__(self, col: Column, operator: str, value: Value):
        self.left = col
        self.operator = operator
        self.right = value

    def columns(self):
        _cols = []
        if isinstance(self.left, Column):
            _cols += [self.left.s]
        elif isinstance(self.left, Condition):
            _cols += self.left.columns()

        if isinstance(self.right, Column):
            _cols += [self.right.s]
        elif isinstance(self.right, Condition):
            _cols += self.right.columns()

        return _cols

    def And(self, right: 'Condition'):
        return Condition(self, "AND", right)

    def Or(self, right: 'Condition'):
        return Condition(self, "OR", right)

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

    def translate(self, select: Select, condition: Condition):
        unnest = set()
        for c in select.columns + condition.columns():
            if c in self.unnest_dict:
                unnest.add(self.unnest_dict.get(c))

        from_clause = ", ".join([self.table] + [f"unnest({u})" for u in list(unnest)])
        return f"SELECT {select} FROM {from_clause} WHERE {condition}"
