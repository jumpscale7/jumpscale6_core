from JumpScale import j
# import JumpScale.grid.serverbase
from .TLOG import TLOG

j.base.loader.makeAvailable(j, 'db')
j.db.tlog = TLOG()
