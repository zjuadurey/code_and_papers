import json
import mmap
import os
from pathlib import Path
import platform
import shutil
import subprocess
import tempfile
from .benchmark_config import bench_dir

def command(args):
    try:
        p=subprocess.run(args,capture_output=True,text=True,timeout=30)
        return dict(command=args,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr)
    except Exception as e: return dict(command=args,error=str(e))

def powershell_json(code):
    exe=shutil.which('powershell.exe')
    if not exe:return None
    r=command([exe,'-NoProfile','-Command',code])
    try:return json.loads(r['stdout'].lstrip('\ufeff'))
    except (KeyError,ValueError):return None

def host_volume():
    distros=powershell_json('Get-ChildItem HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Lxss | Get-ItemProperty | Select-Object DistributionName,BasePath | ConvertTo-Json')
    if isinstance(distros,dict):distros=[distros]
    chosen=[x for x in distros or [] if x['DistributionName']==os.environ.get('WSL_DISTRO_NAME')]
    if not chosen and len(distros or [])==1: chosen=distros
    if not chosen:return None
    import re
    match=re.search(r'([A-Za-z]):',chosen[0]['BasePath'])
    if not match:return None
    letter=match.group(1).upper()
    volumes=powershell_json('Get-Volume | Select-Object DriveLetter,FileSystem,SizeRemaining,Size | ConvertTo-Json')
    if isinstance(volumes,dict):volumes=[volumes]
    for v in volumes or []:
        if v['DriveLetter']==letter:return dict(**v,distribution=chosen[0]['DistributionName'],base_path=chosen[0]['BasePath'])
    return None

def host_free(letter):
    if not letter:return None
    if len(letter)!=1 or not letter.isalpha():raise ValueError('Invalid host drive letter')
    v=powershell_json(f'Get-Volume -DriveLetter {letter} | Select-Object SizeRemaining | ConvertTo-Json')
    return int(v['SizeRemaining']) if v else None

def direct_probe(directory):
    created,path=tempfile.mkstemp(prefix='qthin-direct-probe-',dir=directory)
    os.close(created);path=Path(path)
    fd=None
    try:
        fd=os.open(path,os.O_RDWR|os.O_DIRECT|os.O_NOFOLLOW)
        with mmap.mmap(-1,4096) as buffer:
            buffer[:]=bytes([0x5a])*4096
            assert os.pwrite(fd,buffer,0)==4096
            os.fdatasync(fd)
            buffer[:]=bytes(4096)
            assert os.preadv(fd,[buffer],0)==4096 and buffer[4095]==0x5a
        return dict(supported=True,alignment=4096,reason=None)
    except Exception as e:return dict(supported=False,alignment=4096,reason=str(e))
    finally:
        if fd is not None:os.close(fd)
        path.unlink(missing_ok=True)

def probe():
    directory=bench_dir()
    commands=[['uname','-a'],['cat','/proc/version'],['lsblk','-o','NAME,TYPE,SIZE,ROTA,FSTYPE,MOUNTPOINTS,MODEL'],
              ['findmnt'],['df','-h'],['df','-T'],['findmnt','-T',str(directory),'-J'],['stat','-f',str(directory)],
              ['df','-B1',str(directory)],['lscpu']]
    records=[command(c) for c in commands]
    mount=json.loads(records[6]['stdout'])['filesystems'][0]
    iswsl='microsoft' in platform.release().lower()
    fstype=mount['fstype']
    kind='wsl2_drvfs' if iswsl and fstype in {'9p','drvfs'} else 'wsl2_ext4_vhdx' if iswsl and fstype=='ext4' else 'unknown'
    if not iswsl:
        v=command(['systemd-detect-virt'])
        kind='native_linux' if v.get('stdout','').strip()=='none' else 'virtual_machine' if v.get('returncode')==0 else 'unknown'
    dev=Path(mount['source']).name if mount['source'].startswith('/dev/') else None
    stat_path=Path('/sys/class/block')/dev/'stat' if dev else None
    def read(path):
        try:return path.read_text().strip()
        except OSError:return None
    sv=os.statvfs(directory)
    return dict(benchmark_directory=str(directory),storage_environment_class=kind,filesystem=fstype,
        mount_point=mount['target'],mount_source=mount['source'],mount_options=mount.get('options'),
        free_bytes_before_run=sv.f_bavail*sv.f_frsize,block_size=sv.f_bsize,
        device=dev,device_stat_path=str(stat_path) if stat_path and stat_path.is_file() else None,
        device_counter_scope='guest-visible shared block-device' if iswsl else 'shared block-device',
        device_counter_unavailable_reason=None if stat_path and stat_path.is_file() else 'No readable mapped block device',
        device_model=read(Path('/sys/class/block')/dev/'device/model') if dev else None,
        rotational_flag=read(Path('/sys/class/block')/dev/'queue/rotational') if dev else None,
        direct_io=direct_probe(directory),host_volume=host_volume() if kind=='wsl2_ext4_vhdx' else None,
        cpu_logical_count=os.cpu_count(),load_average=os.getloadavg(),kernel=platform.release(),commands=records)
