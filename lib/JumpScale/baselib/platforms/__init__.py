from OpenWizzy import o
o.base.loader.makeAvailable(o, 'system.platform')
platformid = None
try:
    import lsb_release
    platformid = lsb_release.get_distro_information()['ID']
except ImportError:
    exitcode, platformid = o.system.process.execute('lsb_release -i -s', False)
    platformid = platformid.strip()

if platformid in ('Ubuntu', 'LinuxMint'):
    from .ubuntu.Ubuntu import Ubuntu
    o.system.platform.ubuntu=Ubuntu()

