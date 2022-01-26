from subprocess import PIPE, run

class Service():
    def __init__(self, name: str) -> None:
        self.name = name
        if self.status() == "":
            raise Exception("Service not found")

    def status(self):
        status = run("{nssm} status {service}".format(
                    nssm = 'tools\\nssm.exe', 
                    service = self.name), 
                    stdout=PIPE, 
                    stderr=PIPE, 
                    universal_newlines=True, 
                    shell=True)
        result = status.stdout.replace("\x00", "")
        return result.replace("\n", "")

    def start(self):
        run("{nssm} start {service}".format(
                    nssm = 'tools\\nssm.exe', 
                    service = self.name), 
                    stdout=PIPE, 
                    stderr=PIPE, 
                    universal_newlines=True, 
                    shell=True)
        
    def stop(self):
        run("{nssm} stop {service}".format(
                    nssm = 'tools\\nssm.exe', 
                    service = self.name), 
                    stdout=PIPE, 
                    stderr=PIPE, 
                    universal_newlines=True, 
                    shell=True)

if __name__ == '__main__':
    service = Service("PathFinder")