"""
Bunpro Utilities Module

This module provides utility functions for parsing and processing Bunpro grammar data.
It includes functions for extracting grammar tiles, parsing grammar sections, and fetching detailed grammar information.
"""

from typing import Dict, List, Any
from bs4 import BeautifulSoup, Tag
import json
import time
from pydantic import BaseModel, Field
from requests import Session


class GrammarTile(BaseModel):
    """Pydantic model for a grammar tile"""
    link: str = Field(..., description="URL path to the grammar point")
    text: str = Field(..., description="Grammar point text")


class GrammarStructure(BaseModel):
    """Pydantic model for grammar structure"""
    japanese: str = Field(..., description="Japanese grammar pattern")
    meaning: str = Field(..., description="English meaning of the grammar")


class GrammarData(BaseModel):
    """Pydantic model for grammar data sections"""
    troubled_grammar: List[GrammarTile] = Field(default_factory=list, description="List of troubled grammar points")
    ghost_reviews: List[GrammarTile] = Field(default_factory=list, description="List of ghost review grammar points")


def extract_grammar_tiles(section: Tag) -> List[Dict[str, str]]:
    """
    Extract grammar tiles from a BeautifulSoup section.

    Args:
        section (Tag): BeautifulSoup Tag object containing grammar tiles

    Returns:
        List[Dict[str, str]]: List of dictionaries containing link and text for each grammar tile
    """
    # Find all div elements with the specified class
    tiles = section.find_all("div", class_="user-profile-grammar-tile")
    results = []

    # Extract link and text from each tile
    for tile in tiles:
        link = tile.find("a")["href"]
        text = tile.find("p").text
        results.append(GrammarTile(
            link=link,
            text=text
        ).model_dump())
    return results


def parse_grammar_sections(html: str) -> Dict[str, List[Dict[str, str]]]:
    """
    Parse HTML content to extract grammar sections.

    Args:
        html (str): HTML content from Bunpro's stats page

    Returns:
        Dict[str, List[Dict[str, str]]]: Dictionary containing troubled grammar and ghost reviews

    Raises:
        StopIteration: If required sections are not found
    """
    # Parse HTML content
    soup = BeautifulSoup(html, 'html.parser')

    # Find all sections with class "upro-wrapper_gp-tiles"
    sections = soup.find_all("div", class_="upro-wrapper_gp-tiles")

    # Initialize result with Pydantic model
    result = GrammarData().model_dump()

    try:
        # Extract troubled grammar section
        troubled_section = next(s for s in sections if s.find("p").text == "Troubled Grammar")
        result["troubled_grammar"] = extract_grammar_tiles(troubled_section)

        # Extract ghost reviews section
        ghost_section = next(s for s in sections if s.find("p").text == "Ghost Reviews")
        result["ghost_reviews"] = extract_grammar_tiles(ghost_section)

    except StopIteration as e:
        print("Error: Could not find required grammar sections")
        raise e

    return result


def fetch_grammar_details(
    session: Session, 
    base_url: str, 
    grammar_data: Dict[str, List[Dict[str, str]]]
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Fetch and parse details for each grammar point.

    Args:
        session (Session): Active requests session with authentication
        base_url (str): Base URL for Bunpro website
        grammar_data (Dict[str, List[Dict[str, str]]]): Dictionary containing grammar points to process

    Returns:
        Dict[str, List[Dict[str, Any]]]: Enhanced grammar data with additional details

    Note:
        Includes a delay between requests to avoid overwhelming the server
    """
    # Process each category of grammar points
    for category in ['troubled_grammar', 'ghost_reviews']:
        if category in grammar_data:
            for item in grammar_data[category]:
                # Construct full URL for the grammar point
                full_url = base_url + item['link']
                response = session.get(full_url)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')

                    # Find the main content section
                    main_content = soup.find('main')
                    if not main_content:
                        continue

                    # Initialize parsed data dictionary
                    parsed_data = {}

                    # Extract structure information from header
                    structure_div = main_content.find('div', {'id': 'js-rev-header'})
                    if structure_div:
                        japanese = structure_div.find('span', {'class': 'bp-ddw'})
                        meaning = structure_div.find('span', {'class': 'text-body'})
                        if japanese and meaning:
                            parsed_data['structure'] = GrammarStructure(
                                japanese=japanese.get_text(strip=True),
                                meaning=meaning.get_text(strip=True)
                            ).model_dump()

                    # Extract additional details from tabs
                    tab_list = main_content.find('ul', {'role': 'tablist'})
                    if tab_list:
                        details_tab = tab_list.find('button', {'role': 'tab', 'aria-controls': 'Details'})
                        if details_tab:
                            details_content = main_content.find('article', {'data-location': 'show'})
                            if details_content:
                                about_header = details_content.find('header', {'id': 'about'})
                                if about_header:
                                    about_section = about_header.find_parent('section')
                                    if about_section:
                                        about_content = about_section.find('div', class_='prose')
                                        if about_content:
                                            # Commented out to avoid excessive data
                                            # parsed_data['about'] = ' '.join(about_content.stripped_strings)
                                            pass

                    # Update item with parsed data
                    item.update(parsed_data)

                # Add delay to prevent server overload
                time.sleep(0.1)

    return grammar_data