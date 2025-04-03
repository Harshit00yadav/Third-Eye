import curses
from curses import wrapper
from curses.textpad import rectangle
from multiprocessing.connection import Listener
from threading import Thread


def read_logs(lines):
    logs = ''
    with open("logs/server_logs.log", "r") as slogs:
        nlines = slogs.readlines()
        x = len(nlines) - lines
        if x >= 0:
            for nl in range(x, len(nlines) - 1):
                logs += nlines[nl]
        else:
            for nl in nlines:
                logs += nl
    return logs


class UI:
    def __init__(self):
        self.socket_addr = ('localhost', 6000)
        self.listener = Listener(self.socket_addr, authkey=b'intcomm')
        self.conn = self.listener.accept()
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
                self.IPs[msg] = 10
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

    def run(self, stdscr):
        curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
        self.YOB = curses.color_pair(1)
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

            agents = '\n'.join([f" + {ip} {self.IPs[ip]}" for ip in self.IPs.keys()])
            self.agents_win.addstr(0, 0, agents)
            self.agents_win.refresh()
            ch = stdscr.getch()
            if ch == ord('q'):
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
