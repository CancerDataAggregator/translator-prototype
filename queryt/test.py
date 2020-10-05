# Authenticate first: https://cloud.google.com/docs/authentication/getting-started

import json
from queryt import Column, Value, Dataset, Condition


schema = json.load(open("schema.json", "r"))["schema"]
dataset = Dataset(table="gdc-bq-sample.gdc_metadata.r24_clinical", schema=schema)

c1 = Condition(Column('age_at_index'), '>=', Value(50))
c2 = Condition(Column('project_id'), 'like', Value('TCGA%'))
c3 = Condition(Column('figo_stage'), '=', Value('Stage IIIC'))

columns = ['case_id', 'age_at_index', 'gender', 'race', 'project_id', 'figo_stage']
print(c1.And(c2).And(c3).translate(columns, dataset))


from google.cloud import bigquery

client = bigquery.Client()
query_job = client.query(c1.And(c2).And(c3).translate(columns, dataset))
