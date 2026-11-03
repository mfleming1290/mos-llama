# Completion gates (initial)
- No executable test/build/lint commands exist yet; do not claim test completion from an empty repo.
- Before accepting implementation: inspect Git diff/status; run actual frontend/build/package checks once added; verify MOS plugin identity and required files; verify backend installation and lifecycle in a disposable environment; test model inference via llama-swap; separately qualify persistence after MOS reboot.
- Publishing to GitHub or MOS Hub and rebooting Apps require explicit authorization; report each independently.
- Record Serena-vs-GoMCP observations in `SERENA_GOMCP_NOTES.md` after meaningful milestones, as directed by the user's Serena guide.