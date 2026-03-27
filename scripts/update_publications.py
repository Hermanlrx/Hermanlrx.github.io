#!/usr/bin/env python3
"""Fetch publications from ORCID and update publications page"""

import os
import re
import requests
import json
from datetime import datetime
from pathlib import Path

def fetch_orcid_data(orcid_id):
    """Fetch article titles, years, journals, DOIs from ORCID"""
    headers = {'Accept': 'application/json'}
    articles = []
    
    resp = requests.get(f'https://pub.orcid.org/v3.0/{orcid_id}/works', headers=headers)
    if resp.ok:
        data = resp.json()
        for group in data.get('group', []):
            for work in group.get('work-summary', []):
                pub = extract_article_summary(work)
                if pub:
                    articles.append(pub)
    
    articles.sort(key=lambda x: x['year'], reverse=True)
    return articles

def extract_article_summary(work):
    """Extract basic article data (no authors)"""
    try:
        year = work.get('publication-date', {}).get('year', {}).get('value', '')
        title = work.get('title', {}).get('title', {}).get('value', '')
        if not title:
            return None
        
        journal = work.get('journal-title', {}).get('value', '') or \
                  work.get('container-title', {}).get('value', '')
        
        volume = work.get('journal-volume', {}).get('value', '')
        page = work.get('page', {}).get('value', '')
        
        doi = ''
        for ext_id in work.get('external-ids', {}).get('external-id', []):
            if ext_id.get('external-id-type') == 'doi':
                doi = ext_id.get('external-id-value', '').lower()
                break
        
        return {
            'year': year,
            'title': title,
            'journal': journal,
            'volume': volume,
            'page': page,
            'doi': doi
        }
    except:
        return None

def extract_titles_from_existing(existing_section):
    """Extract titles from existing articles section regardless of format"""
    titles = []
    
    if not existing_section:
        return titles
    
    # Pattern 1: Title in italics after authors (your format)
    # Example: le Roux, H., ... (2025), *Title*, *Journal*...
    pattern1 = re.findall(r'\*([^*]+)\*,\s*\*', existing_section)
    titles.extend(pattern1)
    
    # Pattern 2: Title in bold (original format)
    pattern2 = re.findall(r'\*\*([^*]+)\*\*', existing_section)
    titles.extend(pattern2)
    
    # Pattern 3: Title in italics before journal
    pattern3 = re.findall(r'\*([^*]+)\*,\s*\*[^*]+\*', existing_section)
    titles.extend(pattern3)
    
    # Remove duplicates while preserving order
    unique_titles = []
    for title in titles:
        if title not in unique_titles:
            unique_titles.append(title)
    
    return unique_titles

def generate_page(articles, orcid_id, existing_content):
    """Generate publications page preserving manual content"""
    
    # Default sections
    articles_section = ""
    peer_reviews = "*Manually maintained*"
    presentations = "*Manually maintained*"
    posters = "*Manually maintained*"
    
    # Track which articles are new
    new_articles = []
    
    # Extract manual sections from existing file
    if existing_content:
        content = existing_content
        
        # Remove ALL footer lines
        lines = content.split('\n')
        cleaned_lines = [line for line in lines if '*Last updated:' not in line]
        content = '\n'.join(cleaned_lines).rstrip() + '\n'
        
        # Remove frontmatter
        match = re.match(r'^---\n.*?\n---\n', content, re.DOTALL)
        if match:
            content = content[match.end():]
        
        # Extract sections
        match = re.search(r'## Articles\n(.*?)(?=\n## |$)', content, re.DOTALL)
        if match:
            articles_section = match.group(1).strip()
        
        match = re.search(r'## Peer Review\n(.*?)(?=\n## |$)', content, re.DOTALL)
        if match:
            peer_reviews = match.group(1).strip()
        
        match = re.search(r'## Presentations\n(.*?)(?=\n## |$)', content, re.DOTALL)
        if match:
            presentations = match.group(1).strip()
        
        match = re.search(r'## Posters\n(.*?)(?=\n## |$)', content, re.DOTALL)
        if match:
            posters = match.group(1).strip()
    
    # Extract existing titles
    existing_titles = extract_titles_from_existing(articles_section)
    new_titles = [pub['title'] for pub in articles]
    
    # Find new articles (titles not in existing)
    for pub in articles:
        if pub['title'] not in existing_titles:
            new_articles.append(pub)
    
    # Build final articles section
    if articles_section:
        # Keep existing section
        final_articles = articles_section
        
        # Add new articles as bullet points
        for pub in new_articles:
            final_articles += f"\n- **ADD AUTHORS** ({pub['year']}),\n"
            final_articles += f"  *{pub['title']}*,\n"
            final_articles += f"  *{pub['journal']}*"
            if pub['doi']:
                final_articles += f". [DOI](https://doi.org/{pub['doi']})"
            final_articles += "\n"
    else:
        # First run - create initial section with bullet points
        final_articles = ""
        for pub in articles:
            final_articles += f"- **ADD AUTHORS** ({pub['year']}),\n"
            final_articles += f"  *{pub['title']}*,\n"
            final_articles += f"  *{pub['journal']}*"
            if pub['doi']:
                final_articles += f". [DOI](https://doi.org/{pub['doi']})"
            final_articles += "\n\n"
        new_articles = articles
    
    # Clean up any double bullet issues
    final_articles = re.sub(r'\n- \*\*ADD AUTHORS\*\*.*?\n  \*.*?\*,\n  \*.*?\*.*?\n', 
                            lambda m: m.group(0).replace('\n\n-', '\n-'), 
                            final_articles)
    
    # Clean up any extra blank lines
    final_articles = re.sub(r'\n\s*\n\s*\n', '\n\n', final_articles)
    
    # Build new page
    now = datetime.now()
    page = f"""---
title: "Publications"
url: "/Publications/"
date: {now.strftime('%Y-%m-%d')}
showToc: true
draft: false
layout: "single"
---

# Publications

This page is automatically updated from my [ORCID profile](https://orcid.org/{orcid_id}).  

## Articles

{final_articles}

## Peer Review

{peer_reviews}

## Presentations

{presentations}

## Posters

{posters}

*Last updated: {now.strftime('%Y-%m-%d %H:%M:%S UTC')}*"""
    
    return page, new_articles

def main():
    orcid_id = os.environ.get('ORCID_ID')
    if not orcid_id:
        print("Error: ORCID_ID not set")
        return 1
    
    articles = fetch_orcid_data(orcid_id)
    print(f"Fetched: {len(articles)} articles")
    
    pub_path = Path('content/publications.md')
    existing = pub_path.read_text() if pub_path.exists() else None
    
    new_content, new_articles = generate_page(articles, orcid_id, existing)
    pub_path.write_text(new_content)
    
    # Save new articles info for GitHub Action
    if new_articles:
        Path('data').mkdir(exist_ok=True)
        with open('data/new_articles.json', 'w') as f:
            json.dump([{
                'title': a['title'],
                'year': a['year'],
                'journal': a['journal'],
                'doi': a['doi']
            } for a in new_articles], f, indent=2)
        print(f" {len(new_articles)} new article(s) detected!")
        for article in new_articles:
            print(f"  - {article['title']}")
    else:
        # Remove new_articles.json if it exists
        if Path('data/new_articles.json').exists():
            Path('data/new_articles.json').unlink()
    
    print(f"Updated publications page")
    return 0

if __name__ == '__main__':
    exit(main())