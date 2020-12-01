import json
from typing import Union, List

from google.cloud import bigquery


class Column:
    def __init__(self, s):
        self.s = s

    def __str__(self):
        if self.parent() is not None:
            return "_" + self.s
        else:
            return self.s

    def parent(self):
        _parts = self.s.split(".")
        if len(_parts) > 1:
            return _parts[0]
        else:
            return None


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


class Condition:
    def __init__(self, col: Column, operator: str, value: Value):
        self.left = col if isinstance(col, (Column, Condition)) else Column(col)
        self.operator = operator
        self.right = value if isinstance(value, (Value, Condition)) else Value(value)

    def _unnest_recurse(self, term: Union[Column, 'Condition']):
        if isinstance(term, Column):
            return [term.parent()]
        elif isinstance(self.left, Condition):
            return term.columns_to_unnest()
        else:
            return []

    def columns_to_unnest(self):
        return self._unnest_recurse(self.left) + \
            self._unnest_recurse(self.right)

    def And(self, right: 'Condition'):
        return Condition(self, "AND", right)

    def Or(self, right: 'Condition'):
        return Condition(self, "OR", right)

    def __str__(self):
        return f"({self.left} {self.operator} {self.right})"


class Dataset:
    def __init__(self, client, table: str):
        self.client = bigquery.Client()
        self.table = table
        self._columns = None

    def sql(self, cond: Condition):
        from_clause = ", ".join(
            [self.table] +
            [f"UNNEST({u}) AS _{u}"
             for u in set(cond.columns_to_unnest()) if u is not None])
        return f"SELECT * FROM {from_clause} WHERE {cond}"

    def query(self, cond: Condition):
        return self.client.query(self.sql(cond)).result()

    def columns(self):
        _parts = self.table.split(".")
        dataset_name = _parts[:2]
        table_name = _parts[2]
        query = ("SELECT field_path "
                 f"FROM `{'.'.join(dataset_name)}"
                 ".INFORMATION_SCHEMA.COLUMN_FIELD_PATHS`"
                 f" WHERE table_name = '{table_name}'")
        return [r.field_path for r in self.client.query(query)]

    def unique_values_for(self, column: Column):
        clause = f"`{self.table}`"
        if column.parent() is not None:
            clause += f", UNNEST({column.parent()}) as _{column.parent()}"

        sql = f"SELECT DISTINCT({column}) FROM {clause} ORDER BY {column} ASC"
        return [v.values()[0] for v in self.client.query(sql)]
