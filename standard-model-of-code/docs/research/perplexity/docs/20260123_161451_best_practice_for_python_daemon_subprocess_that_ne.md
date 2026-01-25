# Research: Best practice for Python daemon subprocess that needs API keys from Doppler secrets manager. Options...

> **Date:** 2026-01-23 16:14:51
> **Source:** perplexity-mcp
> **Model:** sonar-pro
> **Checksum:** `sha256:f77ceb21ad8eb4c7075dc5082ea50fb3b32967c0b8922868bad87b92fe9ade1f`
> **Raw JSON:** `raw/20260123_161451_best_practice_for_python_daemon_subprocess_that_ne.json`

---

## Query

Best practice for Python daemon subprocess that needs API keys from Doppler secrets manager. Options: (A) wrap subprocess in 'doppler run', (B) export env vars before daemon start, (C) use launchd EnvironmentVariables. Which is most reliable for macOS launchd-managed daemons?

---

## Response

**Option (C) using launchd EnvironmentVariables is the most reliable for macOS launchd-managed daemons.**

Launchd on macOS natively supports setting environment variables directly in the plist file via the `EnvironmentVariables` key, allowing your Python daemon subprocess to access Doppler-fetched API keys securely at launch time without runtime dependencies.[7] This approach avoids shell wrappers or pre-export steps that can fail in daemon contexts.

### Comparison of Options
| Option | Description | Reliability for launchd Daemons | Key Limitations |
|--------|-------------|--------------------------------|-----------------|
| **(A) Wrap subprocess in 'doppler run'** | Use `doppler run -- python your_daemon.py` to inject secrets at runtime via Doppler CLI.[4] | Low: launchd executes commands directly without shell interpretation; wrappers may not propagate env vars reliably, and CLI requires authentication/availability.[2][4] |
| **(B) Export env vars before daemon start** | Fetch secrets (e.g., `doppler run -- printenv`) and export manually before launchd loads the plist.[4] | Medium: Manual step is error-prone, non-reproducible across restarts/updates, and doesn't persist if launchd reloads independently. |
| **(C) launchd EnvironmentVariables** | In your `~/Library/LaunchAgents/yourdaemon.plist`:<br>```xml<br><?xml version="1.0" encoding="UTF-8"?><br><!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"...><br><plist version="1.0"><br><dict><br>  <key>EnvironmentVariables</key><br>  <dict><br>    <key>API_KEY</key><br>    <string>your_doppler_fetched_value</string><br>  </dict><br>  <key>ProgramArguments</key><br>  <array><br>    <string>python</string><br>    <string>/path/to/daemon.py</string><br>  </array><br></dict><br></plist><br>```<br>Load with `launchctl load ~/Library/LaunchAgents/yourdaemon.plist`. | **High: Native, persistent, and secure.** Variables are set per-launch without external tools; Doppler values can be fetched once and stored securely (rotate via Doppler).[4] |

### Recommended Workflow
1. Install Doppler CLI and fetch secrets: `doppler run -- echo "API_KEY=value" > /tmp/secrets.txt` (secure tmp, or use keychain).[4]
2. Edit plist with `EnvironmentVariables` using fetched values (avoid committing secrets).[1][4]
3. In Python daemon: `import os; api_key = os.environ['API_KEY']`.
4. Reload: `launchctl unload/load your.plist`.

This aligns with Doppler's runtime injection best practices (env vars over files) while leveraging launchd's strengths for daemons.[2][4][7] For dynamic rotation, combine with Doppler service tokens or periodic plist updates.

---

## Citations

1. https://www.youtube.com/watch?v=L3RuE7BMruE
2. https://www.doppler.com/blog/secrets-management-best-practices-for-ephemeral-environments
3. https://www.youtube.com/watch?v=7UaVLpbtNCc
4. https://www.doppler.com/blog/doppler-secrets-setup-guide
5. https://www.doppler.com/blog/5-secrets-management-best-practices-for-new-developers
6. https://news.ycombinator.com/item?id=40941412
7. https://discuss.python.org/t/proper-way-to-create-a-daemon-process/79824
8. https://serverascode.com/2021/12/01/dev-experience-doppler-secrets.html

---

## Usage Stats

- Prompt tokens: 62
- Completion tokens: 653
- Total tokens: 715
