---
name: trading-credential-security-check
description: Use when checking crypto or trading repos for exposed exchange credentials, wallet private keys, API tokens, unsafe env/config samples, or credential-printing helper scripts.
---

# Trading Credential Security Check

## Purpose

Run a narrow credential-exposure pass for trading projects. Keep the scope to hardcoded API keys, private keys, wallet keys, tokens, cookies, unsafe credential examples, and helper code that prints or logs secrets.

## Rules

- Never paste raw secrets into chat, docs, commits, or terminal summaries.
- Treat `.env` as allowed local storage only if it is ignored or otherwise not committed.
- Treat `.env.example`, docs, tests, YAML config, scripts, notebooks, archives, and helper tools as exposure surfaces.
- Do not run live trading probes unless the user explicitly asks; credential review should not place orders.
- Do not change trading behavior while cleaning examples, unless a credential default directly creates exposure risk.

## Workflow

1. Load repo instructions and check worktree state.
2. Confirm `.env` storage status:
   - `git ls-files .env .env.*`
   - `git check-ignore -v .env .env.*`
3. Run a redacted scan:
   - `python3 ~/.agents/skills/trading-credential-security-check/scripts/redacted_secret_scan.py /path/to/repo`
4. Classify findings before editing.
5. Patch only true exposure surfaces:
   - replace sample values with `<ENV_VAR_NAME>` or `${ENV_VAR_NAME}`
   - replace config-file credential examples with env references
   - change helper tools to use hidden input for private keys where practical
   - stop printing/exporting raw private keys; print placeholders and instructions to write `.env`
   - update tests only when they assert the changed credential behavior
6. Verify:
   - rerun the redacted scan
   - run focused tests or `py_compile` for changed scripts
   - inspect `git diff` for accidental raw values
7. Report a rotation checklist by credential class, not by raw value.

## Classification Guide

True exposures:

- PEM private key blocks.
- 64-char hex strings near `private_key`, `secret`, `seed`, or `mnemonic`.
- Provider tokens such as `sk-...`, `ghp_...`, `xoxb-...`, JWTs, cookies, or AWS access keys.
- Exchange keys in docs, samples, tests, config YAML, scripts, or archives that look usable rather than obviously fake.
- Helper tools that echo entered private keys, API secrets, cookies, or bearer tokens.
- `.env.example` containing real-looking values instead of placeholders.

Usually safe after review:

- Empty strings.
- `${ENV_VAR}`, `$ENV_VAR`, or `<ENV_VAR>` placeholders.
- Values containing `example`, `placeholder`, `changeme`, `dummy`, `demo_`, `test_`, `redacted`, or `public_data_only`.
- Short numeric indexes in tests or docs, unless they identify a real live account and are paired with exposed secrets.

## Rotation Checklist Template

- Revoke and recreate exposed exchange API keys.
- Rotate Lighter API key private keys; confirm account/API key indexes still match.
- Rotate Backpack API key plus private key pair; use read/trade permissions only, never withdrawal.
- Rotate Hyperliquid or wallet private keys by moving funds to a fresh wallet; wallet keys cannot be safely "changed" in place.
- Invalidate browser cookies/session tokens such as Variational cookies by logging out all sessions and reconnecting.
- Search logs, shell history, notebooks, archives, and CI artifacts for the same values and purge where feasible.
- Update local `.env` with the new credentials and keep `.env` ignored.
