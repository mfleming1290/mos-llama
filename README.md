# MOS Llama

Combined MOS plugin for llama-swap and persistent llama.cpp inference backends. Based on the MOS llama-swap plugin by ich777 (GPL-3.0; see LICENSE and THIRD_PARTY.md).

## Current development state

- Vue settings/configuration UI is adapted from the donor and builds under `page/`.
- `llama_swap` manages the upstream llama-swap binary.
- `llama_backend` stages Vulkan packages in MOS optional package storage and installs a version-checked upstream `llama` binary under `<install_path>/runtime/bin/llama`.
- MOS root filesystem is disposable: runtime installation path must be under `/mnt/home`; installed Vulkan `.deb` files are staged under `/boot/optional/packages` for boot installation.
- Backends may be selected as Vulkan if available or CPU fallback. ROCm and CUDA are not yet supported by this installer.
- Existing Apps installation uses `/mnt/home/appdata/llama-swap` and must not be overwritten by deployment testing.

## Development

```sh
bash -n llama_swap llama_backend functions
cd page && npm ci && npm run build
```

## Status

Local frontend and .deb package build successfully, but hardware-backed runtime and reboot persistence have not been qualified. MOS plugin lifecycle hooks are retained in tagged source; packaged binaries live under /usr/bin/plugins. Not pushed or published.
