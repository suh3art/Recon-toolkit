# modules/dir_fuzz.py

import subprocess
import json
from pathlib import Path

def run(domain: str, output_dir: Path, wordlist: str = "common.txt", threads: int = 40):
    """
    1) Run ffuf against http://<domain>/FUZZ
    2) Save full JSON to ffuf_results.json
    3) Save concise list of found paths to found_paths.txt
    """
    target_url          = f"http://{domain}/FUZZ"
    results_file        = output_dir / "ffuf_results.json"
    paths_file          = output_dir / "found_paths.txt"
    log_file            = output_dir / "logs" / "dir_fuzz.log"
    log_file.parent.mkdir(exist_ok=True)

    ffuf_cmd = [
        "ffuf",
        "-u", target_url,
        "-w", wordlist,
        "-t", str(threads),
        "-o", str(results_file),
        "-of", "json",
        "-mc", "200,301,302"
    ]

    # Run ffuf
    with open(log_file, "a") as log:
        log.write(f"[*] Running ffuf: {' '.join(ffuf_cmd)}\n")
        subprocess.run(ffuf_cmd, stdout=log, stderr=log, text=True)

    # Parse JSON and extract paths
    try:
        data = json.loads(results_file.read_text())
        hits = [entry["input"]["value"] for entry in data.get("results", [])]
    except Exception:
        hits = []

    # Write found paths
    with open(paths_file, "w") as out:
        for p in sorted(set(hits)):
            out.write(p + "\n")

    print(f"[+] Directory fuzzing complete: {len(hits)} hits saved to {paths_file}")

