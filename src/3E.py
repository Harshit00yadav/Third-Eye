from executor_server import start_executor_server, start_ngrok_forwarding
from multiprocessing import Process
from UI import UI


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
