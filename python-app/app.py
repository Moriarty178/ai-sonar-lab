import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()

SONAR_URL = os.getenv("SONAR_URL")
SONAR_TOKEN = os.getenv("SONAR_TOKEN")
PROJECT_KEY = os.getenv("PROJECT_KEY")

AI_MODE = os.getenv("AI_MODE")

AI_API_URL = os.getenv("AI_API_URL")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL")

def wait_for_sonar():
    print("⏳ Waiting for SonarQube...")
    for i in range(20):
        try:
            r = requests.get(f"{SONAR_URL}/api/system/status")
            if r.status_code == 200:
                print("✅ SonarQube is ready")
                return
        except:
            pass

        print(f"Retry {i+1}/20...")
        time.sleep(5)

    raise Exception("❌ SonarQube not ready")


def get_sonarqube_issues():
    url = f"{SONAR_URL}/api/issues/search"
    params = {
        'componentKeys': PROJECT_KEY,
        'statuses': 'OPEN',
        'types': 'BUG,VULNERABILITY',
        'severities': 'BLOCKER,CRITICAL,MAJOR',
    }

    response = requests.get(url, params=params, auth=(SONAR_TOKEN, ""))
    return response.json().get('issues', [])


def ask_ai(prompt):
    if AI_MODE == "mock":
        payload = {
            "model": "mock",
            "messages": [{"role": "user", "content": prompt}]
        }
        r = requests.post(AI_API_URL, json=payload)
        return r.json()['choices'][0]['message']['content']

    elif AI_MODE == "openai":
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "tinyllama",
            "messages": [{"role": "user", "content": prompt}]
        }

        r = requests.post(
            AI_API_URL,
            headers=headers,
            json=payload,
            timeout=300
        )

        print("DEBUG STATUS:", r.status_code)
        print("DEBUG RESPONSE:", r.text)

        data = r.json()

        if "choices" not in data:
            return f"❌ OpenAI Error: {data}"

        return data['choices'][0]['message']['content']


def main():
    print("🚀 Start scanning...\n")

    wait_for_sonar()

    issues = get_sonarqube_issues()

    print(f"Found {len(issues)} issues\n")

    for issue in issues:
        prompt = f"Lỗi: {issue['message']}. Hướng dẫn fix."

        result = ask_ai(prompt)

        print("-----")
        print(issue['message'])
        print(result)


if __name__ == "__main__":
    main()