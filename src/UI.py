import curses
from curses import wrapper
from curses.textpad import rectangle
from multiprocessing.connection import Listener
from threading import Thread


class UI:
    def __init__(self):
        self.socket_addr = ('localhost', 6000)
        self.listener = Listener(self.socket_addr, authkey=b'intcomm')
        self.conn = self.listener.accept()
        self.inactive_threshold = 25
        self.send_signal = False
        self.IPs = {}
        self.LOGS = 'starting http daemon ...\nstarting sockets on 6000....'
        stdscr = curses.initscr()
        stdscr.timeout(500)
        self.rows, self.cols = stdscr.getmaxyx()
        self.log_win_width = self.cols - 24
        self.log_win_height = self.rows // 2 - 7
        self.log_window = curses.newwin(
            self.log_win_height,
            self.log_win_width,
            6,
            22
        )
        self.agents_win_height = self.rows - 4 - self.rows // 2
        self.agents_win_width = self.cols - 4
        self.agents_win = curses.newwin(
            self.agents_win_height,
            self.agents_win_width,
            self.rows // 2 + 2,
            2
        )
        self.cols -= 1
        self.rows -= 2

    def listen_socket(self):
        try:
            while True:
                msg = self.conn.recv()
                if msg == self.selector_ip and self.send_signal:
                    self.conn.send(b"<INTERACT>")
                    self.send_signal = False
                    self.add_to_logs("Signal recieved!")
                else:
                    self.conn.send(b"<NULL>")
                self.IPs[msg] = self.inactive_threshold
        finally:
            self.listener.close()
            self.conn.close()

    def header_(self, stdscr):
        midx = self.cols // 2 - 9
        stdscr.attron(self.GOB)
        rectangle(stdscr, 1, 0, 2, midx - 1)
        rectangle(stdscr, 1, midx + 18, 2, self.cols)
        stdscr.attroff(self.GOB)
        stdscr.addstr(0, midx, "┏┳┓┓ •   ┓  ┏┓")
        stdscr.addstr(1, midx, " ┃ ┣┓┓┏┓┏┫  ┣ ┓┏┏┓")
        stdscr.addstr(2, midx, " ┻ ┛┗┗┛ ┗┻  ┗┛┗┫┗ ")
        stdscr.addstr(3, midx, "               ┛  ")

    def groups_(self, stdscr):
        stdscr.attron(self.GOB)
        rectangle(stdscr, 5, 1, self.rows // 2, 20)
        stdscr.attroff(self.GOB)
        stdscr.addstr(5, 3, "|", self.GOB)
        stdscr.addstr(" Groups ", self.WOB)
        stdscr.addstr("|", self.GOB)

    def httpd_logs_(self, stdscr):
        stdscr.attron(self.GOB)
        rectangle(
            stdscr,
            5,
            21,
            self.rows // 2,
            self.cols - 1
        )
        stdscr.attroff(self.GOB)
        stdscr.addstr(5, 21 + 3, "|", self.GOB)
        stdscr.addstr(" Logs ", self.WOB)
        stdscr.addstr("|", self.GOB)

    def agents_(self, stdscr):
        stdscr.attron(self.GOB)
        rectangle(
            stdscr,
            self.rows // 2 + 1,
            1,
            self.rows - 1,
            self.cols - 1
        )
        stdscr.attroff(self.GOB)
        stdscr.addstr(self.rows // 2 + 1, 3, "|", self.GOB)
        stdscr.addstr(" Agents ", self.WOB)
        stdscr.addstr("|", self.GOB)

    def body_(self, stdscr):
        stdscr.attron(self.GOB)
        rectangle(stdscr, 4, 0, self.rows, self.cols)
        stdscr.attroff(self.GOB)
        stdscr.addstr('[', self.GOB)
        stdscr.addstr('j/k', self.YOB)
        stdscr.addstr('→', self.GOB)
        stdscr.addstr('scroll', self.WOB)
        stdscr.addstr('] [', self.GOB)
        stdscr.addstr('i', self.YOB)
        stdscr.addstr('→', self.GOB)
        stdscr.addstr('interact', self.WOB)
        stdscr.addstr('] [', self.GOB)
        stdscr.addstr('t', self.YOB)
        stdscr.addstr('→', self.GOB)
        stdscr.addstr('terminate', self.WOB)
        stdscr.addstr('] [', self.GOB)
        stdscr.addstr('e', self.YOB)
        stdscr.addstr('→', self.GOB)
        stdscr.addstr('executor', self.WOB)
        stdscr.addstr('] [', self.GOB)
        stdscr.addstr('q', self.YOB)
        stdscr.addstr('→', self.GOB)
        stdscr.addstr('exit', self.WOB)
        stdscr.addstr(']', self.GOB)
        self.groups_(stdscr)
        self.httpd_logs_(stdscr)
        self.agents_(stdscr)

    def agent_window_refresh(self):
        agents = ''
        self.agents_win.addstr(0, 0, agents)
        if len(self.IPs) == 0:
            self.selector = None
            self.selector_ip = None
        else:
            if self.selector is None:
                self.selector = 0
            for indx, ip in enumerate(self.IPs.keys()):
                if self.selector == indx:
                    self.agents_win.addstr(f" ⦿  {ip}\n", self.YOBI)
                    self.selector_ip = ip
                else:
                    self.agents_win.addstr(f" ⦿  {ip}\n")
        self.agents_win.addstr(0, 0, agents)
        self.agents_win.refresh()

    def add_to_logs(self, string):
        self.LOGS += '\n' + string
        lgs_ = self.LOGS.split('\n')
        if len(lgs_) > self.log_win_height:
            self.LOGS = '\n'.join(lgs_[1:])

    def key_event_handler(self, ch):
        if ch == ord('q'):
            return 1
        elif ch == ord('j'):
            if self.selector is not None and self.selector < len(self.IPs) - 1:
                self.selector += 1
        elif ch == ord('k'):
            if self.selector is not None and self.selector > 0:
                self.selector -= 1
        elif ch == ord('i'):
            if self.selector is not None:
                self.send_signal = True
                self.add_to_logs(f"<INTERACT> --> {self.selector_ip}")
        return 0

    def run(self, stdscr):
        curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
        self.YOB = curses.color_pair(1)
        self.YOBI = self.YOB | curses.A_REVERSE
        self.WOB = curses.color_pair(2) | curses.A_BOLD
        self.GOB = curses.color_pair(3) | curses.A_DIM
        curses.noecho()
        curses.cbreak()
        stdscr.keypad(True)

        # -------- LOOP -------
        self.pop_keys = []
        while True:
            stdscr.clear()
            self.header_(stdscr)
            self.body_(stdscr)
            stdscr.refresh()

            self.log_window.addstr(0, 0, self.LOGS)
            self.log_window.refresh()
            self.agent_window_refresh()

            ch = stdscr.getch()
            exit_ = self.key_event_handler(ch)
            if exit_:
                break
            for ip in self.IPs.keys():
                self.IPs[ip] -= 1
                if self.IPs[ip] < 0:
                    self.pop_keys.append(ip)
            for ip in self.pop_keys:
                self.IPs.pop(ip)
                self.pop_keys.remove(ip)
        # ---------------------

        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()

    def start(self):
        Thread(target=self.listen_socket, args=[], daemon=True).start()
        wrapper(self.run)
