# system imports
import time
import json
import yaml

#third party imports
from twisted.internet import task, reactor

# custom imports
from lib import classes, baseBot

# load initial variables from config
with open('config.json', "r") as f:
    config = yaml.safe_load(f)
    
masterLogger = classes.logger(config['logLocation'])
botList = []

def sync():
    for b in botList:
        #save bot variables
        b.saveVars()
        #lower spam counts
        for host in b.heatmap:
            if heatmap[host] > 0:
                heatmap[host] -= 1
            if host in ignoreHosts and heatmap[host] < 9:
                ignoreHosts.pop(host)

    # write log to disk
    masterLogger.write()

l = task.LoopingCall(sync)
l.start(30.0)

for b in config['bots']:
    c = baseBot.baseBotFactory(b, masterLogger, botList)
    reactor.connectTCP(b['server'], b['port'], c) 
                 
reactor.run()
