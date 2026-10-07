import pandas as pd
df_data = pd.read_csv("outputs/dlmai_south_india_combined_output.csv")
print("Columns in df_data:", df_data.columns.tolist()[:15])
