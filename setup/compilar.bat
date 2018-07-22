
rem remove os arquivos temporarios
del /s /q D:\dsv\GIT\GitTurtle\setup\__pycache__\*
del /s /q D:\dsv\GIT\GitTurtle\setup\build\*
del /s /q D:\dsv\GIT\GitTurtle\setup\dist\*
del /s /q D:\dsv\GIT\GitTurtle\setup\GitTurtle.spec


rem gera o executavel do python
pyinstaller --onefile ..\GitTurtle.py


