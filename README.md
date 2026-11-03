# MOS Llama

Combined MOS plugin for llama-swap and persistent llama.cpp inference backends. Based on the MOS llama-swap plugin by ich777 (GPL-3.0; see LICENSE and THIRD_PARTY.md).

## Current development state

- Vue settings/configuration UI is adapted from the donor and builds under `page/`.
- `llama_router` manages the upstream llama-swap binary.
- `llama_backend` stages Vulkan packages in MOS optional package storage and installs a version-checked upstream `llama` binary under `<install_path>/runtime/bin/llama`.
- MOS root filesystem is disposable: runtime installation path must be under `/mnt/home`; installed Vulkan `.deb` files are staged under `/boot/optional/packages` for boot installation.
- Backends may be selected as Vulkan if available or CPU fallback. ROCm and CUDA are not yet supported by this installer.
- Existing Apps installation uses `/mnt/home/appdata/llama-swap` and must not be overwritten by deployment testing.

## Development

```sh
bash -n llama_router llama_backend functions
cd page && npm ci && npm run build
```

## Status

First release is an experimental integration preview, not yet hardware/reboot-qualified. Avoid installing over the existing llama-swap plugin on Apps until migration has been tested.

Local frontend and .deb package build successfully, but hardware-backed runtime and reboot persistence have not been qualified. MOS plugin lifecycle hooks are retained in tagged source; packaged binaries live under /usr/bin/plugins. Initial source checkpoint is pushed; the first tagged release is prepared for controlled testing.

## Coexistence with the original MOS llama-swap plugin

Version 0.0.3 changes the MOS control command to `llama_router` rather than `llama_swap`, avoiding the Debian file ownership collision with `mos-llama-swap-plugin` 0.5.1. The two plugins have separate MOS settings (`llama` versus `llama-swap`), separate PID files, and default to different HTTP ports (`8081` versus `8080`). The upstream executable is still called `llama-swap` but resides in this plugin's own persistent installation directory.

Install MOS Llama **alongside** the existing plugin for testing; do not uninstall the existing plugin or point both plugins at the same install directory. Test model loading and persistence before migrating.
