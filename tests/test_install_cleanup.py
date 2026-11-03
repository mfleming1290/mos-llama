"""Exercise install_backend with fake upstream binaries, without touching MOS."""
from pathlib import Path
import subprocess
import tempfile

script = Path('llama_backend').resolve()
with tempfile.TemporaryDirectory() as directory:
    # Source function declarations without running the dispatch at the bottom.
    harness = r'''
set -euo pipefail
source <(sed '/^case "${1:-}" in/,$d' "$BACKEND_SCRIPT")
runtime() { printf '%s/runtime\n' "$TEST_ROOT"; }
arch() { printf 'x86_64\n'; }
probe() { printf 'b12019 cpu generic\n'; }
fetch_zst() {
  cat > "$2" <<'FAKE'
#!/usr/bin/env bash
case "$1" in
  version) echo 'version: 0.8.0-dev (build 12019, commit test)' ;;
  serve) test "${2:-}" = '--help' ;;
  *) exit 1 ;;
esac
FAKE
}
install_backend
[[ -x "$TEST_ROOT/runtime/bin/llama" ]]
[[ "$(cat "$TEST_ROOT/runtime/bin/llama.version")" = b12019 ]]
[[ "$(cat "$TEST_ROOT/runtime/bin/llama.backend")" = cpu ]]
! find "$TEST_ROOT/runtime" -maxdepth 1 -name '.install.*' | grep -q .
'''
    result = subprocess.run(['bash', '-c', harness], env={
        'PATH': '/usr/bin:/bin',
        'BACKEND_SCRIPT': str(script),
        'TEST_ROOT': directory,
    }, capture_output=True, text=True)
    assert result.returncode == 0, f'{result.stdout}\n{result.stderr}'
    assert 'Installed llama.cpp b12019' in result.stdout
    assert 'unbound variable' not in result.stderr
print('backend install EXIT-trap regression passed')
