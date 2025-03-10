import urllib.request
import json
import os

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

def get_author(author, from_year, to_year):
    url = f'https://dblp.org/search/publ/api?q=author:{author}:&format=json'
    url = f'https://dblp.uni-trier.de/search/publ/api?q=author:{author}:&format=json'
    req = urllib.request.urlopen(url)
    dat = json.load(req)
    hits = dat['result']['hits']['hit']
    papers = []
    for pap in hits:
        pap = pap['info']
        if from_year <= pap["year"] <= to_year:
            authors = pap['authors']['author']
            if isinstance(authors, list):
                authors = ", ".join([
                    a['text']
                    for a in pap['authors']['author']
                ])
            else:
                authors = authors['text']
            authors = authors.replace("0001", "")
            entry = {
                "authors": authors,
                "url": pap['ee'],
                "title": pap['title'],
                "venue": pap['venue'],
                "year": pap['year'],
                "key": pap["key"]
            }
            if entry['venue'] not in exclude_venues:
                papers.append(entry)
    return papers


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
    for author in authors:
        for p in get_author(**author):
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
    

