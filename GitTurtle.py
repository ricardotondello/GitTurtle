import os
from flask import Flask, flash, render_template, request, abort, session
import subprocess
from os import path
from pathlib import Path
import json
import requests
import threading
import time

PORT=5010
SERVER='0.0.0.0'
comando_log = 'log  --pretty=format:"%an | %d | %s | %cr | %H" --abbrev-commit --date=relative --reverse '

prefixo = "remotes/origin/"
branch_logs = []

class commit:
    kind = 'Commit info'
    
    def __init__(self):
        self.autor          = ''
        self.description    = ''
        self.branch         = ''
        self.date_relative  = ''
        self.hash           = ''
        
class branch_log:
    kind = 'Armazena o log da branch'
    def __init__(self):
        self.origin      = ''
        self.destiny     = ''
        self.description = ''
        self.order       = 0
        self.color       = 'Red'
        self.comits      = []
        self.blocked     = False

app = Flask(__name__)

@app.before_first_request
def activate_job():
    def run_job():
        while True:
            print("git fetching...")
            git_fetch()
            time.sleep(60)

    thread = threading.Thread(target=run_job)
    thread.start()

def start_runner():
    def start_loop():
        not_started = True
        while not_started:
            print('In start loop')
            try:
                r = requests.get('http://127.0.0.1:{0}/hl'.format(PORT))
                if r.status_code == 200:
                    print('Server started, quiting start_loop')
                    not_started = False
                print(r.status_code)
            except:
                print('Server not yet started')
            time.sleep(2)
    print('Started runner')
    thread = threading.Thread(target=start_loop)
    thread.start()

@app.route("/hl")
def hello():
    return "Hello World!"


def git_fetch():
    execute_command("fetch --all")

def get_command(origem, destino):
    return "{gitlog}{branchorigem}..{branchdestino}".format(gitlog=comando_log, branchorigem=prefixo + destino, branchdestino=prefixo + origem)
    
@app.route('/')
def compare_all():
    global branch_logs
    branch_logs = []

    load_releases_from_file()
   
    branch_logs_sum =  sum([ len(comits.comits) for comits in branch_logs ])

    return render_template('main.html', branch_logs=branch_logs, branch_logs_sum=branch_logs_sum)

def load_releases_from_file():
    global branch_logs
    path = Path().absolute()
    release_path = str(path) + '\\releases.json'

    if not validar_file(release_path):
        return
    
    with open(release_path, 'r') as data_file:
        release_array = json.loads(data_file.read())
    
    for release in release_array['releases']:
        branch_logs.append(add_branch(release["origin"], release["destiny"], release["description"], release["order"], release["color"], release["blocked"]))

def add_branch(origin, destiny, description, order, color, blocked):

    b_log = branch_log()
    b_log.origin      = origin
    b_log.destiny     = destiny
    b_log.description = '{0} to {1}'.format(origin, destiny) if not description else description
    b_log.order       = order
    b_log.color       = 'Red' if not color else color
    b_log.comits      = tratar_resultado(execute_command(get_command(origin, destiny)).splitlines())
    b_log.blocked     = blocked

    return b_log

def tratar_resultado(array_commit):
    comits = []
    for co in array_commit:
        aux = commit()
        aux.autor         = co.split('|')[0].strip()
        aux.branch        = co.split('|')[1].strip()
        aux.description   = co.split('|')[2].strip()
        aux.date_relative = co.split('|')[3].strip()
        aux.hash          = co.split('|')[4].strip()

        ##ignorar merge branches autmaticas.
        if not ("Merge branch '" in aux.description):
            comits.append(aux)

    return comits

def execute_command(comando):
    repository = get_config()
    first_letter = repository[0]
    some_command = first_letter + ': && ' + ' cd "' + repository + '" && git ' + comando

    p = subprocess.Popen(some_command, stdout=subprocess.PIPE, shell=True)

    (output, err) = p.communicate()  

    p_status = p.wait()
    return output.decode("utf-8")

def get_config():
    path = Path().absolute()
    settings_path = str(path) + '\\settings.json'

    if not validar_file(settings_path):
        return
    
    config                  = json.load(open(settings_path))
    return config["repository"]
    
def validar_file(ps_file):
    if not ps_file:
        return False
    return (os.path.isfile(ps_file) and os.access(ps_file, os.R_OK))

def load_remotes():
    results = str(execute_command("branch -r")).split('\\n')
     
    remote_branches = []
    remote_branches.append('origin/master')
    for s in results:
        if '/release/' in s:
            if not ('2.0.20' in s):
                remote_branches.append(s)

    return remote_branches

if __name__ == "__main__":
    start_runner()
    app.secret_key = os.urandom(12)
    app.run(host=SERVER, port=PORT)

    
