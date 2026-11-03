# Serena vs GoMCP observations

## 2026-11-02 — MOS Llama donor import and initial implementation

Client: ChatGPT
Model: GPT-6
Project: mos-llama
Languages: Vue, JavaScript, Bash
Task type: Plugin integration scaffold

### Serena tools used
- `serena_get_symbols_overview`: attempted on `page/src/Plugin.vue`; unable to extract symbols because the newly initialized project still had no active language servers.

### GoMCP tools used
- `run`: donor inspection, source import, bounded editing, Bash syntax validation, and Vue build; functional and fast.

### Serena strengths observed
- Memory onboarding persisted project context and `serena memories check` passed before this milestone.

### GoMCP strengths observed
- Text-oriented Bash, workflow and scaffolding tasks were completed and validated with bounded commands. Vue production build passed.

### Serena weaknesses/friction
- Initial activation of an empty project generated `language_servers: []`; after adding Vue code, symbol overview remained unavailable until LSP setup is refreshed and verified.

### GoMCP weaknesses/friction
- Codeit tunnel disconnected during the first implementation pass; repository edits persisted and were recovered on reconnection.

### Context efficiency
- Source inspection used bounded excerpts instead of repeating full file reads.

### Tool-selection ergonomics
- GoMCP was a better fit for text-heavy initial repo scaffolding; Serena will be preferred for later symbol edits once language servers are active.

### Candidate GoMCP improvement
- No actionable conclusion from this checkpoint.

### Outcome
- Scaffold restored, `bash -n` passed, and Vite build passed. Runtime and MOS installation remain unverified.

## 2026-11-02 — backend stabilization and local packaging

Client: ChatGPT
Model: GPT-6
Project: mos-llama
Languages: Vue, JavaScript, Bash
Task type: Installer correctness, MOS lifecycle, local package build

### Serena tools used
- `serena_activate_project`: project activated; Vue, TypeScript and Bash language servers detected.
- `serena_get_symbols_overview`: Vue top-level overview produced `template` and `script setup`, useful orientation but little detail for large Vue SFC.

### GoMCP tools used
- `run`: inspected working tree, executed bounded tests, generated local .deb and checked payload.

### Serena strengths observed
- Project language servers became available after activating populated repository, unlike initial empty-repo activation.

### GoMCP strengths observed
- Short shell checks validated Bash syntax, mock path tests, Vue production build, and Debian package contents without deployment.

### Serena weaknesses/friction
- Top-level Vue symbol overview only exposed template/script divisions, so fine-grained changes to template and non-symbolic shell/package files were more efficient as bounded textual edits.

### GoMCP weaknesses/friction
- No tool failure on this milestone.

### Context efficiency
- Focused excerpts avoided rereading full Vue component.

### Tool-selection ergonomics
- Semantic overview selected for orientation, GoMCP for text-oriented packaging and execution.

### Candidate GoMCP improvement
- None established.

### Outcome
- Local .deb builds, Bash syntax passes, tests for path-validation behavior pass. No live MOS installation or reboot validation; follow-up necessary.

## 2026-11-02 — Debian package coexistence repair

Client: ChatGPT
Model: GPT-6
Project: mos-llama
Languages: Vue, JavaScript, Bash, GitHub Actions
Task type: Packaging collision and safe side-by-side deployment

### Serena tools used
- `serena_activate_project`: verified correct active repository and available Vue/TypeScript/Bash language servers.
- `serena_get_symbols_overview`: confirmed Vue component is a template and script setup; naming collision was package-path/string-oriented, not a semantic symbol rename.

### GoMCP tools used
- `run`: inspected all executable names and packaging references, performed scoped renaming and validation, built the .deb, and checked its payload.

### Serena strengths observed
- Correct project activation before edits avoided cross-repository confusion.

### GoMCP strengths observed
- Path-based collision was more accurately resolved by text-oriented package inspection and explicit tests than by a semantic symbol rename.

### Serena weaknesses/friction
- Vue symbol overview was too coarse for command string references inside the template and setup script.

### GoMCP weaknesses/friction
- Initial broad text replacement also changed Vue translation keys; caught by focused inspection and corrected before building.

### Context efficiency
- Focused ripgrep across the wrapper, Vue, hooks, workflow, and packaging avoided unrelated source reads.

### Tool-selection ergonomics
- GoMCP was appropriate for executable file paths, package payloads, and release metadata; Serena provided project orientation.

### Candidate GoMCP improvement
- None justified from this checkpoint.

### Outcome
- New `llama_router` wrapper, separate port 8081, version 0.0.3, and coexistence regression tests; local .deb build and checks passed. MOS runtime install still unverified.
