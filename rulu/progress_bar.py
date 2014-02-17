import sys

class ProgressBar(object):
    def __init__(self, total, message=None, blocksize=100, width=20):
        self.total = total
        self.message = message or ''
        self.blocksize = blocksize
        self.width = width
        self.count = 0
        self.blocknum = -1
        
    def increment(self, value=1):
        prev_blocknum = self.blocknum
        self.count += value
        self.blocknum = self.count / self.blocksize
        finished = self.count == self.total
        if self.blocknum != prev_blocknum or finished:
            progress = self.count * self.width / self.total 
            output = '{} [{}{}] {}/{}\r'.format(self.message, '*' * progress,
                    '-'*(self.width - progress), self.count, self.total)
            self._emit(output)
        if finished:
            self._emit_finished() 
            
    def _emit(self, message): raise NotImplementedError
    def _emit_finished(self): raise NotImplementedError

class StderrProgressBar(ProgressBar):
    def _emit(self, message):
        print >>sys.stderr, message
        
    def _emit_finished(self):
        print >>sys.stderr
        print >>sys.stderr
        
class LogProgressBar(ProgressBar):
    def __init__(self, logger, *args, **kwargs):
        super(LogProgressBar, self).__init__(*args, **kwargs)
        self.logger = logger
        
    def _emit(self, message):
        self.logger.debug(message)
        
    def _emit_finished(self):
        pass
