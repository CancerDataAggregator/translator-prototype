from queryt import *

w1 = Where(Column('age_at_index'), '>=', Value(50))
w2 = Where(Column('project_id'), 'like', Value('TCGA%'))
w3 = Where(Column('figo_stage'), '=', Value('Stage IIIC'))

w4 = Where(w1, 'and', w2)
w5 = Where(w4, 'and', w3)

s = Select(['case_id', 'age_at_index', 'gender', 'race', 'project_id', 'figo_stage'])

q = Query(table="gdc-bq-sample.gdc_metadata.r24_clinical")

print(q.translate(s, w5))
