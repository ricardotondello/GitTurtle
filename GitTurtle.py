import os
from flask import Flask, flash, render_template, request, abort, session
import subprocess
from os import path
from pathlib import Path
import json

##comando_log = 'log --graph -2 --pretty=format:"%Cred%h%Creset - %C(bold blue)<%an> -%C(yellow)%d%Creset %s %Cgreen(%cr) %Creset" --abbrev-commit --date=relative --no-merges '
comando_log = 'log  --pretty=format:"%an | %d | %s | %cr" --abbrev-commit --date=relative --reverse '

prefixo = "remotes/origin/"

versoes = {}
versoes['301sp'] = "release/3.0.1/servicepack"
versoes['301pr'] = "release/3.0.1/producao"
versoes['303sp'] = "release/3.0.3/servicepack"
versoes['303pr'] = "release/3.0.3/producao"
versoes['310sp'] = "release/3.1.0/servicepack"
versoes['master'] = "master"

class commit:
    kind = 'Commit info'
    
    def __init__(self):
        self.autor          = ''
        self.description    = ''
        self.branch         = ''
        self.date_relative  = ''
        

app = Flask(__name__)

def git_fetch():
    execute_command("fetch --all")

def get_command(origem, destino):
    return "{gitlog}{branchorigem}..{branchdestino}".format(gitlog=comando_log, branchorigem=prefixo + versoes[destino], branchdestino=prefixo + versoes[origem])
    
@app.route('/')
def compare_all():
    get_config()
    git_fetch()

    logs = {}

    logs['/3.0.1/servicepack to 3.0.1/producao']    = tratar_resultado(execute_command(get_command('301sp', '301pr')).splitlines())
    logs['/3.0.1/servicepack to 3.0.3/servicepack'] = tratar_resultado(execute_command(get_command('301sp', '303sp')).splitlines())
    logs['/3.0.3/servicepack to 3.0.3/producao']    = tratar_resultado(execute_command(get_command('303sp', '303pr')).splitlines())
    logs['/3.0.3/servicepack to 3.1.0/servicepack'] = tratar_resultado(execute_command(get_command('303sp', '310sp')).splitlines())
    logs['/3.1.0/servicepack to master']            = tratar_resultado(execute_command(get_command('310sp', 'master')).splitlines())
    
   
    return render_template('main.html', logs=logs)

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

    
