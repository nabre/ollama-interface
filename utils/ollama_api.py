import requests
import json

class OllamaAPI:
    def __init__(self, base_url="http://localhost:11434"):
        self.base_url = base_url

    def get_models(self):
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            return [model["name"] for model in response.json()["models"]]
        except requests.RequestException as e:
            raise Exception(f"Failed to get models: {str(e)}")

    def chat(self, message, model="llama2"):
        try:
            data = {
                "model": model,
                "prompt": message,
                "stream": False
            }
            response = requests.post(f"{self.base_url}/api/generate", json=data)
            response.raise_for_status()
            return response.json()["response"]
        except requests.RequestException as e:
            raise Exception(f"Chat failed: {str(e)}")

    def download_model(self, model_name, progress_callback=None):
        try:
            data = {"name": model_name}
            with requests.post(f"{self.base_url}/api/pull", json=data, stream=True) as response:
                response.raise_for_status()
                total_size = int(response.headers.get("content-length", 0))
                downloaded_size = 0
                for chunk in response.iter_content(chunk_size=8192):
                    downloaded_size += len(chunk)
                    if progress_callback:
                        progress_callback(downloaded_size / total_size)
        except requests.RequestException as e:
            raise Exception(f"Failed to download model: {str(e)}")

    def delete_model(self, model_name):
        try:
            data = {"name": model_name}
            response = requests.delete(f"{self.base_url}/api/delete", json=data)
            response.raise_for_status()
        except requests.RequestException as e:
            raise Exception(f"Failed to delete model: {str(e)}")

    def create_model(self, model_name, modelfile_content, progress_callback=None):
        try:
            data = {
                "name": model_name,
                "modelfile": modelfile_content
            }
            with requests.post(f"{self.base_url}/api/create", json=data, stream=True) as response:
                response.raise_for_status()
                total_size = int(response.headers.get("content-length", 0))
                created_size = 0
                for chunk in response.iter_content(chunk_size=8192):
                    created_size += len(chunk)
                    if progress_callback:
                        progress_callback(created_size / total_size)
        except requests.RequestException as e:
            raise Exception(f"Failed to create model: {str(e)}")