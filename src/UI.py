import sys
import curses
from curses import wrapper
from curses.textpad import rectangle, Textbox
from multiprocessing.connection import Listener
from multiprocessing import Process
from screen_reciever import view_agent_screen
from threading import Thread


def popup_rectangle(win, uly, ulx, lry, lrx):
    rectangle(win, uly, ulx, lry, lrx)
    n = lrx - ulx + 1
    win.addstr(uly - 1, ulx, u'\u2588' * n)
    win.addstr(lry + 1, ulx, u'\u2588' * n)


class UI:
    def __init__(self):
        self._init_signals()
        self.socket_addr = ('localhost', 36250)
        self.listener = Listener(self.socket_addr, authkey=b'intcomm')
        self.conn = self.listener.accept()
        self.inactive_threshold = 25
        self.pid_vas = None
        self.send_signal = False
        self.signal = None
        self.spawn_terminal = False
        self.popup_message = None
        self.IPs = {}
        self.LOGS = 'starting http daemon ...\nstarting sockets on 6000....'
        self.EXECUTOR_MESSAGE = self.SLEE_SIG
        self.INTERACTION_URL = None
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

    def _init_signals(self):
        self.TERM_SIG = b"<TERMINATE>"
        self.INTR_SIG = b"<INTERACT>"
        self.SLEE_SIG = b"<SLEEP>"
        self.VIEW_SIG = b"<VIEWSCREEN>"
        self.STOP_SIG = b"<STOPSCREEN>"

    def show_alert(self, msg, time):
        self.popup_message = msg
        self.popup_time_counter = time

    def alert_popup(self, stdscr, msg):
        y = self.rows // 2
        x = (self.cols // 2) - (len(msg) // 2) - 2
        stdscr.attron(self.ROB)
        popup_rectangle(stdscr, y - 1, x, y + 1, x + len(msg) + 3)
        stdscr.addstr(y, x + 1, f" {msg} ")
        stdscr.attroff(self.ROB)

    def listen_socket(self):
        try:
            while True:
                msg = self.conn.recv()
                if msg == self.selector_ip and self.signal == self.TERM_SIG:
                    secs = 0
                else:
                    secs = self.inactive_threshold
                if msg == self.selector_ip and self.send_signal:
                    self.conn.send(self.signal)
                    self.send_signal = False
                    self.signal = None
                    self.add_to_logs("Signal recieved!")
                elif "[ LOG ]" in msg:
                    self.add_to_logs(msg)
                    self.conn.send('got it')
                    continue
                else:
                    self.conn.send(self.EXECUTOR_MESSAGE)
                self.IPs[msg] = secs
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

    def spawn_input_terminal(self, stdscr):
        height, width = 1, 65
        top, left = self.rows // 2 - 1, (self.cols // 2) - (width // 2)
        stdscr.attron(self.GOB)
        rectangle(
            stdscr,
            top - 1,
            left - 1,
            top + height,
            left + width
        )
        stdscr.attroff(self.GOB)
        stdscr.refresh()
        window = curses.newwin(height, width, top, left)
        window.clear()
        box = Textbox(window)
        box.edit()
        contents = box.gather().strip()
        contents = contents.replace('[200~', '').replace('[201~', '')
        return contents

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
        stdscr.addstr('v', self.YOB)
        stdscr.addstr('→', self.GOB)
        stdscr.addstr('open', self.WOB)
        stdscr.addstr('] [', self.GOB)
        stdscr.addstr('e', self.YOB)
        stdscr.addstr('→', self.GOB)
        stdscr.addstr('executor', self.WOB)
        stdscr.addstr('] [', self.GOB)
        stdscr.addstr('t', self.YOB)
        stdscr.addstr('→', self.GOB)
        stdscr.addstr('terminate', self.WOB)
        stdscr.addstr('] [', self.GOB)
        stdscr.addstr('q', self.YOB)
        stdscr.addstr('→', self.GOB)
        stdscr.addstr('exit', self.WOB)
        stdscr.addstr(']', self.GOB)
        self.groups_(stdscr)
        self.httpd_logs_(stdscr)
        self.agents_(stdscr)
        if self.spawn_terminal:
            content = self.spawn_input_terminal(stdscr)
            self.spawn_terminal = False
            if self.signal == self.INTR_SIG:
                self.INTERACTION_URL = bytes(content, 'utf-8')
                self.signal += b'@' + self.INTERACTION_URL
                self.send_signal = True
            elif self.signal == self.VIEW_SIG:
                self.VIEW_URL = bytes(content, 'utf-8')
                self.signal += b'@' + self.VIEW_URL
                self.send_signal = True
                self.pid_vas = Process(target=view_agent_screen, args=[])
                self.pid_vas.start()
                self.add_to_logs("[ ON ] Screen Reciever")
            else:
                self.EXECUTOR_MESSAGE = bytes(content, 'utf-8')
                self.add_to_logs(f"EXEC_MESSAGE = {content}")

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
                    self.agents_win.addstr(f" ⦿  {ip} \n", self.YOBI)
                    self.selector_ip = ip
                else:
                    self.agents_win.addstr(f" ⦿  {ip} \n")
        self.agents_win.addstr(0, 0, agents)
        self.agents_win.refresh()

    def add_to_logs(self, string):
        self.LOGS += '\n' + string
        lgs_ = self.LOGS.split('\n')
        if len(lgs_) > self.log_win_height:
            self.LOGS = '\n'.join(lgs_[1:])

    def key_event_handler(self, ch):
        if ch == ord('q'):
            self.pid_vas.kill()
            return 1
        elif ch == ord('j'):
            if self.selector is not None and self.selector < len(self.IPs) - 1:
                self.selector += 1
        elif ch == ord('k'):
            if self.selector is not None and self.selector > 0:
                self.selector -= 1
        elif ch == ord('i'):
            if self.selector is not None:
                self.signal = self.INTR_SIG
                self.add_to_logs(f"{self.signal} --> {self.selector_ip}")
                self.spawn_terminal = True
            else:
                self.show_alert("Bad Agent", 3)
        elif ch == ord('v'):
            if self.selector is not None:
                self.signal = self.VIEW_SIG
                self.add_to_logs(f"{self.signal} --> {self.selector_ip}")
                self.spawn_terminal = True
            else:
                self.show_alert("Bad Agent", 3)
        elif ch == ord('e'):
            self.spawn_terminal = True
        elif ch == ord('t'):
            self.send_signal = True
            self.signal = self.TERM_SIG
            self.add_to_logs(f"{self.signal} --> {self.selector_ip}")
        if self.pid_vas is not None and not self.pid_vas.is_alive():
            self.pid_vas = None
            self.send_signal = True
            self.signal = self.STOP_SIG
            self.add_to_logs("[ OFF ] Screen Reciever")
        return 0

    def run(self, stdscr):
        curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)
        self.YOB = curses.color_pair(1)
        self.YOBI = self.YOB | curses.A_REVERSE
        self.WOB = curses.color_pair(2) | curses.A_BOLD
        self.GOB = curses.color_pair(3) | curses.A_DIM
        self.ROB = curses.color_pair(4) | curses.A_BOLD
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
            if self.popup_message is not None:
                self.alert_popup(stdscr, self.popup_message)
                self.popup_time_counter -= 1
                if self.popup_time_counter < 0:
                    self.popup_message = None

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
        sys.stdout.write("\x1b[?2004h")
        sys.stdout.flush()
        wrapper(self.run)
        sys.stdout.write("\x1b[?2004l")
        sys.stdout.flush()
