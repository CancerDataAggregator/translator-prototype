# Query translator prototype

The query translator takes in query in the harmonized query tree format and 
generates a SQL where clause and relevant joins that are required to execute 
the query on the big query tables 

![](https://github.com/CancerDataAggregator/api/blob/master/images/CDA.png)

The prototype will be used to study

1. The algorithm to go from harmonized query tree to SQL query string
1. The coupling between this conversion and the table structure in the database
1. Python data structures for harmonized query tree
