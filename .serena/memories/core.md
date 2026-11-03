# mos-llama — project map
- Repository: `/home/matt/code/mos-llama`; Git remote `mfleming1290/mos-llama`.
- At initial onboarding, repository contains only Git metadata, `.editorconfig`, `.gitattributes`, `.gitignore`, and Serena config; no plugin source, runtime, or tests yet.
- Intended product (user-established): MOS plugin integrating llama-swap model orchestration with llama.cpp inference backend management, including persistent MOS installation and optional MOS LLM API integration. This is a target, **not implemented behavior**.
- MOS plugin contract to preserve when source is added: mandatory `page/src/Plugin.vue`, `page/plugin.config.js`, optional `functions` and `settings.json`; `mos_start` lifecycle; custom functions via MOS API. Confirm exact behavior against donor/source before implementing.
- Consult `mem:tech_stack` for stack status; `mem:conventions` for MOS-specific constraints; `mem:suggested_commands` and `mem:task_completion` after build tooling is introduced.