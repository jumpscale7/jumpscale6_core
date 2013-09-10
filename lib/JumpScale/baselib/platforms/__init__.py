from JumpScale import j
j.base.loader.makeAvailable(j, 'system.platform')
platformid = None
try:
    import lsb_release
    platformid = lsb_release.get_distro_information()['ID']
except ImportError:
    exitcode, platformid = j.system.process.execute('lsb_release -i -s', False)
    platformid = platformid.strip()

if platformid in ('Ubuntu', 'LinuxMint'):
    from .ubuntu.Ubuntu import Ubuntu
    ubuntu = Ubuntu()
    j.system.platform.ubuntu = Ubuntu()

