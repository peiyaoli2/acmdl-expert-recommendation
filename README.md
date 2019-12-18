# acmdl-expert-recommendation
UIUC CS510 final project

## Dependencies
metapy

nltk

numpy

## Dataset
ACM Digital Library - 25262 papers in Machine Learning, Natural Language Processing and Information Retrieval. 

Link to pdf: [Login with U of I account](https://drive.google.com/file/d/1tPzuOdgj4DK13rWS4d_GJ7tG-0UUwV2B/view?usp=sharing) (You don't need this to run the code)

Link to raw grobid file (input to `process_xml.py`): [Login with U of I account](https://drive.google.com/file/d/1Z3hLffwzAhKlSln4Y3fqWNZAjv-SnABz/view?usp=sharing) (You don't need this to run the code)

## Code

### `expert_recommend.py`:
#### Example
`python expert_recommend.py --query='machine learning' --write_to_file=1`

#### Arguments
`--query` specifies a query name, e.g. `--query='machine learning'`. Default is set to `'information retrieval'`

`--write_to_file` specifies if output will be printed to console or txt file. Default is 0 and will print to console.

If set to 1, the name of the file would be \[query_name\].txt under the `output/` folder.

### `process_xml.py`
You don't need to run this code.

This file contains all the preprocessing code we did from the raw grobid file, e.g. extracting information such as title, abstract, introduction, full body text, authors, citations, keywords (attempted), year of publication (attempted).

After information are extracted, they are dumped under `pickles/` which are used as input to `expert_recommend.py`.
