# Query translator prototype

## Design decisions
1. Users will query using concepts from the CRDC-H model. Nested structures are
   denoted using a dot notation.
2. Users will get results in structures matching the CRDC-H model.
3. (R1) The API return structure will be a list of dictionaries, one per case,
   with keys and values matching the CRDC-H model.
4. In order to construct SQL that will work with BQ nested tables
    1. We use SELECT * . This allows us to maintain the nested data structure in
       the return without having to unnest the data (which leads to
       complications with column names).
    2. In the WHERE clause, when we need to UNNEST a nested column we alias it
       with a name that simply adds an underscore to the original name. This is
       completely internal and does not affect the returned data because of 1. 

## Example

_Note that this example does not use the CRDC-H model nomenclature, but the principles are
the same_

Query
> Select data from TCGA-OV project, with donors over age 50 with Stage IIIC cancer?

SQL
```
SELECT * FROM gdc-bq-sample.gdc_metadata.r24_clinical, UNNEST(demographic) as _demographic, UNNEST(diagnoses) as _diagnoses, UNNEST(project) as _project WHERE (((_demographic.age_at_index >= 50) AND (_project.project_id = 'TCGA-OV')) AND (_diagnoses.figo_stage = 'Stage IIIC'))
```

It can be verified that the return JSON maintains the original nested structure
of the data

# How to experiment

1. Clone this repository
1. `pip install -e .`
1. `jupyter notebook`
1. Run the example notebook
