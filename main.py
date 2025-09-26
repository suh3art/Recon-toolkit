# main.py

from pathlib import Path
from modules import subdomain_enum, live_probe, js_scraper, wayback_urls, dir_fuzz

def get_target_from_user():
    """
    Prompt until the user enters a valid host or host:port,
    or presses Enter to quit.
    """
    while True:
        inp = input("🎯 Enter the root target (e.g., example.com or localhost:3000): ").strip()
        if not inp:
            print("👋 Exiting recon toolkit.")
            exit(0)

        # Split host and optional port
        if ":" in inp:
            host, port = inp.split(":", 1)
            if not port.isdigit():
                print("❌ Port must be numeric. Try again.")
                continue
        else:
            host = inp

        # Validate host: allow localhost, IPs, or domains containing at least one dot
        if host == "localhost" or host.replace(".", "").isdigit() or "." in host:
            return inp  # keep the port if present
        else:
            print("❌ Invalid host. Use domain (example.com), IP (127.0.0.1), or localhost[:port].")

def setup_workspace(target: str) -> Path:
    """
    Create (or reuse) output/<target_dir> folder and logs/ inside it.
    Replace ':' in the folder name so that localhost:3000 → localhost_3000
    """
    safe_name = target.replace(":", "_")
    base = Path("output") / safe_name
    (base / "logs").mkdir(parents=True, exist_ok=True)
    print(f"📁 Workspace ready: {base}")
    return base

if __name__ == "__main__":
    while True:
        target     = get_target_from_user()
        output_dir = setup_workspace(target)

        # 1) Passive Subdomain Enumeration
        sub_file = output_dir / "subdomains.txt"
        if sub_file.exists():
            skip = input(f"⚠️ subdomains.txt exists for {target}. Skip? (Y/N): ").strip().lower() == "y"
            if not skip:
                subdomain_enum.run(target, output_dir)
        else:
            subdomain_enum.run(target, output_dir)

        # 2) Live Probing
        live_file = output_dir / "live_subdomains.txt"
        if live_file.exists():
            skip = input(f"⚠️ live_subdomains.txt exists for {target}. Skip? (Y/N): ").strip().lower() == "y"
            if not skip:
                live_probe.run(target, output_dir)
        else:
            live_probe.run(target, output_dir)

        # 3) JS Scraping
        js_file = output_dir / "js_urls.txt"
        if js_file.exists():
            skip = input(f"⚠️ js_urls.txt exists for {target}. Skip? (Y/N): ").strip().lower() == "y"
            if not skip:
                js_scraper.run(target, output_dir)
        else:
            js_scraper.run(target, output_dir)

        # 4) Wayback URL Collection
        wayback_urls.run(target, output_dir)

        # 5) Directory Fuzzing
        ffuf_file = output_dir / "ffuf_results.json"
        if ffuf_file.exists():
            skip = input(f"⚠️ ffuf_results.json exists for {target}. Skip? (Y/N): ").strip().lower() == "y"
            if not skip:
                dir_fuzz.run(target, output_dir)
        else:
            dir_fuzz.run(target, output_dir)

        print(f"\n✅ Full recon pipeline complete for: {target}\n")
