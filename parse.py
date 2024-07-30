import requests
import re
import json
from urllib.parse import urlparse, parse_qs, urlunparse, urlencode

def fetch_wikitext(url):
    """
    Fetch the raw wikitext from the given MediaWiki page URL, ensuring the 'action=raw' parameter is present.
    """
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)

    if 'action' not in query_params or query_params['action'][0] != 'raw':
        query_params['action'] = 'raw'
        url = urlunparse(parsed_url._replace(query=urlencode(query_params, doseq=True)))

    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Failed to fetch page. Status code: {response.status_code}")

def clean_text(text):
    """
    Remove invisible or directionality control characters from the text.
    """
    # Regular expression for stripping invisible characters and control characters
    invisible_chars = re.compile(r'[\u200e\u200f\u202a-\u202e]+$')
    return invisible_chars.sub('', text.strip())

def parse_mwon(wikitext):
    """
    Parse the wikitext into a list of JSON objects based on the MWON format.
    """
    # Remove all ==Level 2 headers== without affecting the rest of the text
    wikitext = re.sub(r'^==[^=]+==$', '', wikitext, flags=re.MULTILINE)

    sections = []
    level3_sections = re.split(r'===\s*(.*?)\s*===', wikitext)
    level3_sections = level3_sections[1:]  # Discard everything before the first Level 3 header

    for i in range(0, len(level3_sections), 2):
        section_id = clean_text(level3_sections[i].strip())
        content = level3_sections[i+1].strip()
        section_obj = {"id": section_id}

        # Process the bullet points and key-value pairs
        lines = content.split('\n')
        key = None
        for line in lines:
            line = clean_text(line.strip())
            if line.startswith('* '):
                if ':' in line:
                    key, value = line[2:].split(':', 1)
                    key = clean_text(key.strip())
                    value = clean_text(value.strip())
                    if not value:
                        section_obj[key] = []
                    else:
                        section_obj[key] = value
                else:
                    key = clean_text(line[2:].strip())
                    if key not in section_obj:
                        section_obj[key] = []
            elif line.startswith('** ') and key:
                section_obj[key].append(clean_text(line[3:].strip()))
            elif line:
                # Text after the key-value pairs
                cleaned_line = clean_text(line)
                if "section body" not in section_obj:
                    section_obj["section body"] = cleaned_line
                else:
                    section_obj["section body"] += f" {cleaned_line}"

        # Clean up and consolidate the object
        if key in section_obj and isinstance(section_obj[key], list) and not section_obj[key]:
            del section_obj[key]  # Remove empty lists if they were not populated

        sections.append(section_obj)

    return sections

def parse_mwon_from_url(url):
    wikitext = fetch_wikitext(url)
    parsed_data = parse_mwon(wikitext)
    json_data = json.dumps(parsed_data, indent=2)
    print(json_data)
