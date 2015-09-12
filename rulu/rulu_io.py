def facts_to_df(engine, type_name):
    import pandas as pd
    # TODO: Add indexes
    return pd.DataFrame([f._as_dict() for f in engine.get_facts(type_name)])
