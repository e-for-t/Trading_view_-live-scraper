import pandas as pd 
import time
from threading import Thread

class algo:
    def __init__(self,R):
        self.pipe=R
        self.pdf=pd.DataFrame()
        self._pipe_()
        _=Thread(target=self.__pipe__)
        _.start()
        self.index_now=self.pdf.index[-1]
        self.your_function(self.index_now)

    def your_function(self,index):
        '''this is a toy function to represent what you want to do with the data.
            For now let's save it in a file.
            If you run,stop and run the program again, the file contents will be erased.
            indexing is important because another thread may modify the DataFrame.
        '''
        self.pdf.iloc[:index].to_csv('main1.csv',mode='w',index=False,header=True)
        while 1:
            if self.pdf.index[-1]==index:
                time.sleep(1)
            else:
                _=self.pdf.index[-1]
                self.pdf.iloc[index:_].to_csv('main1.csv',mode='a',index=False,header=False)
                index=_

    def __pipe__(self):
        while 1:
            _=pd.DataFrame(self.pipe.recv(),columns=('d','o','h','l','c'))
            self.pipe.send(1)
            index=[i for i in range(self.index_now+1,self.index_now+len(_)+1)]
            for i in index:
                self.index_now+=1
            _.index=index
            self.pdf=pd.concat([self.pdf,_])

    def _pipe_(self):
        '''getting data from a pipe and updating our dataframe'''
        self.pdf=pd.concat([self.pdf,pd.DataFrame(self.pipe.recv(),columns=('d','o','h','l','c'))])
        self.pipe.send(1)

if __name__=='__main__':
    from multiprocessing import Pipe,Process
    from datafeed import Tview_wsmsgs
    S,R=Pipe(duplex=True)
    child_p=Process(target=algo,args=(R,))
    child_p.start()
    Tview_wsmsgs(S) #default option
    # Tview_wsmsgs(S,True) #uncomment to spefify timeslot e.g. minutes, hours, days etc  
    child_p.terminate()
    
