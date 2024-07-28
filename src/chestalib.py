import discord
import asyncio, time, random, json
import builtins

dailyFuncs = []
hourlyFuncs = []
weeklyFuncs = []
monthlyFuncs = []

savedTimes = {
    "daily": 0,
    "hourly": 0,
    "weekly": 0,
    "monthly": 0
}

def OnDaily(func):
    dailyFuncs.append(func)
    return func

def OnHourly(func):
    hourlyFuncs.append(func)
    return func

def OnWeekly(func):
    weeklyFuncs.append(func)
    return func

def OnMonthly(func):
    monthlyFuncs.append(func)
    return func

def CheckTime():
    currentTime = time.time()
    if (currentTime - savedTimes["daily"] >= 86400):
        for func in dailyFuncs:
            func()
        savedTimes["daily"] = currentTime

    if (currentTime - savedTimes["hourly"] >= 3600):
        for func in hourlyFuncs:
            func()
        savedTimes["hourly"] = currentTime

    if (currentTime - savedTimes["weekly"] >= 604800):
        for func in weeklyFuncs:
            func()
        savedTimes["weekly"] = currentTime

    if (currentTime - savedTimes["monthly"] >= 2629743):
        for func in monthlyFuncs:
            func()
        savedTimes["monthly"] = currentTime


async def StartTimer():
    while True:
        CheckTime()
        await asyncio.sleep(5)

