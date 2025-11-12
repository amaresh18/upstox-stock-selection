"""
OAuth helper for Upstox API authentication.
Handles authorization flow and token exchange.
"""
import os
import requests
from typing import Optional, Dict, Tuple
from urllib.parse import urlencode, parse_qs, urlparse


class UpstoxOAuthHelper:
    """Helper class for Upstox OAuth authentication flow."""
    
    # OAuth endpoints
    AUTHORIZATION_URL = "https://api.upstox.com/v2/login/authorization/dialog"
    TOKEN_URL = "https://api.upstox.com/v2/login/authorization/token"
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str = "https://127.0.0.1"):
        """
        Initialize OAuth helper.
        
        Args:
            client_id: Upstox API client ID
            client_secret: Upstox API client secret
            redirect_uri: Redirect URI (must match Upstox app settings)
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
    
    def get_authorization_url(self) -> str:
        """
        Generate authorization URL for OAuth flow.
        
        Returns:
            Authorization URL string
        """
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri
        }
        return f"{self.AUTHORIZATION_URL}?{urlencode(params)}"
    
    def extract_code_from_url(self, callback_url: str) -> Optional[str]:
        """
        Extract authorization code from callback URL.
        
        Args:
            callback_url: The callback URL with code parameter
            
        Returns:
            Authorization code or None if not found
        """
        try:
            parsed = urlparse(callback_url)
            params = parse_qs(parsed.query)
            code = params.get('code', [None])[0]
            return code
        except Exception as e:
            print(f"Error extracting code: {e}")
            return None
    
    def exchange_code_for_token(self, code: str) -> Tuple[bool, Dict]:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from callback
            
        Returns:
            Tuple of (success: bool, response_data: dict)
        """
        try:
            headers = {
                "accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            data = {
                "code": code,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "redirect_uri": self.redirect_uri,
                "grant_type": "authorization_code"
            }
            
            response = requests.post(
                self.TOKEN_URL,
                headers=headers,
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return True, result
            else:
                error_msg = response.text
                return False, {"error": error_msg, "status_code": response.status_code}
                
        except Exception as e:
            return False, {"error": str(e)}
    
    def save_token_to_env(self, access_token: str, api_key: str = None) -> bool:
        """
        Save access token to environment variable (for current session).
        
        Args:
            access_token: The access token to save
            api_key: Optional API key to save as well
            
        Returns:
            True if successful
        """
        try:
            os.environ['UPSTOX_ACCESS_TOKEN'] = access_token
            if api_key:
                os.environ['UPSTOX_API_KEY'] = api_key
            return True
        except Exception as e:
            print(f"Error saving to environment: {e}")
            return False
    
    def save_token_to_file(self, access_token: str, api_key: str = None, 
                          file_path: str = ".env.local") -> bool:
        """
        Save access token to a local file.
        
        Args:
            access_token: The access token to save
            api_key: Optional API key to save as well
            file_path: Path to save the file
            
        Returns:
            True if successful
        """
        try:
            lines = []
            if api_key:
                lines.append(f"UPSTOX_API_KEY={api_key}\n")
            lines.append(f"UPSTOX_ACCESS_TOKEN={access_token}\n")
            
            with open(file_path, 'w') as f:
                f.writelines(lines)
            return True
        except Exception as e:
            print(f"Error saving to file: {e}")
            return False

