#!/usr/bin/env python3
"""Fetch publications from ORCID and update publications page"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path

def fetch_orcid_works(orcid_id):
    """Fetch works from ORCID public API"""
    url = f'https://pub.orcid.org/v3.0/{orcid_id}/works'
    headers = {'Accept': 'application/json'}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        publications = []
        if 'group' in data:
            for group in data['group']:
                if 'work-summary' in group:
                    for work in group['work-summary']:
                        pub = extract_publication(work)
                        if pub:
                            publications.append(pub)
        
        publications.sort(key=lambda x: x.get('year', ''), reverse=True)
        return publications
        
    except Exception as e:
        print(f"Error: {e}")
        return []

def extract_publication(work):
    """Extract publication data"""
    try:
        # Get year
        pub_date = work.get('publication-date', {})
        year = pub_date.get('year', {}).get('value', '')
        
        # Get title
        title = work.get('title', {}).get('title', {}).get('value', '')
        if not title:
            return None
        
        # Get journal
        journal = ''
        if 'journal-title' in work:
            journal = work.get('journal-title', {}).get('value', '')
        elif 'container-title' in work:
            journal = work.get('container-title', {}).get('value', '')
        
        # Get DOI
        doi = ''
        if 'external-ids' in work:
            for ext_id in work['external-ids'].get('external-id', []):
                if ext_id.get('external-id-type') == 'doi':
                    doi = ext_id.get('external-id-value', '').lower()
                    break
        
        return {
            'title': title,
            'year': year,
            'journal': journal,
            'doi': doi
        }
    except:
        return None

def generate_publications_page(publications, orcid_id):
    """Generate publications.md"""
    
    content = f"""---
title: "Publications"
date: {datetime.now().strftime('%Y-%m-%d')}
draft: false
layout: "single"
---

# Publications

This page is automatically updated from my [ORCID profile](https://orcid.org/{orcid_id}).  
Last synchronized: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

## Articles

"""
    
    # Add articles
    for pub in publications:
        if pub.get('journal'):
            content += f"**{pub['title']}**  \n"
            content += f"*{pub['journal']}*, {pub['year']}  \n"
            
            if pub.get('doi'):
                content += f"[DOI](https://doi.org/{pub['doi']})  \n"
            
            content += "\n"
    
    # Add note about other sections
    content += """## Presentations

*Manually maintained*

## Posters

*Manually maintained*

---

*Last updated: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC') + """*
"""
    
    # Write file
    pub_path = Path('content/publications.md')
    pub_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(pub_path, 'w') as f:
        f.write(content)
    
    print(f"Updated with {len([p for p in publications if p.get('journal')])} articles")

if __name__ == '__main__':
    orcid_id = os.environ.get('ORCID_ID')
    
    if not orcid_id:
        print("Please set ORCID_ID environment variable")
        exit(1)
    
    publications = fetch_orcid_works(orcid_id)
    
    if publications:
        generate_publications_page(publications, orcid_id)
    else:
        print("No publications found")