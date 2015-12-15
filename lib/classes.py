import time
import os

class logger:

    def __init__(self, directory):
        self.directory = directory
        self.errorLog = ''
        self.cmdLog = ''

    def log(self, flag, text):
        timestamp = time.strftime("%H:%M:%S", time.gmtime())
        if flag == "error":
            self.errorLog += timestamp + "|" + text + "\n"
        if flag == "cmd":
            self.cmdLog += timestamp + "|" + text + "\n"

    def write(self):
        date = time.strftime("%b_%d_%Y", time.gmtime())
        workingDir = self.directory + date + "/"
        if not os.path.isdir(workingDir):
            os.makedirs(workingDir)

        oldCmd = []
        oldError = []

        if os.path.exists(workingDir + "cmd.log"):
            with open(workingDir + "cmd.log", 'r') as f:
                oldCmd = f.read().split("\n")

        if os.path.exists(workingDir + "error.log"):
            with open(workingDir + "error.log", 'r') as f:
                oldError = f.read().split("\n")

        newCmd = self.cmdLog.split("\n")
        newError = self.errorLog.split("\n")

        if len(newCmd) > 0:
            for line in newCmd:
                oldCmd.insert(0, line)
            with open(workingDir + "cmd.log", 'w') as f:
                for line in oldCmd:
                    if len(line) > 0:
                        f.write(line + "\n")

        if len(newError) > 0:
            for line in newError:
                oldError.insert(0, line)
            with open(workingDir + "error.log", 'w') as f:
                for line in oldError:
                    if len(line) > 0:
                        f.write(line + "\n")

        self.errorLog = ""
        self.cmdLog = ""
        return True
