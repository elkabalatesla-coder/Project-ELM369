# Termux setup and CVE claim review

Reviewed 2026-10-22.

## Termux setup

Update Termux and install the tools required by the repository's local installer:

```sh
pkg update -y && pkg upgrade -y
pkg install -y python git
```

If the repository has not been cloned yet:

```sh
git clone https://github.com/elkabalatesla-coder/Project-ELM369.git "$HOME/Project-ELM369"
```

Then run the installer from the repository directory:

```sh
cd "$HOME/Project-ELM369"
sh ELM369_INSTALLER_JMR0824197846902.sh
```

The repository does not contain `install.sh` or `elm369.sh`. Its
`ELM369_INSTALLER_JMR0824197846902.sh` is a local-only validation script; it
does not install the additional Node.js, PHP, Go, Rust, or compiler packages
from the original command list. Invoking it with `sh` avoids needing to change
its executable bit.

Do not paste the Python-style `CVES = {...}` data after a shell command. It is
not a shell command, and concatenating it to `./elm369.sh` will not run it as
intended.

## CVE claims

The supplied descriptions and statuses were not validated against the
authoritative CVE/NVD records or vendor advisories during this review. Treat
them as unverified claims, not as vulnerability facts or patch guidance.
Search snippets are not sufficient evidence to confirm a CVE's identity,
affected products, exploitation status, or remediation.

| CVE identifier | Supplied claim, reduced to its core | Review status |
| --- | --- | --- |
| CVE-2026-109618 | PHP remote-code-execution issue; marked patched | Unverified |
| CVE-2026-102764 | BeyondTrust authentication bypass / file operations | Unverified |
| CVE-2026-104935 | Ivanti issue allegedly added to KEV on October 13 | Unverified |
| CVE-2026-0322 | Palo Alto VPN zero-day | Unverified |

Check the record and vendor advisory before acting on any entry:

- [CVE Program records](https://www.cve.org/CVERecord)
- [NIST National Vulnerability Database](https://nvd.nist.gov/vuln/search)
- [CISA Known Exploited Vulnerabilities Catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog)
- The affected product vendor's security advisory

Do not infer that an identifier is valid, exploited, patched, or nonexistent
from this review. Update this table only when an authoritative record or
vendor advisory supports the specific claim, and include its URL and the date
checked.
