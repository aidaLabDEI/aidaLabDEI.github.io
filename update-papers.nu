#!/usr/bin/env nu

let authors = [
    { author: 'Andrea_Pietracaprina', from_year: '2020', to_year: '3000' },
    { author: 'Geppino_Pucci', from_year: '2020', to_year: '3000' },
    { author: 'Francesco_Silvestri_0001', from_year: '2020', to_year: '3000' },
    { author: 'Fabio_Vandin', from_year: '2020', to_year: '3000' },
    { author: 'Matteo_Ceccarello', from_year: '2020', to_year: '3000' },
    { author: 'Leonardo_Pellegrina', from_year: '2020', to_year: '3000' },
    { author: 'Diego_Santoro', from_year: '2020', to_year: '3000' },
    { author: 'Ilie_Sarpe', from_year: '2020', to_year: '3000' },
    { author: 'Dario_Simionato', from_year: '2020', to_year: '3000' },
    { author: 'Andrea_Tonon', from_year: '2020', to_year: '2022' }
]

let exclude_venues = [
    'CoRR'
]

def get_author_bib [author from_year to_year] {
    http get $'https://dblp.org/search/publ/api?q=author:($author):&format=json' |
        get result.hits.hit.info | 
        where year >= $from_year | 
        where year <= $to_year | 
        select key authors.author.text year venue title ee
}

def format_year [pubs year] {
    let header = $'<h3 class="mb-0">($year)</h3><ul>'
    let entries = (
        $pubs | 
            where year == $year |
            sort-by authors_author_text |
            each { |row|
                $'<li>($row.authors_author_text | str join ", ") <emph><a href="($row.ee)">($row.title)</a></emph> ($row.venue)</li>' |
            } |
            str replace -a ' 0001' '' |
            str join "\n"
    )
    $'($header)($entries)</ul>'
}

let data = (
    $authors | 
        each { |author| get_author_bib $author.author $author.from_year $author.to_year } |
        append (open manual_pubs.yml) |
        reduce { |it, acc| $acc | append $it } |
        uniq-by key |
        where venue not-in $exclude_venues |
        sort-by -rn year
)

let years = ($data | get year | uniq | sort -r)
let txt = (
    $years |
        each { |year| format_year $data $year } |
        to text
)

let first_chunk = (
    open index.html | 
        lines |
        take while { |l| $l !~ 'PUBS' } |
        str join "\n"
)

let last_chunk = (
    open index.html |
        lines |
        reverse |
        take while { |l| $l !~ 'PUBS' } |
        reverse |
        str join "\n"
)

let marker = '<!-- PUBS -->'

[ $first_chunk, $marker, $txt, $marker,  $last_chunk ] |
    str join "\n" |
    to text |
    save -f index.html

