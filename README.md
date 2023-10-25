# Algorithms for Intelligent Data Analytics website

This repository hosts the sources for the [AIDALab](https://aidalabdei.github.io/) website.

The `index.html` file can be edited directly. Adding new publications is automated with the
`update-papers.py` script.

## Updating the publications

Running `python update-papers.py` will query DBLP for the papers written by the members of the group.
The resulting information is integrated with papers listed in `manual_pubs.json` and used to update
the `index.html` file.
As part of normal operations no other actions are required, other than running the `update-papers.py` script.

Papers from Arxiv are not considered.

### Adding papers that are not indexed by DBLP

To add a paper that is not listed in DBLP, one can add an entry to `manual_pubs.json` with the following format:

```json
{
  "authors": [
    "First Author",
    "Second Author"
  ],
  "key": "a-unique-key-for-the-paper",
  "title": "title of the paper",
  "url": "url to retrieve the paper",
  "venue": "Journal or conference",
  "year": "year of publication"
},
```

After editing the file (which is indexed in `git`) one should run

```
python update-papers.py
```
to see the changes included in `index.html`

### Adding paper authors

The list of people whose papers will be looked for in DBLP is at the beginning of the
`update-papers.py` script:

https://github.com/aidaLabDEI/aidaLabDEI.github.io/blob/1ad9ad9143e782bf19cf7187ec3113739ce71ba0/update-papers.py#L5-L16

To add new person, simply add a new entry following the same structure.
If someone leaves the group, we can modify the corresponding `to_year` entry, so that only papers that were
published while in the group are included in the website.

