from pylibftdi import BitBangDevice

relay_on_cmds=[0x01,0x02,0x04,0x08]
relay_off_cmds=[0xFE,0xFD,0xFB,0xF7]

def relay_on(rel_num, bbobj):
    bbobj.port |= relay_on_cmds[rel_num - 1]

def relay_off(rel_num, bbobj):
    bbobj.port &= relay_off_cmds[rel_num - 1]
