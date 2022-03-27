# majority-judgment-tracker
This repository is a simple tool for tracking the progress of opinion with majority-judgment.
It provides elegant plots such as merit profiles, merit profile evolutions.

The database is a simple .csv file which contains polls compatible with the majority judgment rules:
`presidentielle_jm.csv`

The number of grades depends of the survey (4,5,6). An AggregationMode Enum is provided to choose the aggregation mode.
The mapping to a common system of grades is provided in the `standardisation.csv` file.




