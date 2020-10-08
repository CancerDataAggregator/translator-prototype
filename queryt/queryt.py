import json
from typing import Union, List

from google.cloud import bigquery


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
        elif self.s is None:
            return "NULL"
        else:
            return str(self.s)


class Dataset:
    def __init__(self, client, table: str, schema: dict):
        self.client = bigquery.Client()
        self.table = table
        self.unnest_dict = make_unnest_dictionary(schema)
        self._columns = None

    def columns(self):
        # This needs to be done in a more principled manner
        if self._columns is None:
            _d = self.schema()
            self._columns = [
                _row["column_name"]
                for _index, _row in _d.iterrows()
                if not _row["data_type"].startswith('ARRAY')
            ]
            self._columns += list(self.unnest_dict.keys())
            self._columns = sorted(self._columns)

        return self._columns

    def unique_values_for(self, column: Column):
        from_clause = f"`{self.table}`"
        if column in self.unnest_dict:
            from_clause += f", UNNEST({self.unnest_dict.get(column)})"

        sql = f"SELECT DISTINCT({column}) FROM {from_clause} ORDER BY {column} ASC"
        return [v[column] for v in self.client.query(sql)]

    def schema(self):
        # This will be the way to get the schema going forward
        # There is probably a better way to get the table name for this purpose
        _parts = self.table.split('.')
        _table_prefix = '.'.join(_parts[:-1])
        _table_name = _parts[-1]

        sql = f"SELECT * FROM `{_table_prefix}.INFORMATION_SCHEMA.COLUMNS` WHERE table_name='{_table_name}'"
        return self.client.query(sql).to_dataframe()


def make_unnest_dictionary(schema: dict):
    unnest_dictionary = {}
    for v in schema["fields"]:
        if v["type"] != "RECORD":
            continue

        for field in v["fields"]:
            unnest_dictionary[field["name"]] = v["name"]
    return unnest_dictionary


class Condition:
    def __init__(self, col: Column, operator: str, value: Value):
        self.left = col if isinstance(col, (Column, Condition)) else Column(col)
        self.operator = operator
        self.right = value if isinstance(value, (Value, Condition)) else Value(value)

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

    def sql(self, columns: List[Column], dataset: Dataset):
        unnest = set()
        for c in columns + self.columns():
            if c in dataset.unnest_dict:
                unnest.add(dataset.unnest_dict.get(c))

        select = ", ".join(columns)
        from_clause = ", ".join([dataset.table] + [f"unnest({u})" for u in list(unnest)])
        return f"SELECT {select} FROM {from_clause} WHERE {self}"

    def as_df(self, columns: List[Column], dataset: Dataset):
        return dataset.client.query(self.sql(columns, dataset)).to_dataframe()
