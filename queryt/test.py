from queryt import Column, Value, Condition, Select, Query

q = Query(table="gdc-bq-sample.gdc_metadata.r24_clinical")
s = Select(['case_id', 'age_at_index', 'gender', 'race', 'project_id', 'figo_stage'])

c1 = Condition(Column('age_at_index'), '>=', Value(50))
c2 = Condition(Column('project_id'), 'like', Value('TCGA%'))
c3 = Condition(Column('figo_stage'), '=', Value('Stage IIIC'))

print(q.translate(s, c1.And(c2).And(c3)))
