from settings import *

from utils_fcts import *

conn = sqlite3.connect(db_file)

selected_period = "as_all"

start_date ="2024-01-19"
end_date ="2024-01-19"


if selected_period == 'as_all':
    query = f"SELECT * FROM {dbTime_name}"
    interval_txt = " (tout)"
    interval_txt = " Toutes les données"
else:
    query = get_query_extractInterval(dbTime_name, start_date, end_date)
    print(query)
    interval_txt = ("Période : " + start_date.strftime('%d/%m/%Y') + " - " +
                    end_date.strftime('%d/%m/%Y'))
all_df = pd.read_sql_query(query, conn)
conn.close()
puicol_tot = xtpuicol_L1 + "+" + xtpuicol_L2
all_df[puicol_tot] = all_df[xtpuicol_L1] + all_df[xtpuicol_L2]
import numpy as np

df = all_df[[db_timecol, puicol_tot, xtpuicol_L1, xtpuicol_L2]].copy()
df.loc[:, 'catTime'] = np.where(
    (pd.to_datetime(df[db_timecol]).dt.time >=
     datetime.strptime("08:00", "%H:%M").time()) &
    (pd.to_datetime(df[db_timecol]).dt.time <
     datetime.strptime("18:00", "%H:%M").time()),
    "Jour",
    "Nuit"
)
time_df = df[['catTime', puicol_tot, xtpuicol_L1, xtpuicol_L2]].copy()
tot_df = df[[puicol_tot, xtpuicol_L1, xtpuicol_L2]].copy()

catTime_counts = time_df['catTime'].value_counts().reset_index()
# VRAI si 1 jour sélectionné
if selected_period == 'as_day':
    assert (catTime_counts.loc[catTime_counts['catTime'] == 'Nuit', 'count'] == 840).all()
    assert (catTime_counts.loc[catTime_counts['catTime'] == 'Jour', 'count'] == 600).all()


