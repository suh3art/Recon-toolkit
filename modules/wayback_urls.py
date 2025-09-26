# modules/wayback_urls.py

import requests
from pathlib import Path
import re

def run(domain: str, output_dir: Path):
    """
    1) Query the Wayback CDX API for archived URLs
    2) Save to wayback_urls.txt
    3) Filter for juicy endpoints into suspicious_wayback.txt
    """
    wayback_file    = output_dir / "wayback_urls.txt"
    suspicious_file = output_dir / "suspicious_wayback.txt"
    log_file        = output_dir / "logs" / "wayback_urls.log"
    log_file.parent.mkdir(exist_ok=True)

    # 1) Fetch from CDX API
    api_url = (
        "https://web.archive.org/cdx/search/cdx"
        f"?url={domain}"
        "&output=json"
        "&fl=original"
        "&collapse=urlkey"
    )
    try:
        resp = requests.get(api_url, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        with open(log_file, "a") as log:
            log.write(f"[!] CDX API error for {domain}: {e}\n")
        print(f"[!] Failed to query Wayback CDX for {domain}. See log.")
        return

    # Parse and dedupe URLs (skip header row if present)
    all_urls = []
    for entry in data:
        if isinstance(entry, list):
            url = entry[0]
        else:
            # some responses might be flat lists
            url = entry
        if url and url not in all_urls:
            all_urls.append(url)

    # 2) Write all archived URLs
    with open(wayback_file, "w") as out_all, open(log_file, "a") as log:
        log.write(f"[*] Retrieved {len(all_urls)} URLs via CDX API\n")
        for url in all_urls:
            out_all.write(url + "\n")

    # 3) Filter juicy endpoints
    patterns = [
        r"login", r"logout", r"register", r"admin", r"dashboard", r"user",
        r"config", r"settings", r"backup", r"secret", r"token", r"api",
        r"auth", r"csrf", r"upload", r"download", r"export", r"import",
        r"adminer", r"phpmyadmin", r"wp-admin", r"wp-login", r"\.json",
        r"\.xml", r"\.php", r"\.aspx", r"\.jsp", r"\.action", r"sitemap\.xml",
        r"\.git", r"\.env", r"credentials", r"db", r"certificate", r"cert\.pem",
        r"key", r"metrics", r"health", r"status", r"logs", r"error", r"debug",
        r"backup\.zip", r"tar\.gz"
    ]
    regex = re.compile("|".join(patterns), re.IGNORECASE)

    count = 0
    with open(suspicious_file, "w") as out_suspicious, open(log_file, "a") as log:
        log.write("[*] Filtering suspicious endpoints from cd x URLs...\n")
        for url in all_urls:
            if regex.search(url):
                out_suspicious.write(url + "\n")
                count += 1
        log.write(f"[*] Suspicious endpoints saved: {count}\n")

    print(f"[+] Wayback URLs saved to: {wayback_file}")
    print(f"[+] Suspicious endpoints saved to: {suspicious_file}")
