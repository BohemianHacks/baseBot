import urllib2
import urllib
import yaml

commands = {}
baseUrl = 'https://shapeshift.io/'


#runs before loading commands
def init(bot):
    print "Loading shapeshift.io..."

#runs before unloading commands
def stop(bot):
    print "Unloading shapeshift.io..."
 
def post(url, vals):
    req = urllib2.Request(url, urllib.urlencode(vals))
    return yaml.safe_load(urllib2.urlopen(req).read())

def get(url):
    return yaml.safe_load(urllib2.urlopen(url).read())

def getCoins(bot, cmd):
    args = cmd['args']
    chan = cmd['chan']
    user = cmd['user']
    nick = cmd['nick']
    url = baseUrl + 'getcoins'
    
    data = get(url)
    coins = data.keys()[0]
    for key in data.keys():
        coins = coins + ', ' + key
    bot.msg(user, "Valid coins: " + coins)
    bot.addHeat(cmd['host'], 1)
commands['getcoins'] = (getCoins, '.getcoins | List valid shapeshift.io coin symbols', 'public')

def info(bot, cmd):
    args = cmd['args']
    chan = cmd['chan']
    user = cmd['user']
    nick = cmd['nick']
    url = baseUrl + 'marketinfo/'
    
    coins = yaml.safe_load(urllib2.urlopen(baseUrl+'getcoins').read())
    if len(args) >= 3 and args[1].upper() in coins and args[2].upper() in coins:
        pair = args[1] + '_' + args[2]
        data = get(url+pair)
        res = data['pair'].upper().replace('_','->') + ' Rate:'
        res = res + '%.8f' % data['rate'] + ' Min:%.8f' % data['minimum'] + ' Max:%.8f' % data['limit']
        res = res + ' TX Fee:%.8f' % data['minerFee']
        bot.msg(chan, res)
        bot.addHeat(cmd['host'], 1)

commands['mkinfo'] = (info, '.mkinfo <from coin> <to coin> | Get market info for coin pair on shapeshift.io', 'authed')

def status(bot, cmd):
    args = cmd['args']
    chan = cmd['chan']
    user = cmd['user']
    nick = cmd['nick']
    url = baseUrl + 'txStat/'
    key = 'shapeshift_'+user
    
    if len(args) >= 2:
        url = url + args[1]
    elif key in bot.vars:
        url = url + bot.vars[key][0]
    else:
        bot.msg(chan, nick + ':' + 'no recent transactions, please include address')
        return
        
    data = get(url)
    if data['status'] == 'complete':
        bot.msg(chan, nick + ' Done, trxID: ' + data['transaction'])
        bot.addHeat(cmd['host'], 1)
    elif data['status'] == 'no_deposits':
        bot.msg(chan, nick + ', no deposits yet.')
        bot.addHeat(cmd['host'], 1)
    elif data['status'] == 'recieved':
        bot.msg(chan, nick + ", coins recieved but still processing.")
        bot.addHeat(cmd['host'], 1)
    elif data['status'] == 'failed':
        bot.msg(user, nick + ' Failed: ' + data['error'])
        bot.addHeat(cmd['host'], 1)
        
    
commands['txstat'] = (status, '.txstat (deposit address) | Check status of shapeshift.io deposit', 'authed')
      
def shift(bot, cmd):
    args = cmd['args']
    chan = cmd['chan']
    user = cmd['user']
    nick = cmd['nick']
    url = baseUrl + 'shift'
    
    #check for valid coin symbols
    coins = yaml.safe_load(urllib2.urlopen(baseUrl+'getcoins').read())
    if args[1].upper() in coins and args[2].upper() in coins:
        
        #load values for post request
        pair = args[1]+'_'+args[2]
        vals = {
        'withdrawal':args[3],
        'pair':pair
        }
        if len(args) >= 5:
            vals['returnAddress'] = args[4]
        
        data = post(url, vals)
        if 'deposit' in data:
            key = 'shapeshift_'+user
            if key in bot.vars:
                bot.vars[key].insert(0,data['deposit'])
                if len(bot.vars[key]) > 10:
                    bot.vars[key].pop()
            else:
                bot.vars[key] = [data['deposit']]
        
            bot.msg(chan, nick + ': '+data['deposit'])
            bot.addHeat(cmd['host'], 1)
        else:
            bot.msg(chan, nick + 'Error, please try again later')
            bot.addHeat(cmd['host'], 1)
    
    else:
        bot.msg(chan, nick + 'Invalid coin symbol.')
        bot.addHeat(cmd['host'], 1)
          
commands['shift'] = (shift, '.shift <from coin> <to coin> <withdraw address> (return address) | shapeshift.io exchange', 'authed')
