"""
Bunpro Client Module

This module provides a client for interacting with Bunpro's website to fetch grammar data.
It handles authentication and data retrieval for a user's troubled grammar points and ghost reviews.
"""

from typing import Dict, Optional
from pydantic import BaseModel, Field
import requests
from bs4 import BeautifulSoup
import json
from bunpro_utils import parse_grammar_sections, fetch_grammar_details


class BunproCredentials(BaseModel):
    """Pydantic model for Bunpro credentials"""
    email: str = Field(..., description="Bunpro account email")
    password: str = Field(..., description="Bunpro account password")


class BunproGrammarPoint(BaseModel):
    """Pydantic model for a grammar point"""
    link: str = Field(..., description="URL path to the grammar point")
    text: str = Field(..., description="Grammar point text")
    structure: Optional[Dict[str, str]] = Field(
        None, 
        description="Grammar structure containing Japanese and meaning"
    )


class BunproClient:
    """
    A client for interacting with Bunpro's website.
    
    This client handles authentication and data retrieval for a user's grammar points.
    It can fetch troubled grammar points and ghost reviews, along with their detailed information.
    
    Attributes:
        session (requests.Session): Session object for maintaining cookies and connection
        email (str): User's Bunpro email
        password (str): User's Bunpro password
        data_file (str): Path to store the fetched grammar data
    """

    def __init__(self, email: str, password: str) -> None:
        """
        Initialize the Bunpro client.

        Args:
            email: Bunpro account email
            password: Bunpro account password
        """
        # Create a session to maintain cookies across requests
        self.session = requests.Session()
        # Store credentials
        self.credentials = BunproCredentials(email=email, password=password)
        # Set the default data file path
        self.data_file = 'bunpro_data.json'

    def login(self) -> tuple[bool, str]:
        """
        Authenticate with Bunpro using provided credentials.

        Returns:
            tuple[bool, str]: (success status, error message if any)
        """
        login_page_url = "https://bunpro.jp/users/sign_in"

        try:
            # Get the login page first to obtain the CSRF token
            response = self.session.get(login_page_url)
            response.raise_for_status()

            # Parse the page to find the authentication token
            soup = BeautifulSoup(response.text, 'html.parser')
            authenticity_token = soup.find('input', {'name': 'authenticity_token'})['value']

            # Prepare login form data
            login_data = {
                "utf8": "✓",
                "authenticity_token": authenticity_token,
                "user[email]": self.credentials.email,
                "user[password]": self.credentials.password,
                "user[remember_me]": "1",
                "commit": "Log in"
            }

            # Attempt to log in
            login_response = self.session.post(login_page_url, data=login_data)
            
            # Parse response for error messages
            error_soup = BeautifulSoup(login_response.text, 'html.parser')
            
            # Find the errors container and check for the alert message
            errors_div = error_soup.find('div', {'class': 'errors'})
            if errors_div:
                alert_div = errors_div.find('div', {'class': 'alert'})
                if alert_div and "Invalid Email or password." in alert_div.text:
                    return False, "Invalid email or password. Please check your Bunpro credentials."
            
            if login_response.status_code != 200:
                return False, f"Login failed with status code: {login_response.status_code}"
            
            return True, ""

        except requests.RequestException as e:
            return False, f"Connection error: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error during login: {str(e)}"

    def fetch_grammar_data(self) -> tuple[bool, str]:
        """
        Fetch and save grammar data from the user's profile.

        Returns:
            tuple[bool, str]: (success status, error message)
        """
        # URL for the user's grammar stats
        stats_url = "https://bunpro.jp/user/profile/stats"

        try:
            # Fetch the stats page
            stats_response = self.session.get(stats_url)
            stats_response.raise_for_status()
            # Check if we're redirected to login page (session expired or not logged in)
            if "sign_in" in stats_response.url.lower():
                return False, "Login required. Please check your credentials."

            if stats_response.status_code == 200:
                # Parse the grammar sections from the response
                result = parse_grammar_sections(stats_response.text)
                base_url = "https://bunpro.jp"
                
                # Fetch detailed information for each grammar point
                detailed_result = fetch_grammar_details(self.session, base_url, result)

                # Save the results to a file
                with open(self.data_file, 'w', encoding='utf-8') as f:
                    json.dump(detailed_result, f, indent=2, ensure_ascii=False)
                return True, "Successfully fetched grammar data!"
            
            return False, f"Failed to fetch data: HTTP {stats_response.status_code}"

        except requests.RequestException as e:
            return False, f"Connection error: {str(e)}"
        except Exception as e:
            return False, f"Error processing grammar data: {str(e)}"

    def update_grammar_data(self) -> tuple[bool, str]:
        """
        Login and update the grammar data.

        Returns:
            tuple[bool, str]: (success status, error message if any)
        """
        # First try to login
        success, error_msg = self.login()
        if not success:
            return False, f"Login failed: {error_msg}"
        
        # Then try to fetch data
        success, fetch_msg = self.fetch_grammar_data()
        if not success:
            return False, fetch_msg
        
        return True, "Successfully updated Bunpro data!"


if __name__ == "__main__":
    # Example usage
    import os
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
    # Create client instance
    client = BunproClient(
        email=os.getenv("BUNPRO_EMAIL"),
        password=os.getenv("BUNPRO_PASSWORD")
    )
    
    # Update grammar data
    if client.update_grammar_data():
        print("Successfully updated Bunpro data!")
    else:
        print("Failed to update Bunpro data")
