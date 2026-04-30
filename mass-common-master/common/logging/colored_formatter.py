import logging

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)
STANDARD, BOLD = range(2)
FOREGROUND, BACKGROUND = 30, 40

# These are the sequences need to get colored output
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[%d;%dm"

COLORS = {
    logging.DEBUG: (STANDARD, FOREGROUND + WHITE),
    logging.INFO: (STANDARD, FOREGROUND + GREEN),
    logging.WARNING: (STANDARD, FOREGROUND + YELLOW),
    logging.ERROR: (STANDARD, FOREGROUND + RED),
    logging.CRITICAL: (BOLD, FOREGROUND + RED),
}


class ColoredFormatter(logging.Formatter):
    def format(self, record):
        color = COLOR_SEQ % COLORS.get(record.levelno, (WHITE, STANDARD))
        record.levelname = color + record.levelname + RESET_SEQ
        return logging.Formatter.format(self, record) + RESET_SEQ
