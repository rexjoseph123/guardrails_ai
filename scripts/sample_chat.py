import json
import sys
import httpx


def main():
    prompt = " ".join(sys.argv[1:]) or "Tell me a joke about cats"
    payload = {"prompt": prompt}
    with httpx.Client(timeout=30) as client:
        resp = client.post("http://localhost:8000/chat", json=payload)
        resp.raise_for_status()
        data = resp.json()
        if data.get("blocked"):
            print(f"Blocked: {data.get('reason')}")
        else:
            print(data.get("content", ""))


if __name__ == "__main__":
    main()


