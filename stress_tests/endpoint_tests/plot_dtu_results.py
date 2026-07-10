import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

path = "caches/stats/comparison_dtu_scaling_03.csv"

df = pd.read_csv(path)

dtu_config = [100,200,300,400,800,1200]

df_initial= df[df["type"] == "initial_import"]
df_initial["dtus"] = dtu_config
df_diff= df[df["type"] == "differential_import"]
df_diff["dtus"] = dtu_config


print(df_initial)

plt.plot(df_initial["dtus"], df_initial["fields_per_sec"], label="inital import", marker="o")
plt.plot(df_diff["dtus"], df_diff["fields_per_sec"], label="differential import", marker="o")
plt.legend()
plt.title("Performance of different import methods, with runtimes ~3minutes")
plt.xlabel("Elastic pool Dtus")
plt.ylabel("imported fields per second")
plt.savefig("caches/plots/import_comparison_dtu.png")
plt.show()