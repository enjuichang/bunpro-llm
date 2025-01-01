from bs4 import BeautifulSoup
import json
import time


def extract_grammar_tiles(section):
    tiles = section.find_all("div", class_="user-profile-grammar-tile")
    results = []

    for tile in tiles:
        link = tile.find("a")["href"]
        text = tile.find("p").text
        results.append({
            "link": link,
            "text": text
        })
    return results

def parse_grammar_sections(html):
    soup = BeautifulSoup(html, 'html.parser')

    # Find all sections with class "upro-wrapper_gp-tiles"
    sections = soup.find_all("div", class_="upro-wrapper_gp-tiles")

    # Create result dictionary
    result = {
        "troubled_grammar": [],
        "ghost_reviews": []
    }

    # First section with "Troubled Grammar" title
    troubled_section = next(s for s in sections if s.find("p").text == "Troubled Grammar")
    result["troubled_grammar"] = extract_grammar_tiles(troubled_section)

    # Second section with "Ghost Reviews" title
    ghost_section = next(s for s in sections if s.find("p").text == "Ghost Reviews")
    result["ghost_reviews"] = extract_grammar_tiles(ghost_section)

    return result


def fetch_grammar_details(session, base_url, grammar_data):
    """
    Fetch and parse details for each grammar point
    """

    for category in ['troubled_grammar', 'ghost_reviews']:
        if category in grammar_data:
            for item in grammar_data[category]:
                full_url = base_url + item['link']
                response = session.get(full_url)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')

                    # Find the main content sections
                    main_content = soup.find('main')
                    if not main_content:
                        continue

                    # Parse and store the extracted information
                    parsed_data = {
                    }

                    # Get the structure section first (it's in the header)
                    structure_div = main_content.find('div', {'id': 'js-rev-header'})
                    if structure_div:
                        japanese = structure_div.find('span', {'class': 'bp-ddw'})
                        meaning = structure_div.find('span', {'class': 'text-body'})
                        if japanese and meaning:
                            parsed_data['structure'] = {
                                'japanese': japanese.get_text(strip=True),
                                'meaning': meaning.get_text(strip=True)
                            }

                    # Find the tabs section
                    tab_list = main_content.find('ul', {'role': 'tablist'})
                    if tab_list:
                        # Find the Details tab content
                        details_tab = tab_list.find('button', {'role': 'tab', 'aria-controls': 'Details'})
                        if details_tab:
                            # Find the corresponding content section
                            details_content = main_content.find('article', {'data-location': 'show'})
                            if details_content:
                                # Look for About section by finding the header with id="about"
                                about_header = details_content.find('header', {'id': 'about'})
                                if about_header:
                                    # Get the parent section that contains this header
                                    about_section = about_header.find_parent('section')
                                    if about_section:
                                        about_content = about_section.find('div', class_='prose')
                                        if about_content:
                                            # Replace HTML tags with spaces to preserve readability
                                            # parsed_data['about'] = ' '.join(about_content.stripped_strings)
                                            pass
                    # Update the item with parsed data
                    item.update(parsed_data)

                # Add a small delay between requests
                time.sleep(0.1)

    return grammar_data