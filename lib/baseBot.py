# system imports
import time
import inspect
import importlib
import sys
import json
import yaml

# twisted imports
from twisted.words.protocols import irc
from twisted.internet import protocol, reactor

# custom imports
from lib.classes import *


class baseBot(irc.IRCClient):
    """A basic bot"""

    def __init__(self, *args, **kwargs):
        self.channels = None
        self.nickname = None
        self.password = None
        self.heatmap = None
        self.logger = None
        self.cmdQueue = []
        self.commands = {}
        self.modules = []
        self.vars = {}
        
    def saveVars(self):
        if not os.path.isdir('vars/'):
            os.makedirs('vars/')
        with open('vars/'+self.nickname+'.json', "w") as f:
            json.dump(self.vars,f)
    
    def loadVars(self):
        if os.path.exists('vars/'+self.nickname+'.json'):
            with open('vars/'+self.nickname+'.json', "r") as f:
                self.vars = yaml.safe_load(f)
            return True
        else:
            return False

    def noticed(self, user, channel, msg):
        user = user.split('!', 1)[0]
        if user == "NickServ" and "ACC" in msg:
            acc = msg.lower().split()
            for cmd in self.cmdQueue:
                try:
                    if acc[0] == cmd['user']:
                        if acc[2] == "3":
                            if cmd['cmd'] in self.commands:
                                if cmd['type'] == 'admin':
                                    if cmd['user'] in self.vars['admins']:
                                        self.commands[cmd['cmd']][0](self, cmd)
                                else:
                                    self.commands[cmd['cmd']][0](self, cmd)
                                self.cmdQueue.remove(cmd)
                except Exception as e:
                    self.msg(cmd['chan'], cmd['nick'] + ', something went wrong.')
                    self.logger.log("error", self.nickname+": Error in authed command:" + str(cmd) + ':' + str(e))
                    self.cmdQueue.remove(cmd)

    def loadModule(self, module):
        if 'modules.' + module in sys.modules.keys():
            self.logger.log("Error", "Module " + module + " already loaded.")
            return False
                  
        commands = getattr(importlib.import_module('modules.' + module), 'commands')
        getattr(sys.modules['modules.' + module], 'init')(self)
        
        for cmd in commands:
            self.commands[cmd] = commands[cmd]
                
        if module not in self.modules:
            self.modules.append(module)
            
        return True   

    def unloadModule(self, module):
        if 'modules.' + module in sys.modules.keys():
            commands = getattr(sys.modules['modules.' + module], 'commands')
            getattr(sys.modules['modules.' + module], 'stop')(self)
            for cmd in commands:
                if cmd in self.commands:
                    del self.commands[cmd]
            del sys.modules['modules.' + module]
            if module in self.modules:
                self.modules.remove(module)
            return True
        else:
            return False           

    def connectionMade(self):
        irc.IRCClient.connectionMade(self)
        time.sleep(1)
        self.msg("NickServ", "identify " + self.password)
        for mod in self.modules:
            self.loadModule(mod)

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)
        self.logger.log('error', 'Connection lost:'+str(reason))

    def signedOn(self):
        for channel in self.channels:
            self.join(channel)

    def privmsg(self, user, channel, msg):
    
# do any preprocessing before commands
        user = user.split('!', 1)
        nick = user[0]
        host = user[1].split('@')[1]
        user = user[0].lower()
        command = msg.split()[0].strip('.')
        
        if user in self.vars['ignore']:
            return

        if channel == self.nickname:
            chan = nick
        else:
            chan = channel

        if not msg.startswith("."):
            if channel == self.nickname:
                msg = "." + str(msg)
            else:
                return

# spam block
        if msg.startswith("."):

            if host in self.heatmap and self.heatmap[host] > 10:
                if self.heatmap[host] > 20:
                    self.heatmap[host] = 20
                    return
                self.msg(user, "Please wait " + str(30 * (self.heatmap[host] - 9)) + " seconds to send commands.")
                self.heatmap[host] += 1
                return

# run commands

        if command in self.commands:
            try:
                cType = self.commands[command][2]
                cmd = {}
                cmd['user'] = user
                cmd['args'] = msg.split()
                cmd['chan'] = chan
                cmd['host'] = host
                cmd['nick'] = nick
                cmd['type'] = cType
                cmd['cmd'] = command
                self.logger.log('cmd', self.nickname+':'+chan+':'+nick+':'+msg)
                if cType == 'admin' or cType == 'authed':
                    self.cmdQueue.append(cmd)
                    self.msg("NickServ", "acc " + user)
                    return
                else:
                    self.commands[command][0](self, cmd)
            except Exception as e:
                self.msg(chan, nick + ', something went wrong.')
                self.logger.log('error', self.nickname+':'+nick+':Error running command:'+msg+':'+str(e))


class baseBotFactory(protocol.ClientFactory):

    def __init__(self, b, masterLogger, botList):
        self.channels = b['channels']
        self.nickname = b['nick']
        self.password = b['password']
        self.admins = b['admins']
        self.heatmap = b['heatmap']
        self.modules = b['modules']
        self.ignore = b['ignore']
        self.logger = masterLogger
        self.botList = botList
        
    def buildProtocol(self, addr):
        p = baseBot()
        p.factory = self
        p.channels = self.channels
        p.nickname = self.nickname
        p.password = self.password
        p.logger = self.logger
        p.heatmap = self.heatmap
        p.modules = self.modules
        p.lineRate = 0.5
        p.reactor = reactor
        p.botList = self.botList
        
        if p.loadVars():
            for entry in self.admins:
                if entry not in p.vars['admins']:
                    p.vars['admins'].append(entry)
        
            for entry in self.ignore:
                if entry not in p.vars['ignore']:
                    p.vars['ignore'].append(entry)
        else:
            p.vars['admins'] = self.admins
            p.vars['ignore'] = self.ignore
                    
        self.botList.append(p)
        return p

    def clientConnectionLost(self, connector, reason):
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "Could not connect to irc", reason
        reactor.stop()
