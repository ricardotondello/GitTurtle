import os
from flask import Flask, flash, render_template, request, abort, session
import subprocess
from os import path
from pathlib import Path
import json

##comando_log = 'log --graph -2 --pretty=format:"%Cred%h%Creset - %C(bold blue)<%an> -%C(yellow)%d%Creset %s %Cgreen(%cr) %Creset" --abbrev-commit --date=relative --no-merges '
comando_log = 'log  --pretty=format:"%an | %d | %s | %cr" --abbrev-commit --date=relative --reverse '

prefixo = "remotes/origin/"
branch_logs = []

class commit:
    kind = 'Commit info'
    
    def __init__(self):
        self.autor          = ''
        self.description    = ''
        self.branch         = ''
        self.date_relative  = ''
        
class branch_log:
    kind = 'Armazena o log da branch'
    def __init__(self):
        self.origin      = ''
        self.destiny     = ''
        self.description = ''
        self.order       = 0
        self.color       = 'Red'
        self.comits      = []

app = Flask(__name__)

def git_fetch():
    execute_command("fetch --all")

def get_command(origem, destino):
    return "{gitlog}{branchorigem}..{branchdestino}".format(gitlog=comando_log, branchorigem=prefixo + destino, branchdestino=prefixo + origem)
    
@app.route('/')
def compare_all():
    global branch_logs
    branch_logs = []

    get_config()
    git_fetch()
    add_branchs_log()
   
    return render_template('main.html', branch_logs=branch_logs)

def add_branchs_log():
    global branch_logs
    branch_logs.append(add_branch('release/3.0.1/servicepack', 'release/3.0.1/producao'   , '3.0.1 SP to 3.0.1 P' , 0, 'green'))
    branch_logs.append(add_branch('release/3.0.1/servicepack', 'release/3.0.3/servicepack', '3.0.1 SP to 3.0.3 SP', 1, 'blue'))
    branch_logs.append(add_branch('release/3.0.3/servicepack', 'release/3.0.3/producao'   , '3.0.3 SP to 3.0.3 P' , 2, 'red'))
    branch_logs.append(add_branch('release/3.0.3/servicepack', 'release/3.1.0/servicepack', '3.0.3 SP to 3.1.0 SP', 3, 'blue-grey'))
    branch_logs.append(add_branch('release/3.1.0/servicepack', 'master'                   , '3.1.0 SP to Master'  , 4, 'orange'))
    
def add_branch(origin, destiny, description, order, color):

    b_log = branch_log()
    b_log.origin      = origin
    b_log.destiny     = destiny
    b_log.description = '{0} to {1}'.format(origin, destiny) if not description else description
    b_log.order       = order
    b_log.color       = 'Red' if not color else color
    b_log.comits      = tratar_resultado(execute_command(get_command(origin, destiny)).splitlines())

    return b_log

def tratar_resultado(array_commit):
    comits = []
    for co in array_commit:
        aux = commit()
        aux.autor         = co.split('|')[0].strip()
        aux.branch        = co.split('|')[1].strip()
        aux.description   = co.split('|')[2].strip()
        aux.date_relative = co.split('|')[3].strip()

        ##ignorar merge branches autmaticas.
        if not ("Merge branch '" in aux.description):
            comits.append(aux)

    return comits

def execute_command(comando):
    first_letter = session.get('repository')[0]
    some_command = first_letter + ': && ' + ' cd "' + session.get('repository') + '" && git ' + comando

    p = subprocess.Popen(some_command, stdout=subprocess.PIPE, shell=True)

    (output, err) = p.communicate()  

    p_status = p.wait()
    return output.decode("utf-8")

def get_config():
    path = Path().absolute()
    session['settings_path'] = str(path) + '\\settings.json'

    if not validar_file(session.get('settings_path')):
        return
    
    config                  = json.load(open(session.get('settings_path')))
    session['repository']   = config["repository"]
    
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
    app.secret_key = os.urandom(12)
    app.run(host='0.0.0.0', port=5010)

    
