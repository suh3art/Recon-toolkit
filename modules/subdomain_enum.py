# modules/subdomain_enum.py

import subprocess
from pathlib import Path

def run(target_domain: str, output_dir: Path):
    print(f"[+] Running subdomain enumeration for {target_domain}")

    output_file = output_dir / "subdomains.txt"
    log_file = output_dir / "logs" / "subdomain_enum.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)

    # Commands for crt.sh and subfinder
    crtsh_command = (
        f"curl -s 'https://crt.sh/?q=%25.{target_domain}&output=json' | "
        "jq -r '.[].name_value' | sed 's/\\*\\.//g' | sort -u"
    )
    subfinder_command = f"subfinder -d {target_domain} -silent"

    with open(output_file, 'w') as outfile, open(log_file, 'w') as logfile:
        try:
            logfile.write("[*] Running crt.sh enumeration...\n")
            crtsh_result = subprocess.check_output(crtsh_command, shell=True, text=True)
            outfile.write(crtsh_result)
            logfile.write(crtsh_result + "\n")

            logfile.write("[*] Running subfinder enumeration...\n")
            subfinder_result = subprocess.check_output(subfinder_command, shell=True, text=True)
            outfile.write(subfinder_result)
            logfile.write(subfinder_result + "\n")

            print(f"[+] Subdomain enumeration complete. Results saved to {output_file}")
        except subprocess.CalledProcessError as e:
            logfile.write(f"[!] Error during subdomain enumeration: {e}\n")
            print(f"[!] Subdomain enumeration failed: {e}")
