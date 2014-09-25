
from JumpScale import j
j.base.loader.makeAvailable(j, 'tools')
from whmcsorders import whmcsorders
from whmcstickets import whmcstickets
from whmcsusers import whmcsusers

j.tools.orders = whmcsorders()
j.tools.tickets = whmcstickets()
j.tools.users = whmcsusers()
