from rulu.rulu_io import facts_to_df

def print_rst_table(engine, fact_type, filename):
    try:
        import tabulate
    except ImportError:
        raise ImportError('You must have tabulate installed in order to build the documentation.')
    df = facts_to_df(engine, fact_type)
    with open(filename, 'w') as fileobj:
        print >>fileobj, tabulate.tabulate(df, headers=[fact_type]+list(df.keys()), 
                                           tablefmt="grid")
