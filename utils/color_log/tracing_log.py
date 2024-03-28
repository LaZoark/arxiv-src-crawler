import time

class Tracing:
  def __init__(self) -> None:
    pass
  last_upload_tid: int = 0
  '''Trace the latest push ITD'''
  def now(self):
    '''return current time in seconds. (Unix timestamp)'''
    return int(time.time())

class Timer:
  def __init__(self, start_time: float=None):
    '''Measure the usage of time during any process (e.g., training or testing)\n
    Parameters:  
    start_time: usually set to `time.time()`
    '''
    # self.start_time = start_time
    self.start_time = time.time()
    self.__update()
    
  def __update(self):
    self.time_span = time.time() - self.start_time
    self.m = int(self.time_span//60)
    self.h = int(self.m//60)
    self.m = int(self.m%60)
    self.s = self.time_span%60
    return self
  
  def update(self, sep: str=':', show_float: int=0) -> str:
    '''
    
    Args:
      sep (str): the seperator for formating the time.
      sep (str="::"): the seperator for formating the time.
      sep (str=":"): the seperator for formating the time.
      show_float (int=0): decide the number of digits to show of floating point for `second`.
    
    Returns:
      str: `hh<sep>mm<sep>ss.f` where `f` stands for the shown floating point.
      str: hh<`sep`>mm<`sep`>ss.f where `f` stands for the shown floating point.
    '''
    self.__update()
    return f'{self.h:0>2}{sep}{self.m:0>2}{sep}{self.s:0>2.{show_float}f}'
  
  def freq(self, amount: int, show_float: int=1) -> str:
    '''Given the amount and calculate the speed of process.'''
    amount = 1 if amount==0 else amount   # prevent from deviding by zero
    return f'{self.time_span/amount:>5.{show_float}f}'




if __name__ == '__main__':
  ss = Tracing()
  print(ss.now())
  
  ########################################### Timer ###########################################
  # from time import sleep
  
  start_t = time.time() - 3904
  timer = Timer(start_time=start_t)
  time.sleep(1.3)
  print(f'{timer.s = }')
  print(f'{timer.m = }')
  print(f'{timer.h = }')
  print(timer.update(sep=':', show_float=2))
  print('CWRU [   1/1500] Train Loss:  2.361, Train Accuracy:  8.906% || Valid Loss:  2.357, Valid Accuracy: 9.271%', end='')
  print(f' (t={timer.update(show_float=0)})')
  print(f'{int(timer.time_span) = }')
  # print(f'{timer.freq(7) = }')
  
  for i in range(10):
    time.sleep(0.3)
    print(f'{timer.freq(i) = }')
