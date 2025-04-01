from reverse_connection_listener import NetListener
from executor_server import start_executor_server, start_ngrok_forwarding
from multiprocessing import Process
from UI import UI
import subprocess


def check_forwarding():
    try:
        res = subprocess.run("ps -u", shell=True, capture_output=True, text=True)
        if "ssh -R 49152" in res.stdout:
            print("good to go")
            return 0
        else:
            print("start portforwarding by 'ssh -R 49152:localhost:9999 nglocalhost.com'")
            return 1
    except Exception as e:
        print(e)
        return 1


if __name__ == "__main__":
    exec_serv_proc = Process(target=start_executor_server, args=[], daemon=True)
    exec_serv_proc.start()
    proc = Process(target=start_ngrok_forwarding, args=[], daemon=True)
    proc.start()
    user_interface = UI()
    user_interface.start()
    '''
    status = check_forwarding()
    if status == 0:
        user_interface = UI()
        listener = NetListener()
        listener.start()
    '''
