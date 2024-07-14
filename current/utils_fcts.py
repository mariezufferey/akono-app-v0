from settings import *
from datetime import timedelta


def get_var_desc(col, db):
    if db == dbTime_name:
        desc_txt = "<b>" + col + "</b> : " + \
                   showcols_settings[col]['description']

    elif db == dbDayP_name:
        desc_txt = "<b>" + col + "</b> : " + \
                   dayPcols_settings[col]['description']

    elif db == dbDayI_name:
        desc_txt = "<b>" + col + "</b> : " + \
                   dayIcols_settings[col]['description']

    else:
        return None
    return desc_txt


# récupérer toutes les colonnes de la table "donnees" sauf "time"
def get_timedata_columns():
    conn = sqlite3.connect(db_file)
    query = f"PRAGMA table_info({dbTime_name})"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return [col for col in df['name'] if col != db_timecol]

def get_daydata_columns(dayType):
    conn = sqlite3.connect(db_file)
    if dayType == "P":
        query = f"PRAGMA table_info({dbDayP_name})"
    elif dayType == "I":
        query = f"PRAGMA table_info({dbDayI_name})"
    else:
        exit(1)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return [col for col in df['name'] if col != db_daycol]

# def prep_table(dt, dt_type, currday=None):
#     if dt_type == 'time':
#         assert re.search(r'00:00$', dt.iloc[0][0])
#         assert re.search(r'23:59$',dt.iloc[dt.shape[0] - 1][0])
#
#         #SQLite utilise le format ISO 8601 pour les dates et les heures, ce qui est très pratique
#         # pour les manipulations ultérieures et les requêtes. Le format ISO 8601 est sous la forme YYYY-MM-DD HH:MM:SS.
#         dt[0] = pd.to_datetime(dt[0], format='%d.%m.%Y %H:%M').dt.strftime('%Y-%m-%d %H:%M:%S')
#
#         #assert dt.iloc[:, nColsTime].isna().all()
#         assert dt.iloc[:, nColsTime+1].isna().all()
#         dt = dt.iloc[:, 0:nColsTime]
#
#
#         dt.columns = time_txt_cols + time_real_cols #['col' + str(i) for i in range(1, len(dt.columns) + 1)]
#
#         ### ajouter les colonnes demandées
#         dt["XT_Iin_Aac_I3116_tot"] = (dt["XT_Iin_Aac_I3116_L1"]+
#                                          dt["XT_Iin_Aac_I3116_L2"])
#
#         dt["XT_Pin_a_kW_I3119_tot"] = (dt["XT_Pin_a_kW_I3119_L1_1"]+
#                                          dt["XT_Pin_a_kW_I3119_L2_2"])
#
#         dt["XT_Pout_a_kW_I3101_tot"] = (dt["XT_Pout_a_kW_I3101_L1_1"]+
#                                          dt["XT_Pout_a_kW_I3101_L2_2"])
#
#         ### arrondir au 10ème
#         dt["BSP_Tbat_C_I7033_1"] = dt['BSP_Tbat_C_I7033_1'].round(2)
#
#     elif dt_type == "dayP":
#         assert dt.iloc[:, nColsDayP].isna().all()
#         dtm = dt.melt(id_vars=[0],
#                             value_vars=list(dt.columns)[1:nColsDayP],
#                             var_name='variable',
#                             value_name='value')
#         dtm.iloc[:, 0] = dtm.iloc[:, 0] + "_" + dtm.iloc[:, 1].astype(str)
#         dtm.drop(columns=['variable'], inplace=True)
#         dt = dtm.T
#         dt.columns = dt.iloc[0]
#         dt = dt[1:]
#         dt.insert(0, day_txt_cols[0], currday)
#     elif dt_type == "dayI":
#         assert dt.iloc[:, nColsDayI].isna().all()
#
#         dtm = dt.melt(id_vars=[0],
#                             value_vars=list(dt.columns)[1:nColsDayI],
#                             var_name='variable',
#                             value_name='value')
#         dtm.iloc[:, 0] = dtm.iloc[:, 0] + "_" + dtm.iloc[:, 1].astype(str)
#         dtm.drop(columns=['variable'], inplace=True)
#         # dt = dt.iloc[:, 0:nColsDayI].T
#         dt = dtm.T
#         dt.columns = dt.iloc[0]
#         dt = dt[1:]
#         dt.insert(0, day_txt_cols[0], currday)
#
#     else:
#         exit(1)
#     return dt
#



# lire les 10 premières lignes de la base de données
def fetch_timedata(date=None):
    conn = sqlite3.connect(db_file)
    if date:
        # query = f"SELECT * FROM {dbTime_name} WHERE DATE({db_timecol}) = '{date}' LIMIT 10"
        query = f"SELECT * FROM {dbTime_name} WHERE DATE({db_timecol}) = '{date}'"
    else:
        # query = f"SELECT * FROM {dbTime_name}"
        query = f"SELECT * FROM {dbTime_name} LIMIT 10"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


# # récupérer toutes les dates disponibles dans la base de données
# def get_timedata_dates():
#     conn = sqlite3.connect(db_file)
#     query = "SELECT DISTINCT DATE("+db_timecol+") as date FROM " + dbTime_name
#     df = pd.read_sql_query(query, conn)
#     conn.close()
#     return df[db_timecol].tolist()
#
# # Récupérer les dates disponibles
#all_dates = get_timedata_dates()
#print(','.join(all_dates))

# def fetch_dayPdata_dates():
#     conn = sqlite3.connect(db_file)
#     query = "SELECT DISTINCT " + day_txt_cols[0] + " FROM " + dbDayP_name
#     ## assumed that same data in dayP and dayI !!!
#     df = pd.read_sql(query, conn)
#     conn.close()
#     return df[db_daycol].tolist()
#


def fetch_timedata_dates():
    conn = sqlite3.connect(db_file)
    query = "SELECT DISTINCT " + time_txt_cols[0] + " FROM " + dbTime_name
    df = pd.read_sql(query, conn)
    conn.close()
    return df[db_timecol].tolist()


def fetch_dayPdata_dates(day_type):
    conn = sqlite3.connect(db_file)
    query = "SELECT DISTINCT " + day_txt_cols[0] + " FROM " + day_type#day_type=dbDayP_name
    df = pd.read_sql(query, conn)
    conn.close()
    return df[db_daycol].tolist()

def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:

        print("Try reading file : " + filename)

        # day_dt = pd.read_csv(io.StringIO(decoded.decode(enc)),
        #                      skiprows=3, nrows=60 * 24, sep=";", header=None)
        #
        # print("file read...")
        #
        # print("first date : " + day_dt.iloc[0][0])
        # print("laste date : " + day_dt.iloc[day_dt.shape[0] - 1][0])
        # # vérifier que la 1ère ligne est 00:00
        # assert re.search(r'00:00$', day_dt.iloc[0][0])
        # assert re.search(r'23:59$', day_dt.iloc[day_dt.shape[0] - 1][0])
        #
        # # SQLite utilise le format ISO 8601 pour les dates et les heures, ce qui est très pratique
        # # pour les manipulations ultérieures et les requêtes. Le format ISO 8601 est sous la forme YYYY-MM-DD HH:MM:SS.
        # day_dt[0] = pd.to_datetime(day_dt[0], format='%d.%m.%Y %H:%M').dt.strftime('%Y-%m-%d %H:%M:%S')
        # day_dt.columns = time_txt_cols + time_real_cols  # ['col' + str(i) for i in range(1, len(day_dt.columns) + 1)]
        #
        # # Connexion à la base de données SQLite
        # conn = sqlite3.connect(db_file)
        # c = conn.cursor()
        # # Créer une table avec la première colonne comme datetime et les autres comme REAL (float)
        # c.execute('''
        #     CREATE TABLE IF NOT EXISTS ''' + dbTime_name + "(" +
        #           ','.join([x + " TEXT" for x in time_txt_cols]) + "," +
        #           ','.join([x + " REAL" for x in time_real_cols]) + '''
        #     ) ''')
        # conn.commit()
        #
        # # Insérer les données dans la base de données
        # day_dt.to_sql(dbTime_name, conn, if_exists='append', index=False)
        #
        # # important de fermer la connexion
        # conn.close()


        ######## 1ère table : les données heure par heure
        # day_dt = pd.read_csv(io.StringIO(decoded.decode(enc)),
        #                      skiprows=nHeaderSkip, nrows=60 * 24, sep=csvSep, header=None)
        # # day_dt = pd.read_csv(datafile, skiprows=nHeaderSkip, nrows=60*24, encoding=enc,
        # #                  sep=csvSep,header=None)
        # # vérifier que la 1ère ligne est 00:00
        # assert re.search(r'00:00$', day_dt.iloc[0][0])
        # assert re.search(r'23:59$',day_dt.iloc[day_dt.shape[0] - 1][0])
        #
        # #SQLite utilise le format ISO 8601 pour les dates et les heures, ce qui est très pratique
        # # pour les manipulations ultérieures et les requêtes. Le format ISO 8601 est sous la forme YYYY-MM-DD HH:MM:SS.
        # day_dt[0] = pd.to_datetime(day_dt[0], format='%d.%m.%Y %H:%M').dt.strftime('%Y-%m-%d %H:%M:%S')
        #
        # assert day_dt.iloc[:, nColsTime].isna().all()
        # assert day_dt.iloc[:, nColsTime+1].isna().all()
        # day_dt = day_dt.iloc[:, 0:nColsTime]
        #
        #
        # day_dt.columns = time_txt_cols + time_real_cols #['col' + str(i) for i in range(1, len(day_dt.columns) + 1)]


        day_dt = prep_table(pd.read_csv(io.StringIO(decoded.decode(enc)),
                             skiprows=nHeaderSkip, nrows=60 * 24, sep=csvSep, header=None),"time")

        curr_day = day_dt[time_txt_cols[0]][0].split(' ')[0]

        ######## 2ème table : bilan journier P

        # p_dt = pd.read_csv(datafile, skiprows=nHeaderSkip + 60 * 24,
        #                    nrows=nRowsDayP, encoding=enc,
        #                    sep=csvSep, header=None)
        p_dt = prep_table(pd.read_csv(io.StringIO(decoded.decode(enc)),
                             skiprows=nHeaderSkip + 60 * 24,
                           nrows=nRowsDayP, sep=csvSep, header=None),"dayP", curr_day)
        # p_dt = pd.read_csv(io.StringIO(decoded.decode(enc)),
        #                      skiprows=nHeaderSkip + 60 * 24,
        #                    nrows=nRowsDayP, sep=csvSep, header=None)
        #
        # assert p_dt.iloc[:, nColsDayP].isna().all()
        # p_dt = p_dt.iloc[:, 0:nColsDayP].T
        # p_dt.columns = p_dt.iloc[0]
        # p_dt = p_dt[1:]
        # p_dt.insert(0, day_txt_cols[0], curr_day)

        ######## 3ème table : bilan journier I

        # i_dt = pd.read_csv(datafile, skiprows=nHeaderSkip + 60 * 24 + nRowsDayP,
        #                    nrows=nRowsDayI, encoding=enc,
        #                    sep=csvSep, header=None)
        i_dt = prep_table(pd.read_csv(io.StringIO(decoded.decode(enc)),
                             skiprows=nHeaderSkip + 60 * 24 + nRowsDayP,
                           nrows=nRowsDayI, sep=csvSep, header=None),
                          "dayI", curr_day)

        # assert i_dt.iloc[:, nColsDayI].isna().all()
        # i_dt = i_dt.iloc[:, 0:nColsDayI].T
        # i_dt.columns = i_dt.iloc[0]
        # i_dt = i_dt[1:]
        # i_dt.insert(0, day_txt_cols[0], curr_day)

        print(":-) data reading success for " + filename)

        # Connexion à la base de données SQLite
        conn = sqlite3.connect(db_file)
        c = conn.cursor()

        # Créer les tables si pas existant
        c.execute('''CREATE TABLE IF NOT EXISTS ''' + dbTime_name + "(" +
                  ','.join([x + " TEXT" for x in time_txt_cols]) + ","+
        ','.join([x + " REAL" for x in time_real_cols+time_added_cols]) + '''
            )''')
        c.execute('''CREATE TABLE IF NOT EXISTS ''' + dbDayP_name + "(" +
                  ','.join([x + " TEXT" for x in day_txt_cols]) + "," +
                  ','.join([x + " REAL" for x in dayP_real_cols]) + '''
              )''')
        c.execute('''CREATE TABLE IF NOT EXISTS ''' + dbDayI_name + "(" +
                  ','.join([x + " TEXT" for x in day_txt_cols]) + "," +
                  ','.join([x + " REAL" for x in dayI_real_cols]) + '''
              )''')
        conn.commit()

        # Insérer les données dans la base de données
        day_dt.to_sql(dbTime_name, conn, if_exists='append', index=False)
        p_dt.to_sql(dbDayP_name, conn, if_exists='append', index=False)
        i_dt.to_sql(dbDayI_name, conn, if_exists='append', index=False)

        # Il est important de fermer la connexion une fois que toutes les opérations sont complétées
        conn.close()

        print("données ajoutées à la DB")

        return html.Div([
            'Successfully uploaded and inserted: {}'.format(filename)
        ])

        # if 'csv' in filename:
        #     # Assume that the user uploaded a CSV file
        #     df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        #     # Optionally, convert and clean the data as necessary
        #     insert_data(df)

    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing the file : ' + filename
        ])


def get_query_extractInterval(dbname, startday, endday):
    if not endday and not startday:
        return f"SELECT * FROM {dbname}"
    if dbname==dbTime_name:
        if startday and endday:
            return f"SELECT * FROM {dbname} WHERE DATE({db_timecol}) >= DATE('{startday}') AND DATE({db_timecol}) <= DATE('{endday}')"
        elif startday and not endday:
            return f"SELECT * FROM {dbname} WHERE DATE({db_timecol}) >= DATE('{startday}')')"
        elif endday and not startday:
            return f"SELECT * FROM {dbname} WHERE DATE({db_timecol}) <= DATE('{endday}')"
        exit(1)
    else :
        if startday and endday:
            return f"SELECT * FROM {dbname} WHERE {db_daycol} >= '{startday}' AND {db_daycol} <= '{endday}'"
        elif startday and not endday:
            return f"SELECT * FROM {dbname} WHERE {db_daycol} >= '{startday}'"
        elif endday and not startday:
            return f"SELECT * FROM {dbname} WHERE {db_daycol} <= '{endday}'"
        exit(1)


def update_layout_cols(selcols):
    if len(selcols) > 0:
        yaxis_layout['title'] = selcols[0]
    if len(selcols) > 1:
        yaxis2_layout['title'] = selcols[1]
    if len(selcols) > 2:
        yaxis3_layout['title'] = selcols[2]
    if len(selcols) > 3:
        yaxis4_layout['title'] = selcols[3]


def get_range_picker(id):
    return dcc.DatePickerRange(
        id=id,
        # date=None,
        display_format='DD.MM.YYYY',  ## prend les dates seulement dayP -> assume partt les mm !!
        min_date_allowed=min(fetch_dayPdata_dates(dbDayP_name)),
        max_date_allowed=max(fetch_dayPdata_dates(dbDayP_name)),
        disabled_days=[pd.to_datetime(date).date() for date in
                       pd.date_range(start=min(fetch_dayPdata_dates(dbDayP_name)),
                                     end=max(fetch_dayPdata_dates(dbDayP_name))).
                       difference(pd.to_datetime(fetch_dayPdata_dates(dbDayP_name)))],
        minimum_nights=0,
        style={'display': 'none'}  # Initialement caché
    )


def get_period_dropdown(id):
    return dcc.Dropdown(
        id=id,
        options=[
            {'label': 'Jour', 'value': 'stat_day'},
            {'label': 'Semaine', 'value': 'stat_week'},
            {'label': 'Mois', 'value': 'stat_month'},
            {'label': 'Année', 'value': 'stat_year'},
            {'label': 'Tout', 'value': 'stat_all'},
            {'label': 'Personnalisé', 'value': 'stat_perso'}
        ],
        value='stat_day',
        placeholder="Période"
    )


def get_startrange_date(endd, period):
    if period == 'stat_week':
        return endd - timedelta(days=7)
    elif period == 'stat_month':
        return endd - timedelta(days=30)
    elif period == 'stat_year':
        return endd - timedelta(days=365)

# def insert_data(df):
#     """
#     Insert the data from the dataframe into the SQLite database.
#     """
#     conn = sqlite3.connect(db_file)
#     df.to_sql(dbTime_name, conn, if_exists='append', index=False)
#     conn.close()
#
