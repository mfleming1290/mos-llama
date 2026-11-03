# MOS plugin conventions and constraints
- Intended plugin identity is `mos-llama`; maintain consistency across repository, plugin name, package metadata, and MOS Hub entry when authored.
- MOS plugin requires `page/src/Plugin.vue` and `page/plugin.config.js` with a no-spaces internal name; `functions` may implement `install`, `uninstall`, `plugin_update`, `mos_start`, `mos_osupdate` and custom operations.
- MOS has disposable rootfs. Persist backend/model assets under `/mnt/home/appdata` and optional `.deb` dependencies under `/boot/optional/packages`; validate dependency closure and reboot recovery.
- Keep llama-swap and llama.cpp as upstream binaries rather than source forks; avoid overwriting an existing working Apps deployment.
- No repository-specific style or naming rules have yet been implemented; inspect adopted donor source before setting them.