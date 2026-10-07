import pandas as pd
df_data = pd.read_csv("outputs/dlmai_south_india_combined_output.csv")
print([c for c in df_data.columns if not c.endswith('_provenance')])
