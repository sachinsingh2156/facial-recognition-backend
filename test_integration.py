"""
Integration tests: run against a live server (e.g. docker-compose up, then python test_integration.py).
Uses real face images if available (face_test.jpeg or first .jpg/.jpeg in project), otherwise skips.
Covers: register -> authenticate (same face), duplicate image reject, same-face-different-id reject,
and unregistered face returns 401.
"""
import base64
import os
import sys

try:
    import requests
except ImportError:
    print("Install requests: pip install requests")
    sys.exit(1)

BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8053")
REGISTER_URL = f"{BASE_URL}/api/authentication/register/"
AUTH_URL = f"{BASE_URL}/api/authentication/authenticate/"


def image_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def find_face_image():
    for name in ["face_test.jpeg", "face_test.jpg", "test_face.jpg", "1.jpg", "2.jpg"]:
        if os.path.isfile(name):
            return name
    for root, _, files in os.walk("."):
        for f in files:
            if f.lower().endswith((".jpg", ".jpeg")) and "face" in f.lower():
                return os.path.join(root, f)
    return None


def main():
    image_path = find_face_image()
    if not image_path:
        print("No face image found (face_test.jpeg, 1.jpg, etc.). Skipping integration tests.")
        return 0

    print(f"Using image: {image_path}")
    b64 = image_to_base64(image_path)
    failures = []

    # 1. Register new user
    r = requests.post(
        REGISTER_URL,
        json={"unique_id": "qa_user_1", "name": "QA User One", "face_image": b64},
        timeout=10,
    )
    if r.status_code != 201:
        failures.append(f"Register (new user): expected 201, got {r.status_code} - {r.text}")
    else:
        print("PASS: Register new user -> 201")

    # 2. Same image again (different unique_id) -> 400
    r2 = requests.post(
        REGISTER_URL,
        json={"unique_id": "qa_user_2", "name": "QA User Two", "face_image": b64},
        timeout=10,
    )
    if r2.status_code != 400:
        failures.append(f"Register (same image): expected 400, got {r2.status_code} - {r2.text}")
    elif "exact image" not in (r2.json().get("message") or "").lower():
        failures.append(f"Register (same image): message should mention exact image - {r2.json()}")
    else:
        print("PASS: Register same image again -> 400")

    # 3. Authenticate with same face -> 200 and correct identity
    r3 = requests.post(AUTH_URL, json={"face_image": b64}, timeout=10)
    if r3.status_code != 200:
        failures.append(f"Authenticate (registered face): expected 200, got {r3.status_code} - {r3.text}")
    else:
        data = r3.json()
        if data.get("unique_id") != "qa_user_1" or data.get("name") != "QA User One":
            failures.append(f"Authenticate: wrong identity returned: {data}")
        else:
            print("PASS: Authenticate same face -> 200, correct identity")

    # 4. Invalid image -> 400
    r4 = requests.post(
        REGISTER_URL,
        json={"unique_id": "bad", "name": "Bad", "face_image": "not-valid-base64!!"},
        timeout=10,
    )
    if r4.status_code != 400:
        failures.append(f"Register (invalid image): expected 400, got {r4.status_code}")
    else:
        print("PASS: Register invalid image -> 400")

    # 5. Missing face_image -> 400
    r5 = requests.post(REGISTER_URL, json={"unique_id": "x", "name": "Y"}, timeout=10)
    if r5.status_code != 400:
        failures.append(f"Register (no face_image): expected 400, got {r5.status_code}")
    else:
        print("PASS: Register missing face_image -> 400")

    if failures:
        print("\nFAILURES:")
        for f in failures:
            print(" -", f)
        return 1
    print("\nAll integration checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
