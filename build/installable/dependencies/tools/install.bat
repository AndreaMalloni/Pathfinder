@echo off
for %%a in ("%CD%") do set "root_folder=%%~dpa"

.\nssm install "PathFinder" "%root_folder%pathfinder.exe"
.\nssm set "PathFinder" AppStdout "%root_folder%logs\stdout.log"
.\nssm set "PathFinder" AppStderr "%root_folder%logs\stderr.log"