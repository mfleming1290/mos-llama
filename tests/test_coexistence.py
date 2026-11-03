"""Regression guard: MOS Llama must coexist with mos-llama-swap-plugin."""
from pathlib import Path
import json
import re

root = Path(__file__).resolve().parents[1]
workflow = (root / '.github/workflows/build-plugin.yaml').read_text()
packager = (root / 'scripts/package-local.sh').read_text()
vue = (root / 'page/src/Plugin.vue').read_text()
functions = (root / 'functions').read_text()
router = (root / 'llama_router').read_text()
settings = json.loads((root / 'settings.json').read_text())
assert (root / 'llama_router').is_file()
assert not (root / 'llama_swap').exists()
assert 'usr/bin/plugins/llama_router' in packager
assert 'usr/bin/plugins/llama_swap' not in packager
assert 'llama_router' in workflow and 'Old plugin file collision' in workflow
assert "command: 'llama_router'" in vue
assert "command: 'llama_swap'" not in vue
assert '/usr/bin/plugins/llama_router start' in functions
assert '/var/run/mos-llama.pid' in router
assert '/boot/optional/plugins/llama' in router
assert settings['install_path'] == '/mnt/home/appdata/llama'
assert settings['port'] == '8081'
assert "DEFAULT_PORT = '8081'" in vue
assert 'PORT="8081"' in router
assert "name: 'llama'" in (root / 'page/plugin.config.js').read_text()
assert "version: '0.0.3'" in (root / 'page/plugin.config.js').read_text()
assert '/plugins/llama/main.js' in (root / 'page/index.html').read_text()
print('MOS Llama coexistence source checks passed')
