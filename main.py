import pandas as pd
import time
from threading import Thread

columns = ['d', 'o', 'h', 'l', 'c']


class Algo:
    def __init__(self, Recv, logger_):
        self.pipe = Recv
        self.pdf = pd.DataFrame()
        self.logger = logger_
        self.logger.debug('Algo started')
        from threading import Event, Lock
        event = Event()
        self.lock = Lock()
        self.index_now = None
        _ = Thread(target=self.__pipe__, args=(event,))
        _.start()
        self.your_function(event)

    def your_function(self, event):
        """this is a toy function to represent what you want to do with the data.
            For now let's save it in a file.
            If you run,stop and run the program again, the file contents will be erased.
            Keeping our local index is important because another thread may modify the DataFrame.
        """
        self.logger.debug('waiting for Event()')
        event.wait()
        index = self.index_now
        try:
            self.pdf.iloc[self.index_now]
        except TypeError:
            self.logger.critical('Empty DataFrame')
            return
        self.logger.debug('passed event')
        self.pdf.iloc[:index].to_csv('main1.csv', mode='w', index=False, header=True)
        while 1:
            if self.pdf.index[-1] == index:
                time.sleep(1)
            else:
                with self.lock:
                    _ = self.pdf.index[-1]
                self.pdf.iloc[index:_].to_csv('main1.csv', mode='a', index=False, header=False)
                index = _

    def __pipe__(self, event):
        """getting data from a pipe and updating our dataframe. Blocks until some data is available. The first data
        to arrive is always a pandas.DataFrame, so, before then, your_function() will raise an empty dataframe
        exception. Threading.Event will pause it until we have a dataframe. In case of an error while your_function() is
        waiting, we set the event so that child_process.join() can return"""
        self.logger.debug('Pipe.recv end started')
        _ = self.pipe.recv()
        if not _:
            self.logger.critical('Sender encountered an error. Pipe closing...')
            S.close()
            event.set()
            return
        self.pdf = pd.concat([self.pdf, pd.DataFrame(_, columns=columns)])
        self.logger.debug(f'Pipe received pandas.Dataframe, length {len(self.pdf)}')
        self.index_now = self.pdf.index[-1]
        event.set()
        self.logger.debug('Event set()')
        self.pipe.send(1)
        try:
            while 1:
                temp = pd.DataFrame(self.pipe.recv(), columns=columns)
                self.logger.debug(f'Received DataFrame len {len(temp)}')
                self.pipe.send(1)
                index = [i for i in range(self.index_now + 1, self.index_now + len(temp) + 1)]
                print(index)
                with self.lock:
                    for _ in index:
                        self.index_now += 1
                temp.index = index
                self.pdf = pd.concat([self.pdf, temp])
                self.logger.debug(f'Internal DataFrame updated, new length {len(self.pdf)}')
        except Exception as e:
            self.pipe.send(0)
            self.logger.critical(str(e))
            raise e


if __name__ == '__main__':
    from multiprocessing import Pipe, Process
    from datafeed import Tv
    from mylog import Log

    log = Log()
    logger = log.getLogger('trading_logs.txt')
    S, R = Pipe(duplex=True)
    child_p = Process(target=Algo, args=(R, logger))
    child_p.start()

    # one of these two must be uncommented
    Tv(S, logger)  # default option
    # Tv(S, logger, True)  # uncomment to specify timeslot e.g. minutes, hours, days etc
    child_p.join()
    # print(child_p.is_alive())
