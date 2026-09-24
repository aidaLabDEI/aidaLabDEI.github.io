import json
import re
import subprocess

SPARQL_ENDPOINT = 'https://sparql.dblp.org/sparql'

authors = [
    { 'author': 'Andrea_Pietracaprina', 'from_year': '2020', 'to_year': '3000' },
    { 'author': 'Geppino_Pucci', 'from_year': '2020', 'to_year': '3000' },
    { 'author': 'Francesco_Silvestri_0001', 'from_year': '2020', 'to_year': '3000' },
    { 'author': 'Fabio_Vandin', 'from_year': '2020', 'to_year': '3000' },
    { 'author': 'Matteo_Ceccarello', 'from_year': '2020', 'to_year': '3000' },
    { 'author': 'Leonardo_Pellegrina', 'from_year': '2020', 'to_year': '3000' },
    { 'author': 'Diego_Santoro', 'from_year': '2020', 'to_year': '3000' },
    { 'author': 'Ilie_Sarpe', 'from_year': '2020', 'to_year': '3000' },
    { 'author': 'Dario_Simionato', 'from_year': '2020', 'to_year': '3000' },
    { 'author': 'Andrea_Tonon', 'from_year': '2020', 'to_year': '2022' },
    { 'author': 'Fabrizio_Boninsegna', 'from_year': '2023', 'to_year': '2026' },
    { 'author': 'Cristian_Boldrin', 'from_year': '2023', 'to_year': '2027' }
]

exclude_venues = [
    'CoRR'
]

def sparql(query):
    # Use curl rather than urllib: dblp serves a bot challenge page to
    # urllib-like clients, but not to curl.
    out = subprocess.run(
        ['curl', '-sS', '--fail', '-G', SPARQL_ENDPOINT,
         '-H', 'Accept: application/sparql-results+json',
         '--data-urlencode', f'query={query}'],
        check=True, capture_output=True
    ).stdout
    try:
        dat = json.loads(out)
    except json.JSONDecodeError:
        raise RuntimeError(f"dblp SPARQL returned non-JSON output: {out[:100]!r}")
    return [
        {var: b['value'] for var, b in row.items()}
        for row in dat['results']['bindings']
    ]


def get_papers():
    # Every publication (co-)created by one of the authors in their year range,
    # one row per author signature so that we can rebuild the author list.
    values = "\n".join(
        f'("{a["author"].replace("_", " ")}" "{a["from_year"]}" "{a["to_year"]}")'
        for a in authors
    )
    query = f"""
PREFIX dblp: <https://dblp.org/rdf/schema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?pub ?title ?year ?venue ?url ?ord ?name WHERE {{
  {{
    SELECT DISTINCT ?pub WHERE {{
      VALUES (?label ?from ?to) {{ {values} }}
      ?person rdfs:label ?label .
      ?pub dblp:createdBy ?person ;
           dblp:yearOfPublication ?y .
      FILTER(STR(?y) >= ?from && STR(?y) <= ?to)
    }}
  }}
  ?pub dblp:title ?title ;
       dblp:yearOfPublication ?year ;
       dblp:hasSignature ?sig .
  ?sig a dblp:AuthorSignature ;
       dblp:signatureOrdinal ?ord ;
       dblp:signatureDblpName ?name .
  OPTIONAL {{ ?pub dblp:publishedIn ?venue }}
  OPTIONAL {{ ?pub dblp:primaryDocumentPage ?url }}
}}
"""
    papers = dict()
    for row in sparql(query):
        key = row['pub'].removeprefix('https://dblp.org/rec/')
        pap = papers.setdefault(key, {
            "names": dict(),
            "url": row.get('url', row['pub']),
            "title": row['title'],
            "venue": row.get('venue', ''),
            "year": row['year'],
            "key": key
        })
        pap["names"][int(row['ord'])] = row['name']

    result = []
    for pap in papers.values():
        names = pap.pop("names")
        # drop dblp homonym disambiguation suffixes, e.g. "Francesco Silvestri 0001"
        pap["authors"] = ", ".join(
            re.sub(r' \d{4}$', '', names[i]) for i in sorted(names)
        )
        if pap['venue'] not in exclude_venues:
            result.append(pap)
    return result


def format_year(pubs, year):
    header = f'<h3 class="mb-0">{year}</h3><ul>'
    raw_entries = [
        pub
        for pub in pubs
        if year == pub['year']
    ]
    raw_entries.sort(key=lambda e: e['authors'])
    entries = [
        f"""<li>{pub["authors"]} <emph><a href="{pub['url']}">{pub["title"]}</a></emph> {pub["venue"]}</li>"""
        for pub in raw_entries
    ]
    entries = "\n".join(entries)
    return f'{header}{entries}</ul>'


def format_all(pubs):
    formatted = [
        format_year(pubs, str(year))
        for year in reversed(range(2020, 2026))
    ]
    return "\n".join(formatted)


def load_manual_pubs():
    path = "manual_pubs.json"
    with open(path) as fp:
        pubs = json.load(fp)
        for pub in pubs:
            if isinstance(pub["authors"], list):
                pub["authors"] = ", ".join(pub["authors"])
        return pubs


def get_all():
    papers = dict()
    for p in load_manual_pubs():
        if p['key'] not in papers:
            papers[p['key']] = p
        else:
            print("ERROR: paper", p['key'],
                  "present more than one time in manual publications")
    print("Querying dblp")
    for p in get_papers():
        if p['key'] not in papers:
            papers[p['key']] = p
    return list(papers.values())


def update_html(pubs):
    path = "index.html"
    with open(path) as fp:
        html = fp.read()

    marker = '<!-- PUBS -->'
    spos = html.find(marker) + len(marker)
    epos = html.find(marker, spos+1)

    pre = html[:spos].strip()
    post = html[epos:].strip()
    formatted = format_all(pubs).strip()

    output = pre + "\n" + formatted + "\n" + post
    with open(path, "w") as fp:
        print(output, file=fp)


def main():
    pubs = get_all()
    update_html(pubs)

if __name__ == "__main__":
    main()
    

