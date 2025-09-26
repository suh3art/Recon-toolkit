# modules/js_scraper.py

import subprocess
from pathlib import Path

def run(domain: str, output_dir: Path):
    """
    1) Gather JS URLs via gau
    2) Save them to js_urls.txt
    3) Curl each URL and scan for secrets
    4) Log to found_secrets.txt & js_scraper.log
    """
    js_urls_file = output_dir / "js_urls.txt"
    secrets_file = output_dir / "found_secrets.txt"
    log_file     = output_dir / "logs" / "js_scraper.log"
    log_file.parent.mkdir(exist_ok=True)

    # 1) Gather JS URLs
    gau_cmd = ["gau", domain]
    with open(js_urls_file, "w") as out_js, open(log_file, "a") as log:
        log.write("[*] Running gau to collect JS URLs...\n")
        subprocess.run(gau_cmd, stdout=out_js, stderr=log, text=True)

    # 2) Scan each JS for secrets
    patterns = ["apiKey", "token", "secret", "auth", "clientId", "key"]
    with open(secrets_file, "w") as out_sec, open(log_file, "a") as log:
        log.write("[*] Scanning JS for secrets...\n")
        for url in js_urls_file.read_text().splitlines():
            url = url.strip()
            if not url.lower().endswith(".js"):
                continue
            try:
                proc = subprocess.Popen(
                    ["curl", "-sL", url],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                for line in proc.stdout:
                    for pat in patterns:
                        if pat in line:
                            out_sec.write(f"{url}: {line.strip()}\n")
            except Exception as e:
                log.write(f"[!] Error fetching {url}: {e}\n")

    print(f"[+] JS scraping done. URLs → {js_urls_file}, secrets → {secrets_file}")
