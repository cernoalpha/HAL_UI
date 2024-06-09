from pylibftdi import BitBangDevice



relay_on_cmds=[0x01,0x02,0x04,0x08]
relay_off_cmds=[0xFE,0xFD,0xFB,0xF7]


#to turn on the realy
#rel_num-->relay index (1 to 4)

def relay_on(rel_num,bbobj):
    global relay_on_cmds
    bbobj.port |= relay_on_cmds[rel_num-1]


#to turn off the realy
#rel_num-->relay index (1 to 4)    
    
def relay_off(rel_num,bbobj):
    global relay_off_cmds
    bbobj.port &= relay_off_cmds[rel_num-1]


#specify the device id 

#you can get the FT245RL device id using pylibftdi librery in the Terminal


bb=BitBangDevice('AC00LH65')
bb.direction = 0x0F

#to on the realay

relay_on(1,bb)
relay_on(2,bb)
relay_on(3,bb)
relay_off(4,bb)




