import requests

class PaymentGateway:
    def __init__(self, api_key, api_secret, base_url):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url

    def initiate_escrow(self, payer_phone, payee_phone, amount):
        url = f"{self.base_url}/escrow/initiate"
        headers = self._build_headers()
        data = {
            "payer_phone": payer_phone,
            "payee_phone": payee_phone,
            "amount": str(amount)
        }
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()

    def release_funds(self, escrow_account_id):
        url = f"{self.base_url}/escrow/release"
        headers = self._build_headers()
        data = {"escrow_account_id": escrow_account_id}
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()

    def refund(self, escrow_account_id):
        url = f"{self.base_url}/escrow/refund"
        headers = self._build_headers()
        data = {"escrow_account_id": escrow_account_id}
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()

    def _build_headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
