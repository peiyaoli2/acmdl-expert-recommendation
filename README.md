# acmdl-expert-recommendation
UIUC CS510 final project

## Dependencies
metapy

nltk

numpy

## Dataset
ACM Digital Library - 25262 papers in Machine Learning, Natural Language Processing and Information Retrieval. 

Link to pdf: [Login with U of I account](https://drive.google.com/file/d/1tPzuOdgj4DK13rWS4d_GJ7tG-0UUwV2B/view?usp=sharing)

Link to raw grobid file (input to `process_xml.py`): [Login with U of I account](https://drive.google.com/file/d/1Z3hLffwzAhKlSln4Y3fqWNZAjv-SnABz/view?usp=sharing)

## Code

### `expert_recommend.py`:
#### Example
`python expert_recommend.py --query='machine learning' --write_to_file=1`

#### Arguments
`--query` specifies a query name, e.g. `--query='machine learning'`. Default is set to `'information retrieval'`

`--write_to_file` specifies if output will be a txt file under the `output/` folder. Default is 0.

If set to 1, the name of the file would be \[query_name\].txt
