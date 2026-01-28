import requests
import json
import logging

# Configure logging to see what's happening
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration constants
CARBON_API_URL = "http://localhost:5000/intensity"
LOCAL_LLM_URL = "http://localhost:8000/v1/chat/completions"
CLOUD_THRESHOLD = 200  # gCO2/kWh: Below this is "Green", Above is "Dirty"

class EcoRouter:
    def __init__(self):
        self.headers = {"Content-Type": "application/json"}

    def get_carbon_intensity(self):
        """Fetches the current grid carbon intensity."""
        try:
            response = requests.get(CARBON_API_URL)
            data = response.json()
            return data.get("intensity", 0)
        except Exception as e:
            logging.error(f"Failed to fetch carbon data: {e}")
            return 999  # Assume worst case on error

    def route_query(self, user_prompt, model_complexity="hard"):
        """
        Decides where to send the query based on Carbon Intensity.
        Logic:
        - If Carbon is HIGH (>200) -> FORCE LOCAL (Save the planet, use your solar/local GPU)
        - If Carbon is LOW (<200) AND Task is HARD -> ALLOW CLOUD (Simulated)
        - If Task is EASY -> ALWAYS LOCAL
        """
        intensity = self.get_carbon_intensity()
        logging.info(f"🌍 Current Grid Intensity: {intensity} gCO2/kWh")

        # Decision Logic
        if intensity > CLOUD_THRESHOLD:
            decision = "LOCAL"
            reason = "Grid is dirty (High Carbon). Keeping traffic local."
        elif model_complexity == "easy":
            decision = "LOCAL"
            reason = "Task is simple. No need for cloud compute."
        else:
            decision = "CLOUD"
            reason = "Grid is green & task is hard. Offloading to cloud."

        logging.info(f"🚦 Routing Decision: {decision} | Reason: {reason}")
        
        if decision == "LOCAL":
            return self._call_local_gpu(user_prompt)
        else:
            return self._call_cloud_mock(user_prompt)

    def _call_local_gpu(self, prompt):
        """Sends request to your RTX 4060 Ti via vLLM"""
        payload = {
            "model": "TheBloke/Mistral-7B-Instruct-v0.2-AWQ",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 512,
            "temperature": 0.7
        }
        try:
            response = requests.post(LOCAL_LLM_URL, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            return f"❌ Local GPU Error: {e}"

    def _call_cloud_mock(self, prompt):
        """Simulates calling GPT-4 (Just a mock for now)"""
        return f"[MOCK CLOUD RESPONSE] I am a cloud model processing: '{prompt[:20]}...'"

# --- Test Loop ---
if __name__ == "__main__":
    router = EcoRouter()
    
    print("\n--- 🧪 TEST 1: Simple Prompt (Should be LOCAL) ---")
    print(router.route_query("What is 2+2?", model_complexity="easy"))

    print("\n--- 🧪 TEST 2: Complex Prompt (Decision depends on Carbon) ---")
    # This might go Cloud or Local depending on the random Carbon number
    print(router.route_query("Explain quantum entanglement", model_complexity="hard"))