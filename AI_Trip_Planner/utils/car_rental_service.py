
import requests
import os
from dotenv import load_dotenv
load_dotenv()

class CarRentalService:
    def __init__(self):
        self.amadeus_api_key = os.getenv("AMADEUS_API_KEY", "")
        self.amadeus_api_secret = os.getenv("AMADEUS_API_SECRET", "")
        print(f"AMADEUS_API_KEY: '{self.amadeus_api_key}'")
        print(f"AMADEUS_API_SECRET: '{self.amadeus_api_secret}'")
        self.base_url = "https://test.api.amadeus.com/v1/shopping/transfer-offers"
        self.token_url = "https://test.api.amadeus.com/v1/security/oauth2/token"
        self.access_token = self._get_access_token()
        print(f"Access Token: '{self.access_token}'")

    def _get_access_token(self):
        data = {
            "grant_type": "client_credentials",
            "client_id": self.amadeus_api_key,
            "client_secret": self.amadeus_api_secret
        }
        response = requests.post(self.token_url, data=data)
        if response.status_code != 200:
            raise Exception(f"Failed to get Amadeus access token: {response.text}")
        return response.json()["access_token"]

    def search_cars(self, startLocationCode: str, endLocationCode: str, transferType: str, startDateTime: str, duration: str, passengers: int):
        """
        Search for available transfer (car rental/transfer) offers using Amadeus API with new parameter format.
        Args:
            startLocationCode (str): IATA code of the start location (e.g., airport/city)
            endLocationCode (str): IATA code of the end location
            transferType (str): Type of transfer (e.g., HOURLY, ONE_WAY)
            startDateTime (str): Start date and time in ISO format (YYYY-MM-DDTHH:MM:SS)
            duration (str): Duration in ISO 8601 format (e.g., PT9H30M)
            passengers (int): Number of passengers
        Returns:
            dict: API response with available transfer offers
        """
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        params = {
            "startLocationCode": startLocationCode,
            "endLocationCode": endLocationCode,
            "transferType": transferType,
            "startDateTime": startDateTime,
            "duration": duration,
            "passengers": passengers
        }
        response = requests.post(self.base_url, headers=headers, json=params)
        print(f"Request URL: {response.url}")
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")

        if response.status_code != 200:
            raise Exception(f"Car rental API call failed: {response.text}")
        return response.json()
