#!/usr/bin/env python3
"""Check MOS plugin release identity and required source before publishing."""
import json
import pathlib
import re
import subprocess

root = pathlib.Path(__file__).resolve().parents[1]
package = json.loads((root / 'page/package.json').read_text())
lock = json.loads((root / 'page/package-lock.json').read_text())
config = (root / 'page/plugin.config.js').read_text()
match = re.search(r"version:\s*'([^']+)'", config)
assert match, 'plugin.config.js version missing'
version = match.group(1)
assert re.fullmatch(r'\d+\.\d+\.\d+', version), 'Version must be numeric x.y.z'
assert version == package['version'] == lock['version'] == lock['packages']['']['version'], 'Version mismatch'
assert package['name'] == lock['name'] == lock['packages']['']['name'] == 'mos-llama-plugin'
assert "name: 'llama'" in config
for name in ('functions', 'settings.json', 'llama_router', 'llama_backend', 'page/src/Plugin.vue', '.github/workflows/build-plugin.yaml'):
    assert (root / name).is_file(), f'Missing required source: {name}'
assert json.loads((root / 'settings.json').read_text())['install_path'].startswith('/mnt/home/')
print(f'Release source checks passed: {version}')
