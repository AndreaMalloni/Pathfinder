@echo off
for %%a in ("%CD%") do set "root_folder=%%~dpa"

.\nssm install "PathFinder" "%root_folder%pathfinder.exe"