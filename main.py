import random
import requests
import json
import threading
import time
import urllib.request
import socket
import urllib.error
import termcolor
import json
import multiprocessing as mp
import os

checkProxies = False

def cprint(text, color):
    print(termcolor.colored(text, color))

def is_bad_proxy(pip):
    if checkProxies: 
        try:
            proxy_handler = urllib.request.ProxyHandler({'socks4': pip})
            opener = urllib.request.build_opener(proxy_handler)
            opener.addheaders = [('User-agent', 'Mozilla/5.0')]
            urllib.request.install_opener(opener)
            req=urllib.request.Request('http://www.example.com')  # change the URL to test here
            sock=urllib.request.urlopen(req)
        except urllib.error.HTTPError as e:
            return True
        except Exception as detail:
            return True
        return False
    else:
        return False
def randomNumber(low, high):
    return random.randint(low, high)
def getLines(file):
    with open(file) as f:
        return sum(1 for _ in f)
def readLine(file, line):
    f=open(file)
    lines=f.readlines()
    return lines[line]
def openFileLines(fileName):
    with open(fileName) as f:
        return f.readlines()
def getRandomProxy():
    while (True):
        proxy = readLine("proxies.txt", randomNumber(0, getLines("proxies.txt") - 1))
        if (is_bad_proxy(proxy)):
            continue
        else:
            return proxy
tokens = openFileLines("tokens.txt")
workingTokens = []
i = 0
cprint("Checking tokens...", "blue")
for i in range(0, len(tokens)):
    proxy = getRandomProxy()
    token = tokens[i].strip("\n")
    proxy = proxy.split(":")
    proxy[1] = proxy[1].strip("\n")
    r = requests.delete("https://discord.com/api/v8/channels/765751969108328448/messages/ack", proxies=dict(http='socks4://' + proxy[0] + ':' + proxy[1]), headers={'authorization': token})
    if r.status_code != 401 and r.status_code != 403:
        workingTokens.append(tokens[i].strip("\n"))
        cprint("Successful Token: "+tokens[i].strip("\n"), "blue")
    i += 1
tokens = workingTokens
def joinServer(token, invite):
    PostProxiedRequest("https://discord.com/api/v8/invites/" + invite, token, False)
    cprint("Joined/Attempted to join with token: "+token, "blue")
def leaveServer(token, serverId):
    DeleteProxiedRequest("https://discordapp.com/api/v8/users/@me/guilds/"+serverId, token, False)
def includes(string, substring):
    if string.find(substring) != -1:
        return True
    else:
        return False
def joinWithAllTokens(invite):
    i = 0
    for i in range(0, len(tokens)):
        joinServer(tokens[i], invite)
        i += 1
def leaveWithAllTokens(id):
    i = 0
    for i in range(0, len(tokens)):
        leaveServer(tokens[i], id)
        i += 1
def sendMessage(channelId, token, message):
    data = {
        "content": message,
        "tts": "false"
    }
    PostProxiedRequest("https://discord.com/api/v8/channels/"+channelId+"/messages", token, True, data)
def spamChannelWithAllTokens(channelId, Message):
    while True:
        i = 0
        for i in range(0, len(tokens)):
            sendMessage(channelId, tokens[i], Message)
            i += 1
def getProxiedRequest(url, discordSecurityToken, doParams=False, linkParams=""):
    discordSecurityToken = discordSecurityToken.strip("\n")
    cookie = {'authorization': discordSecurityToken}
    proxy = getRandomProxy()
    proxy = proxy.split(":")
    proxy[1] = proxy[1].strip("\n")
    if doParams:
        return requests.get(url, proxies=dict(http='socks4://' + proxy[0] + ':' + proxy[1]), hreaders=cookie, data=linkParams).text
    else:
        return requests.get(url, proxies=dict(http='socks4://' + proxy[0] + ':' + proxy[1]), headers=cookie).text
def PostProxiedRequest(url, discordSecurityToken, doParams=False, linkParams=""):
    discordSecurityToken = discordSecurityToken.strip("\n")
    cookie = {'authorization': discordSecurityToken}
    proxy = getRandomProxy()
    proxy = proxy.split(":")
    proxy[1] = proxy[1].strip("\n")
    if doParams:
        r = requests.post(url, proxies=dict(http='socks4://' + proxy[0] + ':' + proxy[1]), headers=cookie, json=linkParams)
        if (r.status_code != 200):
            cprint("ERROR while POSTING with TOKEN: " + discordSecurityToken+" STATUS CODE: "+str(r.status_code), "red")
            return "404"
        else:
            return r.text
    else:
        r = requests.post(url, proxies=dict(http='socks4://' + proxy[0] + ':' + proxy[1]), headers=cookie)
        if (r.status_code != 200):
            cprint("ERROR while POSTING with TOKEN: " + discordSecurityToken+" STATUS CODE: "+str(r.status_code), "red")
            return "404"
        else:
            return r.text
def DeleteProxiedRequest(url, discordSecurityToken, doParams=False, linkParams=""):
    discordSecurityToken = discordSecurityToken.strip("\n")
    cookie = {'authorization': discordSecurityToken}
    proxy = getRandomProxy()
    proxy = proxy.split(":")
    proxy[1] = proxy[1].strip("\n")
    if doParams:
        r = requests.delete(url, proxies=dict(http='socks4://' + proxy[0] + ':' + proxy[1]), headers=cookie, json=linkParams)
        if (r.status_code != 200):
            cprint("ERROR while POSTING with TOKEN: " + discordSecurityToken+" STATUS CODE: "+str(r.status_code), "red")
            return "404"
        else:
            return r.text
    else:
        r = requests.delete(url, proxies=dict(http='socks4://' + proxy[0] + ':' + proxy[1]), headers=cookie)
        if (r.status_code != 200):
            cprint("ERROR while POSTING with TOKEN: " + discordSecurityToken+" STATUS CODE: "+str(r.status_code), "red")
            return "404"
        else:
            return r.text

while (True):
    command = input(termcolor.colored("Type a command -$ ", "green"))
    if (includes(command, "join")):
        serverInvite = command.strip("join ")
        cprint("JOINING: " + serverInvite, "blue")
        joinWithAllTokens(serverInvite)
    elif (includes(command, "spam channel")):
        args = command.strip("spam channel ")
        args = args.split(' ')
        channelId = args[0]
        text = ' '.join(args[1:])
        cprint("Spamming Channel: " + channelId, "blue")
        spamThread = mp.Process(target=spamChannelWithAllTokens, args=(channelId, text))
        spamThread.run()
        input(termcolor.colored("Press enter to stop", "red"))
        spamThread.terminate()
        spamThread.kill()
    elif (includes(command, "leave")):
        serverId = command.strip("leave ")
        cprint("LEAVING: " + serverId, "blue")
        leaveWithAllTokens(serverId)