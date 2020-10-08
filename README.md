# Query translator prototype

The query translator takes in query in the harmonized query tree format and 
generates a SQL where clause and relevant joins that are required to execute 
the query on the big query tables 

The prototype will be used to study

1. The algorithm to go from harmonized query tree to SQL query string
1. The coupling between this conversion and the table structure in the database
1. Python data structures for API bindings

Please see this [notebook](CDA-MVP-Query-examples.ipynb) to see how some of the
CDA MVP queries can be written and how ISB's nested tables can be queried.

How to experiment:

1. Clone this repository
2. `pip install -e .` 
3. `jupyter notebook`
4. Run the example notebook below
