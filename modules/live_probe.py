from pathlib import Path
import asyncio
import aiohttp
import random
import logging

# modules/live_probe.py

# A small list of User-Agents for header spoofing
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (X11; Linux x86_64)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)"
]

def setup_logger(log_file: Path) -> logging.Logger:
    logger = logging.getLogger("live_probe")
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(log_file, mode='a')
    fh.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    fh.setFormatter(formatter)
    # Avoid duplicate handlers
    if not logger.handlers:
        logger.addHandler(fh)
    return logger

async def probe_url(session: aiohttp.ClientSession, url: str, logger: logging.Logger) -> str | None:
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    try:
        async with session.get(url, headers=headers) as resp:
            status = resp.status
            if status < 400:
                logger.info(f"Alive: {url} (Status {status})")
                return url
            else:
                logger.info(f"Dead:  {url} (Status {status})")
    except Exception as e:
        logger.error(f"Error probing {url}: {e}")
    return None

async def run_probes(subdomains: list[str], output_dir: Path, log_file: Path):
    logger = setup_logger(log_file)
    timeout = aiohttp.ClientTimeout(total=5)
    connector = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        tasks = []
        for sub in subdomains:
            for scheme in ("http://", "https://"):
                tasks.append(probe_url(session, f"{scheme}{sub}", logger))
        results = await asyncio.gather(*tasks)
    # Filter and write live URLs
    live_urls = sorted({url for url in results if url})
    output_file = output_dir / "live_subdomains.txt"
    with open(output_file, "w") as f:
        for url in live_urls:
            f.write(f"{url}\n")
    return live_urls

def run(domain: str, output_dir: Path):
    subdomains_file = output_dir / "subdomains.txt"
    log_file = output_dir / "logs" / "live_probe.log"
    if not subdomains_file.exists():
        print(f"[!] No subdomains.txt found for {domain}. Please run subdomain enumeration first.")
        return

    subdomains = sorted({
        line.strip() for line in subdomains_file.read_text().splitlines() if line.strip()
    })

    print(f"[*] Probing {len(subdomains)} subdomains for liveness (http + https)...")
    live = asyncio.run(run_probes(subdomains, output_dir, log_file))
    print(f"[+] Live hosts found: {len(live)}. Results saved to live_subdomains.txt")
