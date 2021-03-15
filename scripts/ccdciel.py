# Python function to use the CCDciel JSON-RPC interface.
# For more information and reference of the available methods see: 
# https://www.ap-i.net/ccdciel/en/documentation/jsonrpc_reference
#
# The following function can be imported:
# ccdciel()
# IsRunning()
# StartProgram()
# StopProgram()

import sys
import os
import platform
IsWindows = False
IsDarwin = False
if platform.system() == 'Windows':
    IsWindows = True
    sys.path.extend(os.getenv("PYTHONPATH").split(os.pathsep))
elif platform.system() == 'Darwin':
    IsDarwin = True

try:
  from urllib import request
except:
  print('Cannot import urllib.request, your version of python is probably too old, try python3')
  sys.exit(1)
try:
  import json
except:
  print('Cannot import json, your version of python is probably too old, try python3')
  sys.exit(1)
try:
  import subprocess
except:
  print('Cannot import subprocess, your version of python is probably too old, try python3')
  sys.exit(1)

if not IsWindows:
    import psutil

id = 0

# Define the function to call CCDciel method
def ccdciel(method, params=''):
    
    # Increment the request id
    global id
    id += 1

    # Get host and port from environment variable
    host = os.getenv('CCDCIEL_HOST')
    if host == None :
       host='localhost' 
    port = os.getenv('CCDCIEL_PORT')
    if port == None :
       port='3277'
       
    # The request URL
    ccdciel_url = "http://" + host + ":" + port + "/jsonrpc"

    # Prepare JSON request
    jsondata = json.dumps({"jsonrpc": "2.0", "id": id,
        "method": method,
        "params": [params] }
        ).encode('utf8')

    try:
       # Execute the request using POST method
       req = request.Request(ccdciel_url)
       req.add_header('Content-Type', 'application/json; charset=utf-8')
       res = request.urlopen(req, jsondata).read()
    except Exception as inst:
       print(type(inst))
       print(inst.args)
       sys.exit(1)
    
    # Return result as JSON
    return json.loads(res.decode("utf8"))


# Utility function to test if a program is running
# parameter is exe name without the path
def IsRunning (pgm):
    alreadyrunning = False
    if IsWindows:
        Data = subprocess.check_output(['wmic', 'process', 'get', 'name'])
        a = str(Data)
        try:
            for i in range(len(a)):
                if a.split('\\r\\r\\n')[i].strip() == pgm:
                    alreadyrunning = True
        except:
            pass
    else:
        for proc in psutil.process_iter():
            if proc.name() == pgm :
                alreadyrunning = True
    return alreadyrunning


# Utility function to start a program
# parameters are exe name and path, if path is not specified this use the PATH environment
def StartProgram(pgm, pgmpath='') :
    if not IsRunning(pgm):
        if pgmpath:
            pgm = os.path.join(pgmpath,pgm)
        if IsWindows:
            subprocess.Popen(pgm, close_fds=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        else:
            subprocess.Popen(pgm, close_fds=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        started = True
    else:
        started = False
    return started


# Utility function to stop a program
# parameter is exe name without the path
def StopProgram(pgm) :
    if IsWindows:
        subprocess.Popen(['taskkill', '/IM', pgm], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    else:
        for proc in psutil.process_iter():
            if proc.name() ==  pgm :
                try:
                    proc.terminate()
                except Exception as inst:
                    print(type(inst))
                    print(inst.args)