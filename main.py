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
from multiprocessing import Pool
import os
import colorama
import asyncio
import aioconsole
import PySimpleGUI as sg
import sys

# Clear on launch incase there was something there in their terminal from before
os.system('cls' if os.name == 'nt' else 'clear')

os.system('color')
# SETTINGS
checkProxies = False
printWorkingProxies = False
printWorkingTokens = True


def isMain():
    if __name__ == "__main__":
        return True
    else:
        return False


def watermark(text):
    print(termcolor.colored(text, "blue"))


if isMain():
    watermark("___________      .__   ")
    watermark("\_   _____/______|__| ____   ____ ___  ___  ")
    watermark(" |    __) \_  __ \  |/  _ \ /    \\  \/  /")
    watermark(" |     \   |  | \/  (  <_> )   |  \>    <")
    watermark(" \___  /   |__|  |__|\____/|___|  /__/\_ \\")
    watermark("     \/                         \/      \/  ")
colorama.init()


def cprint(text, color):
    print(termcolor.colored(text, color))


def is_bad_proxy(pip):
    if checkProxies:
        try:
            proxy_handler = urllib.request.ProxyHandler({'socks4': pip})
            opener = urllib.request.build_opener(proxy_handler)
            opener.addheaders = [('User-agent', 'Mozilla/5.0')]
            urllib.request.install_opener(opener)
            # change the URL to test here
            req = urllib.request.Request('http://www.example.com')
            sock = urllib.request.urlopen(req)
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
    f = open(file)
    lines = f.readlines()
    return lines[line]


def openFileLines(fileName):
    with open(fileName) as f:
        return f.readlines()


if isMain():
    cprint("Checking proxies...", "blue")
proxies = openFileLines("proxies.txt")
workingProxies = []
i = 0
for i in range(0, len(proxies)):
    proxy = proxies[i]
    proxy = proxy.strip("\n")
    if is_bad_proxy(proxy):
        if isMain():
            cprint("Bad Proxy: " + proxy, "red")
    else:
        if isMain():
            if (printWorkingProxies):
                cprint("Successful Proxy: " + proxy, "blue")
        workingProxies.append(proxy)


def getRandomProxy():
    while (True):
        proxy = workingProxies[randomNumber(0, len(workingProxies) - 1)]
        if (is_bad_proxy(proxy) and checkProxies):
            continue
        else:
            return proxy


tokens = openFileLines("tokens.txt")
workingTokens = []
i = 0
if isMain():
    cprint("Checking tokens...", "blue")
for i in range(0, len(tokens)):
    proxy = getRandomProxy()
    token = tokens[i].strip("\n")
    proxy = proxy.split(":")
    proxy[1] = proxy[1].strip("\n")
    r = requests.delete("https://discord.com/api/v8/channels/765751969108328448/messages/ack",
                        proxies=dict(http='socks4://' + proxy[0] + ':' + proxy[1]), headers={'authorization': token})
    if r.status_code != 401 and r.status_code != 403:
        workingTokens.append(tokens[i].strip("\n"))
        if isMain():
            if printWorkingTokens:
                cprint("Successful Token: "+tokens[i].strip("\n"), "blue")
    i += 1
tokens = workingTokens
i = 0


def joinServer(token, invite):
    PostProxiedRequest(
        "https://discord.com/api/v8/invites/" + invite, token, False)
    cprint("Joined/Attempted to join with token: "+token, "blue")


def leaveServer(token, serverId):
    DeleteProxiedRequest(
        "https://discordapp.com/api/v8/users/@me/guilds/" + serverId, token, False)


def reactToMessage(channel, message, reaction, token):
    PostProxiedRequest("https://discord.com/api/v8/channels/"+channel +
                       "/messages/"+message+"/reactions/"+reaction+"/%40me", token, False)


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


async def sendMessage(channelId, token, message):
    data = {
        "content": message,
        "tts": "false"
    }
    PostProxiedRequest("https://discord.com/api/v8/channels/" +
                       channelId+"/messages", token, True, data)


def addFriend(username, discriminator, token):
    url = "https://discord.com/api/v8/users/@me/relationships"
    data = {
        "username": username,
        "discriminator": discriminator
    }
    PostProxiedRequest(url, token, True, data)


def setStatus(status, token):
    data = {
        "custom_status": status
    }
    PostProxiedRequest(
        "https://discord.com/api/v8/users/@me/settings", token, True, data)


def addWithAllTokens(name):
    name = name.split("#")
    i = 0
    for i in range(0, len(tokens)):
        addFriend(name[0], name[1], tokens[i])
        i += 1


def setStatusAllTokens(status):
    i = 0
    for i in range(0, len(tokens)):
        setStatus(status, tokens[i])
        i += 1


def spamChannelWithAllTokens(channelId, Message):
    while True:
        i = 0
        for i in range(0, len(tokens)):
            asyncio.run(sendMessage(channelId, tokens[i], Message))
            i += 1


def getProxiedRequest(url, discordSecurityToken, doParams=False, linkParams=""):
    discordSecurityToken = discordSecurityToken.strip("\n")
    cookie = {'authorization': discordSecurityToken}
    proxy = getRandomProxy()
    proxy = proxy.split(":")
    proxy[1] = proxy[1].strip("\n")
    if doParams:
        return requests.get(url, proxies=dict(http='socks4://' + proxy[0] + ':' + proxy[1]), headers=cookie, data=linkParams).text
    else:
        return requests.get(url, proxies=dict(http='socks4://' + proxy[0] + ':' + proxy[1]), headers=cookie).text


def PostProxiedRequest(url, discordSecurityToken, doParams=False, linkParams=""):
    discordSecurityToken = discordSecurityToken.strip("\n")
    cookie = {'authorization': discordSecurityToken}
    proxy = getRandomProxy()
    proxy = proxy.split(":")
    proxy[1] = proxy[1].strip("\n")
    if doParams:
        r = requests.post(url, proxies=dict(
            http='socks4://' + proxy[0] + ':' + proxy[1]), headers=cookie, json=linkParams)
        if (r.status_code != 200):
            cprint("ERROR while POSTING with TOKEN: " +
                   discordSecurityToken+" STATUS CODE: "+str(r.status_code), "red")
            return "404"
        else:
            return r.text
    else:
        r = requests.post(url, proxies=dict(
            http='socks4://' + proxy[0] + ':' + proxy[1]), headers=cookie)
        if (r.status_code != 200):
            cprint("ERROR while POSTING with TOKEN: " +
                   discordSecurityToken+" STATUS CODE: "+str(r.status_code), "red")
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
        r = requests.delete(url, proxies=dict(
            http='socks4://' + proxy[0] + ':' + proxy[1]), headers=cookie, json=linkParams)
        if (r.status_code != 200):
            cprint("ERROR while POSTING with TOKEN: " +
                   discordSecurityToken+" STATUS CODE: "+str(r.status_code), "red")
            return "404"
        else:
            return r.text
    else:
        r = requests.delete(url, proxies=dict(
            http='socks4://' + proxy[0] + ':' + proxy[1]), headers=cookie)
        if (r.status_code != 200):
            cprint("ERROR while POSTING with TOKEN: " +
                   discordSecurityToken+" STATUS CODE: "+str(r.status_code), "red")
            return "404"
        else:
            return r.text


def cls():
    os.system('cls' if os.name == 'nt' else 'clear')


def reloadTokens():
    tokens = openFileLines("tokens.txt")
    workingTokens = []
    i = 0
    cprint("Checking tokens...", "blue")
    for i in range(0, len(tokens)):
        proxy = getRandomProxy()
        token = tokens[i].strip("\n")
        proxy = proxy.split(":")
        proxy[1] = proxy[1].strip("\n")
        r = requests.delete("https://discord.com/api/v8/channels/765751969108328448/messages/ack",
                            proxies=dict(http='socks4://' + proxy[0] + ':' + proxy[1]), headers={'authorization': token})
        if r.status_code != 401 and r.status_code != 403:
            workingTokens.append(tokens[i].strip("\n"))
            if printWorkingTokens:
                cprint("Successful Token: "+tokens[i].strip("\n"), "blue")
        i += 1
    cprint("Done.", "green")
    tokens = workingTokens


def reloadProxies():
    cprint("Checking proxies...", "blue")
    proxies = openFileLines("proxies.txt")
    workingProxies = []
    i = 0
    for i in range(0, len(proxies)):
        proxy = proxies[i]
        proxy = proxy.strip("\n")
        if is_bad_proxy(proxy):
            cprint("Bad Proxy: " + proxy, "red")
        else:
            if (printWorkingProxies):
                cprint("Successful Proxy: " + proxy, "blue")
            workingProxies.append(proxy)
    cprint("Done.", "green")


def restart():
    cprint("Restarting...", "red")
    time.sleep(1)
    cls()
    os.system('python main.py')


def showHelp():
    cprint("-$ join [serverInviteCode] | Joins a server", "red")
    cprint(
        "-$ spam channel [channelId] [message] (ARGS POSSIBLE) | Spams a channel in a server with a message", "red")
    cprint(
        "-$ leave [serverId] | Leaves a specific server on all clients", "red")
    cprint("-$ add [username] -- (Example: discord#0001) | Adds a discord user with all tokens (HIGH TOKEN BAN CHANCE)", "red")
    cprint(
        "-$ status [status] | Sets status of all clients (Unknown Token Ban Rate)", "red")
    cprint("-$ help | Shows commands", "red")
    cprint("-$ reloadtokens | reloads all tokens from file", "red")
    cprint("-$ reloadproxies | reloads all proxies from file", "red")
    cprint("-$ restart | restarts program", "red")


def start():
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
            pool = Pool(processes=1)
            result = pool.apply_async(
                spamChannelWithAllTokens, [channelId, text])
            input(termcolor.colored("Press enter to stop", "red"))
            pool.terminate()
        elif (includes(command, "leave")):
            serverId = command.strip("leave ")
            cprint("LEAVING: " + serverId, "blue")
            leaveWithAllTokens(serverId)
        elif (includes(command, "help")):
            showHelp()
        elif (includes(command, "reloadtokens")):
            reloadTokens()
        elif (includes(command, "reloadproxies")):
            reloadProxies()
        elif (includes(command, "add")):
            args = command.strip("add ")
            cprint("Spam-Adding User: " + args, "blue")
            pool = Pool(processes=1)
            result = pool.apply_async(
                addWithAllTokens, [args])
            input(termcolor.colored("Press enter to stop", "red"))
            pool.terminate()
        elif (includes(command, "status")):
            args = command.strip("status ")
            cprint("Setting status: " + args, "blue")
            pool = Pool(processes=1)
            result = pool.apply_async(
                setStatusAllTokens, [args])
            input(termcolor.colored("Press enter to stop", "red"))
            pool.terminate()
        elif (includes(command, "restart")):
            restart()
            break
        elif (includes(command, "clear")):
            cls()
        else:
            cprint("Command did not work, type help to see commands.", "red")


if isMain():
    start()
