import os
commands = {}

#runs before loading commands
def init(bot):
    print "Loading basic commands..."

#runs before unloading commands
def stop(bot):
    print "Unloading basic commands..."
    
def msg(bot, cmd):
    args = cmd['args']
    msg = args[2]
    for ii in range(len(args)-3):
        msg = msg + ' ' + args[ii+3]
    bot.msg(args[1], msg)
    bot.addHeat(cmd['host'], 1)
    
commands['msg'] = (msg, '.msg <nick/channel> <message>', 'admin')

def listMods(bot, cmd):
    nick = cmd['user']
    bot.msg(nick, "Available Modules:")
    for mod in os.listdir('modules'):
        if '__' not in mod and mod.endswith('.py'):
            if mod.strip('.py') in bot.modules:
                bot.msg(nick, '[*]'+mod.strip('.py'))
                bot.addHeat(cmd['host'], 1)
            else:
                bot.msg(nick, '[ ]'+mod.strip('.py'))
                bot.addHeat(cmd['host'], 1)
                
commands['list'] = (listMods, '.list', 'public')        

def get(bot, cmd):
    args = cmd['args']
    if args[1] in bot.stores:
        bot.msg(cmd['chan'], str(bot.stores[args[1]]))
        bot.addHeat(cmd['host'], 1)
    else:
        bot.msg(cmd['chan'], "Variable '"+args[1]+"' not found.")
        bot.addHeat(cmd['host'], 1)
        
commands['get'] = (get, '.get <variable>', 'admin')

def setVar(bot, cmd):
    args = cmd['args']
    val = None
    if args[1] in bot.stores:
        if len(args) > 2:
            if type(bot.stores[args[1]]) == type([]) and '|' not in args[2] and '#' not in args[2]:
                bot.stores[args[1]].append(args[2])
                bot.msg(cmd['chan'], "Value added.")
                bot.addHeat(cmd['host'], 1)
                return
            
    if len(args) > 2:
        if '|' in args[2]:
            val = args[2].split('|')
        elif '#' in args[2]:
            val = float(args[2].strip('#'))
        else:
            val = args[2]
            for ii in range(len(args)-3):
                val = val + ' ' + args[ii+3]
        bot.stores[args[1]] = val
        bot.msg(cmd['chan'], "Value set.")
        bot.addHeat(cmd['host'], 1)
    else:
        del bot.stores[args[1]]
        bot.msg(cmd['chan'], "Value erased.")
        bot.addHeat(cmd['host'], 1)
        
commands['set'] = (setVar, '.set <variable> <value>', 'admin')

def join(bot, cmd):
    args = cmd['args']
    bot.join(args[1])

commands['join'] = (join, '.join <channel>', 'admin')

def leave(bot, cmd):
    args = cmd['args']
    bot.leave(args[1])

commands['leave'] = (leave, '.leave <channel>', 'admin')

def reloadMod(bot, cmd):
    args = cmd['args']
    chan = cmd['chan']
    if bot.unloadModule(args[1]) and bot.loadModule(args[1]):
        bot.msg(chan, 'reloaded: ' + args[1])
        bot.addHeat(cmd['host'], 1)
    else:
        bot.msg(chan, "Could not reload '"+args[1]+"'.")
        bot.addHeat(cmd['host'], 1)
        
commands['reload'] = (reloadMod, '.reload <module>', 'admin')        

def shutdown(bot, cmd):
    chan = cmd['chan']
    for b in bot.botList:
        b.saveVars()
    if b.logger.write():
        b.reactor.stop()

commands['shutdown'] = (shutdown, '.shutdown', 'admin')
        
def load(bot, cmd):
    args = cmd['args']
    chan = cmd['chan']
    if bot.loadModule(args[1]):
        bot.msg(chan, 'loaded: ' + args[1])
        bot.addHeat(cmd['host'], 1)
    else:
        bot.msg(chan, "Could not load '"+args[1]+"'.")
        bot.addHeat(cmd['host'], 1)

commands['load'] = (load, '.load <module>', 'admin')        
        
def unload(bot, cmd):
    args = cmd['args']
    if bot.unloadModule(args[1]):
        bot.msg(cmd['chan'], "unloaded: " + args[1])
        bot.addHeat(cmd['host'], 1)
    else:
        bot.msg(cmd['chan'], "Module '" + args[1] + "' not found.")
        bot.addHeat(cmd['host'], 1)
                 
commands['unload'] = (unload, '.unload <module>', 'admin')
        
def help(bot, cmd):
    args = cmd['args']
    user = cmd['user']
    if len(args) > 1:
        if args[1] in bot.commands:
            bot.msg(cmd['chan'], bot.commands[args[1]][1])
            bot.addHeat(cmd['host'], 1)
    else:
        commandList = ''
        for c in bot.commands:
            if bot.commands[c][2] == 'admin':
                if user in bot.stores['admins']:
                    commandList = commandList + ' ' + bot.commands[c][1]
            else:
                commandList = commandList + ' ' + bot.commands[c][1]
                bot.msg(user, c + ': ' + bot.commands[c][1])
        bot.msg(user, "Commands:" + commandList)
        bot.addHeat(cmd['host'], 1)
                
commands['help'] = (help, ".help <command>", 'public')
