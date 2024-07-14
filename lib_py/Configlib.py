import os


class ConfigLibrary():
    def __init__(self, cfgfile):
        self.cfgfile = open(cfgfile, "r")
        self.filelines = self.cfgfile.readlines()
        
        
    def find_value(self, string):
        for line in self.filelines:
            line = line.split("=")
            if line[0] == string.rstrip('\x00'):
                return line[1].strip('\n')
        return "N/A"