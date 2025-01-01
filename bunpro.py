import requests
from bs4 import BeautifulSoup
import json
from bunpro_utils import parse_grammar_sections, fetch_grammar_details

class BunproClient:
    def __init__(self, email, password):
        self.session = requests.Session()
        self.email = email
        self.password = password
        self.data_file = 'bunpro_data.json'
        
    def login(self):
        """Login to Bunpro and return success status"""
        login_page_url = "https://bunpro.jp/users/sign_in"
        response = self.session.get(login_page_url)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        authenticity_token = soup.find('input', {'name': 'authenticity_token'})['value']
        
        login_data = {
            "utf8": "✓",
            "authenticity_token": authenticity_token,
            "user[email]": self.email,
            "user[password]": self.password,
            "user[remember_me]": "1",
            "commit": "Log in"
        }
        
        login_response = self.session.post(login_page_url, data=login_data)
        return login_response.status_code == 200

    def fetch_grammar_data(self):
        """Fetch and save grammar data"""
        stats_url = "https://bunpro.jp/user/profile/stats"
        stats_response = self.session.get(stats_url)

        if stats_response.status_code == 200:
            result = parse_grammar_sections(stats_response.text)
            base_url = "https://bunpro.jp"
            detailed_result = fetch_grammar_details(self.session, base_url, result)

            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(detailed_result, f, indent=2, ensure_ascii=False)
            return True
        return False

    def update_grammar_data(self):
        """Login and update grammar data"""
        if self.login():
            return self.fetch_grammar_data()
        return False
