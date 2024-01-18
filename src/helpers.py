import builtins
import json
import time

client = builtins.client

savedLogs = []
firstLog = False
def logf(str, args = None):
    if (not firstLog):
        with open("log.txt", "w") as f:
            f.write("---- New Log Session ----\n")
            f.close()
    msg = ""
    t = f"[{time.strftime('%H:%M:%S')}] "
    if (args == "e"):
        msg = f"{t}[ERROR] {str}"
    elif (args == "w"):
        msg = f"{t}[WARNING] {str}"
    elif (args == "i"):
        msg = f"{t}[INFO] {str}"
    elif (args == "d"):
        msg = f"{t}[DEBUG] {str}"
    else:
        msg = f"{t}[INFO] {str}"

    print(msg)
    savedLogs.append(msg)

def formatTime(seconds, internal=False):
    if internal:
            hours = int(seconds // 3600)
            seconds -= hours * 3600
            minutes = int(seconds // 60)
            seconds -= minutes * 60
            return [hours, minutes, seconds]
    hours = int(seconds // 3600)
    seconds -= hours * 3600
    minutes = int(seconds // 60)
    seconds -= minutes * 60
    return f"{hours} hours, {minutes} minutes, {seconds} seconds"


async def dmUser(id, message, embed=False):
    user = client.get_user(id)
    if embed:
        await user.send(embed=message)
    else:
        await user.send(message)


