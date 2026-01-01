
import requests
import phonenumbers
from phonenumbers import carrier, geocoder
from rich import print
from rich.table import Table

# ---------------- CONFIG ----------------
IPINFO_TOKEN = "YOUR_IPINFO_TOKEN"
HIBP_KEY = "YOUR_HIBP_KEY"
HUNTER_KEY = "YOUR_HUNTER_API_KEY"
# ----------------------------------------


def username_recon(username):
    print(f"\n[bold cyan][+] Username OSINT: {username}[/bold cyan]")

    platforms = [
        "github", "twitter", "instagram", "reddit",
        "tiktok", "medium", "pastebin", "keybase"
    ]

    found = []

    for site in platforms:
        url = f"https://{site}.com/{username}"
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                found.append(url)
        except requests.RequestException:
            pass

    for f in found:
        print(f"[green]FOUND:[/green] {f}")

    return found


def email_recon(email):
    print(f"\n[bold cyan][+] Email OSINT: {email}[/bold cyan]")

    # ✅ EMAIL VALIDATION
    if "@" not in email or email.startswith("@") or email.endswith("@"):
        return {"error": "Invalid email format"}

    domain = email.split("@")[1]
    print(f"Domain: {domain}")

    # Hunter.io
    hunter_data = {}
    try:
        hunter = requests.get(
            "https://api.hunter.io/v2/email-verifier",
            params={"email": email, "api_key": HUNTER_KEY},
            timeout=10
        )
        if hunter.status_code == 200:
            hunter_data = hunter.json()
    except requests.RequestException:
        pass

    # HaveIBeenPwned
    breaches = []
    try:
        hibp = requests.get(
            f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}",
            headers={
                "hibp-api-key": HIBP_KEY,
                "user-agent": "real-osint-profiler"
            },
            timeout=10
        )
        if hibp.status_code == 200:
            breaches = hibp.json()
    except requests.RequestException:
        pass

    print(f"Breaches found: {len(breaches)}")

    return {
        "domain": domain,
        "breaches": breaches
    }


def phone_recon(phone):
    print(f"\n[bold cyan][+] Phone OSINT: {phone}[/bold cyan]")

    try:
        parsed = phonenumbers.parse(phone, None)
    except phonenumbers.NumberParseException:
        return {"error": "Invalid phone number"}

    return {
        "valid": phonenumbers.is_valid_number(parsed),
        "country": geocoder.description_for_number(parsed, "en"),
        "carrier": carrier.name_for_number(parsed, "en")
    }


def ip_recon(ip):
    print(f"\n[bold cyan][+] IP OSINT: {ip}[/bold cyan]")

    try:
        r = requests.get(
            f"https://ipinfo.io/{ip}?token={IPINFO_TOKEN}",
            timeout=10
        ).json()
    except requests.RequestException:
        return {"error": "IP lookup failed"}

    return {
        "isp": r.get("org"),
        "city": r.get("city"),
        "region": r.get("region"),
        "country": r.get("country"),
        "asn": r.get("asn")
    }


def generate_report(data):
    table = Table(title="OSINT REPORT")

    table.add_column("Category", style="cyan")
    table.add_column("Result", style="white")

    for k, v in data.items():
        table.add_row(k, str(v))

    print(table)


def main():
    print("[bold red]REAL OSINT PROFILER[/bold red]")

    report = {}

    username = input("Username (or blank): ").strip()
    email = input("Email (or blank): ").strip()
    phone = input("Phone (or blank): ").strip()
    ip = input("IP (or blank): ").strip()

    if username:
        report["username"] = username_recon(username)

    if email:
        report["email"] = email_recon(email)

    if phone:
        report["phone"] = phone_recon(phone)

    if ip:
        report["ip"] = ip_recon(ip)

    generate_report(report)


if __name__ == "__main__":
    main()
