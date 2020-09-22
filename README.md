# Query translator prototype

The query translator takes in query in the harmonized query tree format and 
generates a SQL where clause and relevant joins that are required to execute 
the query on the big query tables 

The prototype will be used to study

1. The algorithm to go from harmonized query tree to SQL query string
1. The coupling between this conversion and the table structure in the database
1. Python data structures for harmonized query tree

The current (2020.09.22) prototype demonstrates query translation of a query
from boolean tree to SQL on nested table. 

The example in [test.py](test.py)

```
from queryt import *

w1 = Where(Column('age_at_index'), '>=', Value(50))
w2 = Where(Column('project_id'), 'like', Value('TCGA%'))
w3 = Where(Column('figo_stage'), '=', Value('Stage IIIC'))

w4 = Where(w1, 'and', w2)
w5 = Where(w4, 'and', w3)

s = Select(['case_id', 'age_at_index', 'gender', 'race', 'project_id', 'figo_stage'])

q = Query(table="gdc-bq-sample.gdc_metadata.r24_clinical")

print(q.translate(s, w5))
```

Results in the following SQL

```
SELECT case_id, age_at_index, gender, race, project_id, figo_stage FROM gdc-bq-sample.gdc_metadata.r24_clinical, unnest(demographic), unnest(project), unnest(diagnoses) WHERE (((age_at_index >= 50) and (project_id like 'TCGA%')) and (figo_stage = 'Stage IIIC'))
```
