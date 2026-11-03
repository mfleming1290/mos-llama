import os, subprocess, tempfile, pathlib, json
script = pathlib.Path('llama_backend').resolve()
with tempfile.TemporaryDirectory() as d:
    root=pathlib.Path(d)
    settings=root/'settings.json'
    settings.write_text(json.dumps({'install_path':'/mnt/home/appdata/llama'}))
    env={**os.environ,'MOS_LLAMA_SETTINGS':str(settings)}
    result=subprocess.run(['bash',str(script),'status'],env=env,capture_output=True,text=True)
    assert result.returncode == 0, result.stderr
    data=json.loads(result.stdout)
    assert not data['installed'] and data['backend']=='' and data['binary'].endswith('/runtime/bin/llama')
    settings.write_text(json.dumps({'install_path':'/tmp/notpersistent'}))
    result=subprocess.run(['bash',str(script),'status'],env=env,capture_output=True,text=True)
    assert result.returncode != 0 and 'persistent' in result.stderr
    settings.write_text(json.dumps({'install_path':'/mnt/home/../etc'}))
    result=subprocess.run(['bash',str(script),'status'],env=env,capture_output=True,text=True)
    assert result.returncode != 0
print('backend status/path tests passed')
