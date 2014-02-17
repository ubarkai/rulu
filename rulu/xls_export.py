from utils import RuleEngineError, logger
from progress_bar import LogProgressBar

try:
    import xlwt
except ImportError:
    raise NotImplementedError('xlwt must be installed to support export to Excel')

_logger = logger.getChild(__name__)

class ExportSheetWriter(object):
    def __init__(self, workbook, sheet_name, max_rows_in_sheet):
        self.workbook = workbook
        self.sheet_name = sheet_name[:30]
        self.max_rows = max_rows_in_sheet - 1
        self.nrows = 0
        
    def _init_sheet(self, fact):
        self.sheet = self.workbook.add_sheet(self.sheet_name)
        self.fields = sorted(fact)
        for nfield, field in enumerate(self.fields):
            self.sheet.write(self.nrows, nfield, field)
            
    def write_fact(self, fact):
        if self.nrows == 0:
            self._init_sheet(fact)
        elif self.nrows >= self.max_rows:
            return
        self.nrows += 1
        for nfield, field in enumerate(self.fields):
            self.sheet.write(self.nrows, nfield, fact[field])
            
def read_fact_file(facts_filename):
    with open(facts_filename) as f:
        num_facts = sum(1 for _ in f)
    progress_bar = LogProgressBar(_logger, num_facts, 'Reading facts...', 10000)
    with open(facts_filename) as f:
        for line in f:
            template_name, values = line.strip()[1:-1].split(None, 1)
            tokens = values.split('(')[1:]
            fact = {}
            for token in tokens:
                token = token.strip()
                assert token.endswith(')'), token
                key, value = token[:-1].split(None, 1)
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1].replace('\\"', '"')
                fact[key] = value
            yield template_name, fact
            progress_bar.increment()    

def export_facts_to_xls(facts_filename, out_filename, max_rows_in_sheet=10000):
    workbook = xlwt.Workbook()
    writers = {}
    _logger.info('Exporting facts to {}.'.format(out_filename))
    for template_name, fact in read_fact_file(facts_filename):
        writer = writers.get(template_name)
        if writer is None:
            writer = ExportSheetWriter(workbook, template_name, max_rows_in_sheet=max_rows_in_sheet)
            writers[template_name] = writer
        writer.write_fact(fact)
    if not writers:
        raise RuleEngineError('No facts found, cannot export to Excel')
    workbook.save(out_filename)
