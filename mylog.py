import logging


class Log:
    def __init__(self):
        self.logger1 = logging.getLogger()
        self.logger1.setLevel(logging.DEBUG)

    def getLogger(self, file_):
        datefmt = '%d-%H:%M.%S'

        handler1 = logging.FileHandler(file_, mode='w')
        handler1.setLevel(logging.DEBUG)
        FORMAT = logging.Formatter(datefmt=datefmt,
                                   fmt='%(asctime)s [%(levelname)s] [%(funcName)s] line:%(lineno)s %(message)s')
        handler1.setFormatter(FORMAT)

        handler2 = logging.StreamHandler()
        handler2.setLevel(logging.CRITICAL)
        FORMAT = logging.Formatter(style='{', datefmt=datefmt, fmt="{levelname}  {asctime}, {message}", )
        handler2.setFormatter(FORMAT)

        self.logger1.addHandler(handler1)
        self.logger1.addHandler(handler2)
        self.logger1.debug('--START--')
        return self.logger1


if __name__ == '__main__':
    log = Log()
    logger = log.getLogger('this_module.txt')
    logger.critical('whoosh!')
