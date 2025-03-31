import curses
from curses import wrapper
from curses.textpad import rectangle


def read_logs(lines):
    logs = ''
    with open("server_logs.log", "r") as slogs:
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
        stdscr = curses.initscr()
        stdscr.timeout(500)
        self.rows, self.cols = stdscr.getmaxyx()
        log_win_width = self.cols - 24
        log_win_height = self.rows // 2 - 7
        log_window = curses.newwin(log_win_height, log_win_width, 6, 22)
        curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
        self.YOB = curses.color_pair(1)
        self.WOB = curses.color_pair(2) | curses.A_BOLD
        self.GOB = curses.color_pair(3) | curses.A_DIM
        self.cols -= 1
        self.rows -= 2
        curses.noecho()
        curses.cbreak()
        stdscr.keypad(True)

        # -------- LOOP -------
        while True:
            stdscr.clear()
            self.header_(stdscr)
            self.body_(stdscr)
            stdscr.refresh()
            logs = read_logs(log_win_height)
            log_window.addstr(0, 0, logs)
            log_window.refresh()
            ch = stdscr.getch()
            if ch == ord('q'):
                break
        # ---------------------

        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()

    def start(self):
        wrapper(self.run)
