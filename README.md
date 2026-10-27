# Juanitor

A local AI assistant that watches my homelab server and explains what broke.
Runs fully on a recycled 2011 Lenovo PC (no GPU, no cloud).

**Status:** work in progress (v0.1)

## What it does
- Checks disks, CPU temperature, memory and backups on a schedule
- Remembers past readings and only alerts once per problem (no spam)
- Sends push alerts to my phone through a self-hosted ntfy server
- Uses a small local model (Qwen 2.5 3B via Ollama) to explain the likely cause and a next step

## How the AI is kept honest
- Plain Python detects problems; the AI only explains them
- Evidence is collected first and kept short
- Answers must follow a fixed JSON format, and are validated in code
- If the AI is slow or wrong, the plain alert still goes out
- An evaluation set scores the AI on realistic scenarios (`python -m evals.run`)

## Stack
Python, SQLite, Ollama, Docker, ntfy, Caddy
