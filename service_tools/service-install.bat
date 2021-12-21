nssm install "PathFinder" "pathfinder.exe"
nssm set "PathFinder" AppDirectory %CD%
nssm set "PathFinder" AppStdout %CD%\stdout.log
nssm set "PathFinder" AppStderr %CD%\stderr.log
nssm start "PathFinder"