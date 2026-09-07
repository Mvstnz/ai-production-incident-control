"""Install the verified official RTK Linux release on an ephemeral GitHub runner."""
import hashlib,io,os,platform,tarfile
from pathlib import Path
from urllib.request import urlopen
assert os.getenv('GITHUB_ACTIONS')=='true' and platform.system()=='Linux' and platform.machine()=='x86_64'
url='https://github.com/rtk-ai/rtk/releases/download/v0.43.0/rtk-x86_64-unknown-linux-musl.tar.gz'
expected='ff8a1e7766496e175291a85aeca1dc97c9ff6df33e51e5893d1fbc78fea2a609'
with urlopen(url,timeout=90) as response:data=response.read()
assert hashlib.sha256(data).hexdigest()==expected,'Official RTK release digest mismatch'
with tarfile.open(fileobj=io.BytesIO(data),mode='r:gz') as archive:
    members=[m for m in archive.getmembers() if m.isfile() and Path(m.name).name=='rtk']
    assert len(members)==1,'Unexpected RTK archive layout'
    binary=archive.extractfile(members[0]).read()
directory=Path.home()/'.local/bin';directory.mkdir(parents=True,exist_ok=True)
path=directory/'rtk';path.write_bytes(binary);path.chmod(0o755)
with open(os.environ['GITHUB_PATH'],'a') as handle:handle.write(str(directory)+'\n')
print('Official RTK v0.43.0 binary installed after SHA-256 verification.')
