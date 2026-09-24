# Behaviour Lens

Behaviour Lens turns one everyday observation about human behaviour into a concise, research-backed brief and keeps the result in an Obsidian-compatible Markdown archive. It also reviews the archive weekly, monthly, or quarterly to surface recurring themes and changes in attention without diagnosing the observer.

## What it does

- Treats an observation as a hypothesis, never as a fact to confirm.
- Produces an approximately 800–1,100 word / five-minute brief.
- Separates evidence status, mechanisms, competing explanations, AI-and-society relevance, current affairs, synthesis, and traceable sources.
- Saves one Markdown file per observation, with YAML frontmatter.
- Searches notes and retrieves them by date period.
- Saves weekly, monthly, and quarterly pattern reviews.
- Describes only the record: an absent topic means “not present in these notes,” not that the user failed to notice it.

## Install from GitHub

Clone the repository into your local plugins directory, add it to a personal or team marketplace, and install it through Codex. If you only want to inspect or adapt the plugin, the repository is self-contained and has no runtime dependencies beyond Python 3.

## Configure the Obsidian vault

1. Choose an existing Obsidian vault or create one.
2. Set `OBSIDIAN_VAULT_PATH` to its absolute path before starting Codex, for example `export OBSIDIAN_VAULT_PATH="/absolute/path/to/My Vault"`.
3. Install it from the marketplace that points to your clone.
4. Start a new Codex task, enable Behaviour Lens, and enter only your observation.

If `OBSIDIAN_VAULT_PATH` is unset, the service uses `~/Documents/Obsidian/Behaviour Lens Vault`. It creates only `Behaviour Lens/Observations` and `Behaviour Lens/Pattern Reviews` inside the chosen vault.

## Typical prompts

- `People on the train seem more willing to watch strangers through a phone camera than look at them directly.`
- `Review my observation patterns this week.`
- `Create my monthly pattern review for August 2026.`
- `What changed in what I attended to this quarter?`

## Vault layout

```text
Behaviour Lens/
├── Observations/
│   └── 2026-09-25-mediated-decisions--<id>.md
└── Pattern Reviews/
    └── 2026-W39-weekly-pattern-review--<id>.md
```

The persistence tools return file paths and machine-readable records. Obsidian does not need a proprietary database or plugin.

## Boundaries and validation

Notes remain in the configured local vault. Codex performs research when creating a brief; current claims must be checked at run time and linked. The instructions forbid invented citations, forced AI connections, psychological diagnosis, and claims that missing themes prove perceptual blind spots.

Run `python3 -m unittest discover -s tests -v` from this directory. If you have the Codex `plugin-creator` skill installed, also run its `scripts/validate_plugin.py .` validator against the repository root.

The MCP server uses only Python's standard library.

## License

MIT. See [LICENSE](LICENSE).
