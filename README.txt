# mwonparse

MediaWiki Object Notation (MWON) is a format for using wiki pages to format configuration blocks in a YAML-like format. It is documented at <https://en.wikipedia.org/wiki/User:Harej/MWON>.

mwonparse is a Python module that takes a wiki page that is formatted with MWON and constructs a Python list that can be exported as JSON.

# Setup

1. `git clone https://github.com/scatter-llc/mwonparse`

2. `cd mwonparse`

3. `python3 -m venv venv`

4. `pip install -r requirements.txt`

# Usage

```
from mwonparse.parse import parse_mwon_from_url

config_url = "https://www.wikidata.org/wiki/Wikidata:Orb_Open_Graph/Queries"
configuration = parse_mwon_from_url(config_url)
````
