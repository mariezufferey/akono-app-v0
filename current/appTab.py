from settings import *
from utils_fcts import *
import plotly.express as px
from datetime import timedelta
import pandas as pd
import numpy as np
from dash import dash_table

## prend les dates seulement dayP -> assume partt les mm !!

dayPdata_columns = get_daydata_columns("P")
dayIdata_columns = get_daydata_columns("I")
timedata_columns = get_timedata_columns()
timecols2show = [x for x in timedata_columns if not showcols_settings[x] =="NA"]
dayPcols2show = [x for x in dayPdata_columns if not x == db_daycol]
dayIcols2show = [x for x in dayIdata_columns if not x == db_daycol]

tabname2tablab = dict()
tabname2tablab[dbTime_name] = "mesures minutées"
tabname2tablab[dbDayP_name] = "bilans journaliers P"
tabname2tablab[dbDayI_name] = "bilans journaliers I"

daysInDB_card = dbc.CardGroup(
    [
        dbc.Card(
            dbc.CardBody(
                [
                    html.H5("Contenu de la table des " + tabname2tablab[dbTime_name],
                            className="card-title"),
                    html.P(id='timeDB_content', className="card-text"),
                ]
            )
        ),
        dbc.Card(
            html.Div(className="fa fa-sun", style=card_icon),
            className="bg-warning",
            style={"maxWidth": 75},
        ),
    ],
    className="mt-4 shadow",
)

# Exemple de card2 ajoutée pour démonstration
card2 = dbc.CardGroup(
    [
        dbc.Card(
            dbc.CardBody(
                [
                    html.H5("Contenu de la table des " + tabname2tablab[dbDayP_name],
                                    className="card-title"),
                    html.P(id='dayPDB_content', className="card-text")
                ]
            )
        ),
        dbc.Card(
            html.Div(className="fa fa-bolt", style=card_icon),
            className="bg-info",
            style={"maxWidth": 75},
        ),
    ],
    className="mt-4 shadow",
)


# Exemple de card2 ajoutée pour démonstration
card3 = dbc.CardGroup(
    [
        dbc.Card(
            dbc.CardBody(
                [
                    html.H5("Contenu de la table des " + tabname2tablab[dbDayI_name],
                            className="card-title"),
                    html.P(id='dayIDB_content', className="card-text")
                ]
            )
        ),
        dbc.Card(
            html.Div(className="fa fa-plug", style=card_icon),
            className="bg-success",
            style={"maxWidth": 75},
        ),
    ],
    className="mt-4 shadow",
)
# Initialiser l'application Dash avec suppression des exceptions de callback
app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.BOOTSTRAP, FONT_AWESOME],
                suppress_callback_exceptions=True)

# Définir la mise en page de l'application
app.layout = html.Div([
    dcc.Tabs(id="tabs-example", value='tab-dashb', children=[ # value ici définit l'onglet par défaut
        dcc.Tab(label='Dashboard', value='tab-dashb',
                className='mytab', selected_className='mytab-slctd'),
        dcc.Tab(label='Données minutes', value='tab-timedata',
                    className='mytab', selected_className='mytab-slctd'),
        dcc.Tab(label='Données journalières', value='tab-daydata',
                className='mytab', selected_className='mytab-slctd'),
        dcc.Tab(label='Statistiques', value='tab-stat',
                className='mytab', selected_className='mytab-slctd'),
        dcc.Tab(label='Analyse (graphes)', value='tab-analyseGraph',
                className='mytab', selected_className='mytab-slctd'),
        dcc.Tab(label='Analyse (chiffres)', value='tab-analyseStat',
                className='mytab', selected_className='mytab-slctd'),

        # dcc.Tab(label='Graphe à choix', value='tab-sltdgraph',
        #         className='mytab', selected_className='mytab-slctd'),
        dcc.Tab(label='Gérer les données', value='tab-updateDB',
                className='mytab', selected_className='mytab-slctd'),
        dcc.Tab(label='Base de données', value='tab-showDB',
                className='mytab', selected_className='mytab-slctd')
    ]),
    ### le datepicker ne peut pas être placé dans render_content
# sinon le composant DatePickerSingle n'existe pas au moment où Dash essaie de
    # l'utiliser comme entrée dans le callback.
    # -> mettre DatePickerSingle présent dans le layout initial de l'application
    # même s'il n'est pas utilisé tout de suite.
    dcc.DatePickerSingle(
            id='date-picker-dbdata',
            date=None,
            display_format='DD.MM.YYYY',
            min_date_allowed=min(fetch_timedata_dates()),
            max_date_allowed=max(fetch_timedata_dates()),
            disabled_days = [pd.to_datetime(date).date() for date in
                         pd.date_range(start=min(fetch_timedata_dates()),
                                       end=max(fetch_timedata_dates())).
                         difference(pd.to_datetime(fetch_timedata_dates()))],
        style={'display': 'none'}  # Initialement caché
        # attention : pd.date_range(...).retourne un DatetimeIndex
        # pd.to_datetime pour convertir all_dates aussi en DatetimeIndex pr comparer
        ),
    dcc.DatePickerRange(
        id='range-picker-daydata',
        #date=None,
        display_format='DD.MM.YYYY',
        min_date_allowed=min(fetch_dayPdata_dates(dbDayP_name)),
        max_date_allowed=max(fetch_dayPdata_dates(dbDayP_name)),
        minimum_nights=0,
        disabled_days=[pd.to_datetime(date).date() for date in
                       pd.date_range(start=min(fetch_dayPdata_dates(dbDayP_name)),
                                     end=max(fetch_dayPdata_dates(dbDayP_name))).
                       difference(pd.to_datetime(fetch_dayPdata_dates(dbDayP_name)))],
        style={'display': 'none'}  # Initialement caché
        # attention : pd.date_range(...).retourne un DatetimeIndex
        # pd.to_datetime pour convertir all_dates aussi en DatetimeIndex pr comparer
    ),
    dcc.DatePickerRange(
        id='range-picker-stat',
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
    ),
    dcc.DatePickerRange(
        id='range-picker-analyseGraph',
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
    ),
    dcc.DatePickerRange(
        id='range-picker-analyseStat',
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
    ),
    html.Div(id='tabs-content'),
dcc.ConfirmDialog(
        id='confirm-dialog',
        message=popupmsg_maxvar
    ),
dcc.ConfirmDialog(
    id='confirm-dialog-stat',
    message=''
),dcc.ConfirmDialog(
    id='confirm-dialog-statgraph',
    message=''
),
dcc.ConfirmDialog(
    id='confirm-dialog-analyseGraph',
    message=''
),dcc.ConfirmDialog(
    id='confirm-dialog-analyseStat',
    message=''
),dcc.ConfirmDialog(
    id='confirm-dialog-daydataP',
    message=popupmsg_maxvar
),dcc.ConfirmDialog(
    id='confirm-dialog-daydataI',
    message=popupmsg_maxvar
)
])

# Callback to update the number of days in the database
@app.callback(
    Output('timeDB_content', 'children'),
Output('dayIDB_content', 'children'),
Output('dayPDB_content', 'children'),
    [Input('tabs-example', 'value')]
)
def update_days_count(tab):
    if tab == 'tab-dashb':
        all_entries = fetch_timedata_dates()
        all_days = set([
            datetime.strptime(x, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
            for x in all_entries
        ])
        num_days = len(all_days)

        conn = sqlite3.connect(db_file)
        query = f"SELECT * FROM {dbDayI_name}"
        dayI_df = pd.read_sql_query(query, conn)
        conn.close()
        num_daysI = len(set(dayI_df[db_daycol]))
        all_entriesP = fetch_dayPdata_dates(dbDayP_name)

        num_daysP = len(all_entriesP)

        chargeTotal_dayI = round(dayI_df[ahCharge_dayIcol + "_1"].fillna(0).sum(),2)
        dechargeTotal_dayI = round(dayI_df[ahDecharge_dayIcol + "_1"].fillna(0).sum(),2)
        rendementTot_dayI = round(dechargeTotal_dayI/chargeTotal_dayI*100,2)
        nCycles = round(chargeTotal_dayI/90)
        return (f'{num_days} jours',
                [f'{num_daysI} jours' ,
                 html.Br(),
                 html.B("Charge batterie total [Ah]")," (" + ahCharge_dayIcol  +") :\t" +\
                            str(chargeTotal_dayI),
                 html.Br(),
                html.B("Rendement batterie total [%]")," (" + ahDecharge_dayIcol  +"/" +\
                                ahCharge_dayIcol + ") :\t" +\
                                            str(rendementTot_dayI) + " %" ,
                 html.Br(),
                    html.B("# Cycles")," (" + ahCharge_dayIcol  +"/90) :\t" + \
                str(nCycles)],
                f'{num_daysP} jours')
    return "", "", ""

# Callback pour mettre à jour la visibilité du DatePickerSingle
@app.callback(
    Output('date-picker-dbdata', 'style'),
    [Input('tabs-example', 'value')]
)
def show_hide_timedatepicker(tab):
    if tab == 'tab-showDB':
        return {'display': 'block', 'margin': '20px 0'}  # Afficher le DatePickerSingle
    else:
        return {'display': 'none'}  # Cacher le DatePickerSingle

# Callback pour mettre à jour la visibilité du DatePickerSingle
@app.callback(
    Output('range-picker-daydata', 'style'),
    [Input('tabs-example', 'value')]
)
def show_hide_daydatepicker(tab):
    if tab == 'tab-daydata':
        return {'display': 'block', 'margin': '20px 0'}  # Afficher le DatePickerSingle
    else:
        return {'display': 'none'}  # Cacher le DatePickerSingle


# Callback pour mettre à jour la visibilité du DatePickerSingle
@app.callback(
    Output('range-picker-stat', 'style'),
    [Input('tabs-example', 'value')]
)
def show_hide_statdatepicker(tab):
    if tab == 'tab-stat':
        return {'display': 'block', 'margin': '20px 0'}  # Afficher le DatePickerSingle
    else:
        return {'display': 'none'}  # Cacher le DatePickerSingle

# Callback pour mettre à jour la visibilité du DatePickerSingle
# Modifier le callback pour afficher/cacher le DatePickerRange
@app.callback(
    Output('range-picker-analyseStat', 'style'),
    [Input('tabs-example', 'value')]
)
def show_hide_analyseStat_datepicker(tab):
    if tab == 'tab-analyseStat':
        return {'display': 'block', 'margin': '20px 0'}  # Afficher le DatePickerRange

    else:
        return {'display': 'none'}  # Cacher le DatePickerRange


######################################### CALL BACK tab analyse GRAPH

# Callback pour mettre à jour la visibilité du DatePickerSingle
# Modifier le callback pour afficher/cacher le DatePickerRange
@app.callback(
    Output('range-picker-analyseGraph', 'style'),
    [Input('tabs-example', 'value')]
)
def show_hide_analyseGraph_datepicker(tab):
    if tab == 'tab-analyseGraph':
        return {'display': 'block', 'margin': '20px 0'}  # Afficher le DatePickerRange
    else:
        return {'display': 'none'}  # Cacher le DatePickerRange


# Modifier le callback pour extraire les données ---- TAB ANALYSE GRAPHS


# # callback pour vérifier le nombre de variables sélectionnées et afficher la pop-up :
# callback pour vérifier le nombre de variables sélectionnées et afficher la pop-up :
@app.callback(
    [Output('confirm-dialog-daydataP', 'displayed'),
     Output('dayPdata-column-dropdown', 'value')],
    [Input('dayPdata-column-dropdown', 'value')]
)
def limit_selection_dayPdata(selected_columns):
    if len(selected_columns) >maxTimePlotVar :
        return True, selected_columns[:maxTimePlotVar]  # Afficher la pop-up et limiter la sélection à 2
    return False, selected_columns  # Ne pas afficher la pop-up
@app.callback(
    [Output('confirm-dialog-daydataI', 'displayed'),
     Output('dayIdata-column-dropdown', 'value')],
    [Input('dayIdata-column-dropdown', 'value')]
)
# # callback pour vérifier le nombre de variables sélectionnées et afficher la pop-up :
# callback pour vérifier le nombre de variables sélectionnées et afficher la pop-up :

def limit_selection_dayPdata(selected_columns):
    if len(selected_columns) >maxTimePlotVar :
        return True, selected_columns[:maxTimePlotVar]  # Afficher la pop-up et limiter la sélection à 2
    return False, selected_columns  # Ne pas afficher la pop-up

# Ajouter un callback pour mettre à jour la description - dayP data
@app.callback(
    Output('dayPdata-column-description', 'children'),
    [Input('dayPdata-column-dropdown', 'value')]
)
def update_dayP_description(selected_columns):
    if selected_columns:
        #print(';'.join(showcols_settings.keys()))
        desc_txt = '<br>'.join(["<b>"+selcol+"</b> : " +\
                                dayPcols_settings[selcol]['description']
                                for selcol in selected_columns])

        # xvar = selected_columns[0]  # On suppose que xvar est la première variable sélectionnée
        # description = showcols_settings.get(xvar, {}).get('description', 'No description available')
        return html.Div([dcc.Markdown(desc_txt, 
                                      dangerously_allow_html=True)])
    return html.P('No column selected')


# Ajouter un callback pour mettre à jour la description - dayP data
@app.callback(
    Output('dayIdata-column-description', 'children'),
    [Input('dayIdata-column-dropdown', 'value')]
)
def update_dayI_description(selected_columns):
    if selected_columns:
        #print(';'.join(showcols_settings.keys()))
        desc_txt = '<br>'.join(["<b>"+selcol+"</b> : " +\
                                dayIcols_settings[selcol]['description']
                                for selcol in selected_columns])

        # xvar = selected_columns[0]  # On suppose que xvar est la première variable sélectionnée
        # description = showcols_settings.get(xvar, {}).get('description', 'No description available')
        return html.Div([dcc.Markdown(desc_txt,
                                      dangerously_allow_html=True)])
    return html.P('No column selected')


@app.callback(
    [
        Output('analyseGraph-pie-chart-global', 'children'),
        Output('analyseGraph-pie-chart-day', 'children'),
        Output('analyseGraph-pie-chart-night', 'children'),
        Output('analyseGraph-period-subtit', 'children'),
        Output('analyseGraph-pie-chart-tit', 'children'),
        Output('analyseGraph-tempbat-barplot', 'children'),
        Output('confirm-dialog-analyseGraph', 'displayed'),
        Output('confirm-dialog-analyseGraph', 'message')
    ],
    [Input('show-asGraph-btn', 'n_clicks')],
    [
        State('asGraphPeriod-dropdown', 'value'),
            State('asL-dropdown', 'value'),
        State('range-picker-analyseGraph', 'start_date'),
        State('range-picker-analyseGraph', 'end_date')
    ]
)
def update_analyse_pie_chart(n_clicks, selected_period, selected_L, start_date, end_date):
    if n_clicks is None or n_clicks == 0:
        return "","","", "","", "", False, ""
    if selected_period != 'as_all' and (not start_date or not end_date):
        return "","","", "","","", True, "Sélectionnez une période"

    if selected_period != 'as_all':
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        if selected_period in ['as_day', 'as_week', 'as_month', 'as_year']:
            if start_date != end_date:
                return  "","","", "","", "", True, "Choisir une seule date dans une modal pop-up"
            if selected_period == 'as_week':
                start_date = end_date - timedelta(days=7)
            elif selected_period == 'as_month':
                start_date = end_date - timedelta(days=30)
            elif selected_period == 'as_year':
                start_date = end_date - timedelta(days=365)

        if selected_period == 'as_perso' and start_date == end_date:
            return "","","", "","", "",True, "Choisir une date différente"

    # Extraire les données pour l'intervalle sélectionné
    conn = sqlite3.connect(db_file)
    if selected_period == 'as_all':
        query = f"SELECT * FROM {dbTime_name}"
        interval_txt = " (tout)"
        interval_txt = " Toutes les données"
    else:
        query = get_query_extractInterval(dbTime_name, start_date, end_date)
        # interval_txt = ("(" + start_date.strftime('%d/%m/%Y') +" - " +
        #                 end_date.strftime('%d/%m/%Y') + ")")
        interval_txt = ("Période : " + start_date.strftime('%d/%m/%Y') + " - " +
                        end_date.strftime('%d/%m/%Y') )
    df = pd.read_sql_query(query, conn)
    conn.close()
    if selected_L == "as_L1":
        df['calc_col'] = df[xtfincol + '_L1']
        calcol_txt = xtfincol + '_L1'
    elif selected_L == "as_L2":
        df['calc_col'] = df[xtfincol + '_L2']
        calcol_txt = xtfincol + '_L2'
    elif selected_L == "as_both":
        df['calc_col'] = df[xtfincol + '_L1'] + df[xtfincol + '_L2']
        calcol_txt = xtfincol + '_L1' + "+" + xtfincol + '_L2'
    else:
        exit(1)

    pie_chart_tit = html.Div([
        html.H4("Répartition fréquences (" + calcol_txt+")"),
        html.H6("(génératrice si > " + str(xtfin_genThresh) +
                " ; ni gén. ni rés. si = " + str(xtfin_nosource) + ")")
        
    ])

    period_subtit = html.H6(interval_txt)

        # Ajouter la colonne 'freq_type'
    df['freq_type'] = np.where(df['calc_col'] > xtfin_genThresh,
                               "génératrice", "réseau")
    df.loc[df['calc_col'] == xtfin_nosource, 'freq_type'] = "ni gén. ni rés."

    # Calculer les pourcentages
    freq_counts = df['freq_type'].value_counts(normalize=True) * 100

    fig_global = px.pie(
        names=freq_counts.index,
        values=freq_counts.values,
        # title="Répartition des fréquences " + interval_txt + " (Global)"
        title = "Global"
    )

    # Filtrer les données de jour (08:00 - 18:00)
    df_day = df[(pd.to_datetime(df[db_timecol]).dt.time >= datetime.strptime("08:00", "%H:%M").time()) &
                (pd.to_datetime(df[db_timecol]).dt.time < datetime.strptime("18:00", "%H:%M").time())]

    # Calculer les pourcentages pour le graphique de jour
    freq_counts_day = df_day['freq_type'].value_counts(normalize=True) * 100

    # Créer le graphique circulaire de jour
    fig_day = px.pie(
        names=freq_counts_day.index,
        values=freq_counts_day.values,
        # title="Répartition des fréquences "  + interval_txt + " (Jour : 08:00 - 18:00)",
        title="Jour : 08:00 - 18:00"
    )

    # Filtrer les données de nuit (18:00 - 08:00)
    df_night = df[(pd.to_datetime(df[db_timecol]).dt.time >= datetime.strptime("18:00", "%H:%M").time()) |
                  (pd.to_datetime(df[db_timecol]).dt.time < datetime.strptime("08:00", "%H:%M").time())]

    assert df.shape[0] == (df_night.shape[0]+df_day.shape[0])

    # Calculer les pourcentages pour le graphique de nuit
    freq_counts_night = df_night['freq_type'].value_counts(normalize=True) * 100

    # Créer le graphique circulaire de nuit
    fig_night = px.pie(
        names=freq_counts_night.index,
        values=freq_counts_night.values,
        # title="Répartition des fréquences " +  interval_txt + " (Nuit : 18:00 - 08:00)"
        title="Nuit : 18:00 - 08:00"
    )

    #### calcul des moyennes températures batterie
    mean_global = df[tempTbatcol].mean()
    mean_day = df_day[tempTbatcol].mean()
    mean_night = df_night[tempTbatcol].mean()

    barplot_data = pd.DataFrame({
        'Période': ['Global', 'Jour', 'Nuit'],
        'Moyenne Temp': [mean_global, mean_day, mean_night]
    })

    fig_barplot = px.bar(barplot_data, x='Période', y='Moyenne Temp', title='Moyenne de TempTbatcol')

    return [dcc.Graph(figure=fig_global),
            dcc.Graph(figure=fig_day),
            dcc.Graph(figure=fig_night),
            period_subtit,
            pie_chart_tit,
            dcc.Graph(figure=fig_barplot),
            False, ""]

######################################### CALL BACK tab analyse GRAPH
# Modifier le callback pour extraire les données ---- TAB ANALYSE - STAT
@app.callback(
    [
         Output('analyseStat-period-subtit', 'children'),
        Output('analyseStat-tableMean', 'children'),
Output('analyseStat-tableMax', 'children'),
Output('analyseStat-tableSum', 'children'),
        Output('analyseStat-period-hourtxt', 'children'),
Output('analyseStat-tableSumByHour', 'children'),
        Output('confirm-dialog-analyseStat', 'displayed'),
        Output('confirm-dialog-analyseStat', 'message')
    ],
    [Input('show-asStat-btn', 'n_clicks')],
    [
        State('asStatPeriod-dropdown', 'value'),

        State('range-picker-analyseStat', 'start_date'),
        State('range-picker-analyseStat', 'end_date')
    ]
)
def update_analyse_stat(n_clicks, selected_period, start_date, end_date):
    if n_clicks is None or n_clicks == 0:
        return *[""] * 6, False, ""
    if selected_period != 'as_all' and (not start_date or not end_date):
        return *[""] * 6, True, "Sélectionnez une période"

    if selected_period != 'as_all':
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        if selected_period in ['as_day', 'as_week', 'as_month', 'as_year']:
            if start_date != end_date:
                return  *[""] * 6,True, "Choisir une seule date dans une modal pop-up"
            if selected_period == 'as_week':
                start_date = end_date - timedelta(days=7)
            elif selected_period == 'as_month':
                start_date = end_date - timedelta(days=30)
            elif selected_period == 'as_year':
                start_date = end_date - timedelta(days=365)

        if selected_period == 'as_perso' and start_date == end_date:
            return *[""] * 6,True, "Choisir une date différente"

    # Extraire les données pour l'intervalle sélectionné
    conn = sqlite3.connect(db_file)
    if selected_period == 'as_all':
        query = f"SELECT * FROM {dbTime_name}"
        interval_txt = " (tout)"
        interval_txt = " Toutes les données"
    else:
        query = get_query_extractInterval(dbTime_name, start_date, end_date)
        interval_txt = ("Période : " + start_date.strftime('%d/%m/%Y') + " - " +
                        end_date.strftime('%d/%m/%Y') )
    all_df = pd.read_sql_query(query, conn)
    conn.close()

    puicol_tot = xtpuicol_L1+"+"+xtpuicol_L2
    all_df[puicol_tot] = all_df[xtpuicol_L1] + all_df[xtpuicol_L2]

    df = all_df[[db_timecol,puicol_tot, xtpuicol_L1, xtpuicol_L2]].copy()
    df.loc[:, 'catTime'] = np.where(
        (pd.to_datetime(df[db_timecol]).dt.time >=
                        datetime.strptime("08:00", "%H:%M").time()) &
        (pd.to_datetime(df[db_timecol]).dt.time <
                        datetime.strptime("18:00", "%H:%M").time()),
        "Jour",
        "Nuit"
    )
    time_df = df[['catTime',puicol_tot, xtpuicol_L1, xtpuicol_L2]].copy()
    tot_df = df[[puicol_tot, xtpuicol_L1, xtpuicol_L2]].copy()

    catTime_counts = time_df['catTime'].value_counts().reset_index()
    #VRAI si 1 jour sélectionné
    if selected_period =='as_day' :
        assert (catTime_counts.loc[catTime_counts['index'] == 'Nuit', 'catTime'] == 840).all()
        assert (catTime_counts.loc[catTime_counts['index'] == 'Jour', 'catTime'] == 600).all()

    maxCat_df = time_df.groupby('catTime').max().reset_index()
    maxTot_df = tot_df.max().to_frame().T
    maxTot_df['catTime'] = "Total"
    assert set(maxCat_df.columns) == set(maxTot_df.columns)
    max_df = pd.concat([maxCat_df, maxTot_df[maxCat_df.columns]], ignore_index=True)
    max_df.columns =  max_df.columns.str.replace(xtpuicol+"_", "", regex=False)
    max_df.columns = max_df.columns.str.replace("catTime", "Type")


    meanCat_df = time_df.groupby('catTime').mean().reset_index()
    meanTot_df = tot_df.mean().to_frame().T
    meanTot_df['catTime'] = "Total"
    assert set(meanCat_df.columns) == set(meanTot_df.columns)
    mean_df = pd.concat([meanCat_df, meanTot_df[meanCat_df.columns]], ignore_index=True)
    mean_df.columns =  mean_df.columns.str.replace(xtpuicol+"_", "", regex=False)
    mean_df.columns = mean_df.columns.str.replace("catTime", "Type")

    sumCat_df = time_df.groupby('catTime').sum().reset_index()
    sumTot_df = tot_df.sum().to_frame().T
    sumTot_df['catTime'] = "Total"
    assert set(sumCat_df.columns) == set(sumTot_df.columns)
    sum_df = pd.concat([sumCat_df, sumTot_df[sumCat_df.columns]], ignore_index=True)
    sum_df.columns =  sum_df.columns.str.replace(xtpuicol+"_", "", regex=False)
    sum_df.columns = sum_df.columns.str.replace("catTime", "Type")

    nHoursTot = pd.to_datetime(df[db_timecol]).dt.floor('H').nunique()
    nHoursTot_df = pd.DataFrame({'catTime': ['Total'], 'time': [nHoursTot]})
    nHours_catTime_df = df.groupby('catTime')[db_timecol].apply(
                  lambda x: pd.to_datetime(x).dt.floor('H').nunique()).reset_index()
    assert set(nHoursTot_df.columns) == set(nHours_catTime_df.columns)
    nh_df = pd.concat([nHours_catTime_df[nHoursTot_df.columns],nHoursTot_df],
                       ignore_index=True)
    nh_df.columns = nh_df.columns.str.replace("catTime", "Type")

    hours_txt = "# heures : "
    hours_txt  += "; ".join([f"{row['Type']} = {row['time']}" for
                        _, row in nh_df.iterrows()])

    sumByHour_df = sum_df.copy()
    for cat_time in nh_df['Type']:
        sumByHour_df.loc[sumByHour_df['Type'] == cat_time, ['L1_1+L2_2', 'L1_1', 'L2_2']] /= \
                         nh_df.loc[nh_df['Type'] == cat_time, db_timecol].values[0]

    period_subtit = html.H6(interval_txt)

    table_mean = dash_table.DataTable(
        data=mean_df.round(2).to_dict('records'),
        columns=[{'name': col, 'id': col} for col in mean_df.columns],
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left', 'whiteSpace': 'normal'},
        style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
        style_cell_conditional=[
            {'if': {'column_id': c}, 'border': '1px solid black',
             'minWidth': '5px', 'maxWidth': '100px'} for c in
            mean_df.columns
        ],
        fill_width=False
    )

    table_sum = dash_table.DataTable(
        data=sum_df.round(2).to_dict('records'),
        columns=[{'name': col, 'id': col} for col in sum_df.columns],
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left', 'whiteSpace': 'normal'},
        style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
        style_cell_conditional=[
            {'if': {'column_id': c}, 'border': '1px solid black',
             'minWidth': '5px', 'maxWidth': '100px'} for c in
            sum_df.columns
        ],
        fill_width=False
    )

    table_sumByHour = dash_table.DataTable(
        data=sumByHour_df.round(2).to_dict('records'),
        columns=[{'name': col, 'id': col} for col in sumByHour_df.columns],
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left', 'whiteSpace': 'normal'},
        style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
        style_cell_conditional=[
            {'if': {'column_id': c}, 'border': '1px solid black',
             'minWidth': '5px', 'maxWidth': '100px'} for c in
            sumByHour_df.columns
        ],
        fill_width=False
    )

    table_max = dash_table.DataTable(
        data=max_df.round(2).to_dict('records'),
        columns=[{'name': col, 'id': col} for col in max_df.columns],
    style_table={'overflow':'scroll'},
    style_header={'backgroundColor':'#305D91','padding':'10px','color':'#FFFFFF'},
    style_cell={'textAlign':'center','minWidth': '5px',
                'maxWidth': '100px',# 'width': 25,
                #'font_size': '12px',
                'whiteSpace':'normal','height':'auto'},
    editable=True,              # allow editing of data inside all cells
    filter_action="native",     # allow filtering of data by user ('native') or not ('none')
    sort_action="native",       # enables data to be sorted per-column by user or not ('none')
    sort_mode="single",         # sort across 'multi' or 'single' columns
    column_selectable="multi",  # allow users to select 'multi' or 'single' columns
    row_selectable="multi",     # allow users to select 'multi' or 'single' rows
    row_deletable=True,         # choose if user can delete a row (True) or not (False)
    selected_columns=[],        # ids of columns that user selects
    selected_rows=[],           # indices of rows that user selects
    page_action="native",
    fill_width=False)

    return [
        period_subtit,
        table_mean,
        table_max,
        table_sum,
        hours_txt,
        table_sumByHour,
        False, ""
    ]

# #################################333 CALL BACKS dayDATA STAT
@app.callback(
    [
     Output('daydata-range-infoStat', 'children'),
        Output('analyseStat-tableDay', 'children')
    ],
    [Input('show-daystat-btn', 'n_clicks')],
    [
     State('range-picker-daydata', 'start_date'),
     State('range-picker-daydata', 'end_date')]
)
def update_day_range_stat(n_clicks, start_date, end_date):
    if n_clicks is None  or not start_date or not end_date:
        return "", ""
    # Production solaire du jour (I11007) [kW]
    # Energie (bilan) sur l'entrée des 2 XT  (somme L1 * L2 I3081)
    # Energie (bilan) sur les sorties des 2 XT (somme L1 * L2 I3083)
    conn = sqlite3.connect(db_file)

    all_cols1 = [x+"_1" for x in dayStat_cols]
    all_cols2 = [x + "_2" for x in dayStat_cols]
    all_cols = all_cols1+all_cols2

    queryI = (f"SELECT " + db_daycol+
             f", {', '.join(all_cols)}"
             f" FROM {dbDayI_name} WHERE " +
                          db_daycol + f" >= '{start_date}' AND " +
                                        db_daycol + f" <= '{end_date}'")
    dfI = pd.read_sql_query(queryI, conn)
    conn.close()

    dfI.fillna(0, inplace=True) ### TODO -> VERIFIER SI OK avec CR !!!!

    dayStat_newcols = []
    for statcol in dayStat_cols:

        newcol = dayIcols_settings[statcol]["description"]  +\
                            " (" + statcol + ")"
        dfI[newcol] = (
            dfI[statcol+"_1"]+dfI[statcol+"_2"])
        dayStat_newcols += [newcol]

    print(','.join(dayStat_cols))
    print(','.join(dayStat_newcols))

    diffBilan_newcol = "Bilan charge-décharge (" +\
                    ahCharge_dayIcol+"-"+ahDecharge_dayIcol+")"
    dfI[diffBilan_newcol] = (dfI[ahCharge_dayIcol+"_1"] - ### ATTEnTION ICI PREND 1 !!
                             dfI[ahDecharge_dayIcol+"_1"])

    date_info = f"Données du {start_date} au {end_date}"
    print(','.join(dfI.columns))

    sub_df = dfI[[db_daycol]+dayStat_newcols]

    print(','.join(sub_df.columns))

    table_dayIstat = dash_table.DataTable(
        data=sub_df.round(2).to_dict('records'),
        columns=[{'name': col, 'id': col} for col in sub_df.columns],
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left', 'whiteSpace': 'normal'},
        style_header={'backgroundColor': 'rgb(230, 230, 230)', 'fontWeight': 'bold'},
        style_cell_conditional=[
            {'if': {'column_id': c}, 'border': '1px solid black',
             'minWidth': '5px', 'maxWidth': '200px'} for c in
            sub_df.columns
        ],
        fill_width=False
    )
    return date_info, table_dayIstat

# #################################333 CALL BACKS dayDATA GRAPH
@app.callback(
    [
        Output('dayP-series-graph', 'figure'),
        Output('dayI-series-graph', 'figure'),
     Output('daydata-range-infoGraph', 'children')
    ],
    [Input('show-daygraph-btn', 'n_clicks')],
    [State('dayPdata-column-dropdown', 'value'),
    State('dayIdata-column-dropdown', 'value'),
     State('range-picker-daydata', 'start_date'),
     State('range-picker-daydata', 'end_date')]
)
def update_day_range_graph(n_clicks, selcols_dayP, selcols_dayI, start_date, end_date):
    if n_clicks is None or (not selcols_dayP and not selcols_dayI) or not start_date or not end_date:
        return go.Figure(), go.Figure(), ""

    conn = sqlite3.connect(db_file)
    if selcols_dayP :
        queryP = (f"SELECT " + db_daycol+
                 f", {', '.join(selcols_dayP)} FROM {dbDayP_name} WHERE " +
                              db_daycol + f" >= '{start_date}' AND " +
                                            db_daycol + f" <= '{end_date}'")
        dfP = pd.read_sql_query(queryP, conn)

    if selcols_dayI :
        queryI = (f"SELECT " + db_daycol+
                 f", {', '.join(selcols_dayI)} FROM {dbDayI_name} WHERE " +
                              db_daycol + f" >= '{start_date}' AND " +
                                            db_daycol + f" <= '{end_date}'")
        dfI = pd.read_sql_query(queryI, conn)

    conn.close()

    figP = go.Figure()
    figI = go.Figure()

    if selcols_dayP:
        for i, col in enumerate(selcols_dayP):
            print(type(dfP[col][0]))
            print(dfP[db_daycol][0])
            #dfP.to_excel('test_data.xlsx')
            # Ajout de chaque variable sur un axe y différent
            figP.add_trace(
                go.Scatter(
                    x=dfP[db_daycol],
                    y=dfP[col],
                    name=col,
                    yaxis=f'y{i + 1}'
                )
            )
        update_layout_cols(selcols_dayP)
        figP.update_layout(
            xaxis=dict(domain=[0.25, 0.75], showline=True,
                       linewidth=2, linecolor='black'),
            yaxis=yaxis_layout,
            yaxis2=yaxis2_layout,
            yaxis3=yaxis3_layout,
            yaxis4=yaxis4_layout,
            title_text="",
            margin=dict(l=40, r=40, t=40, b=30)
        )
    if selcols_dayI:
        for i, col in enumerate(selcols_dayI):
            print(type(dfI[col][0]))
            print(dfI[db_daycol][0])
            #dfI.to_excel('test_data.xlsx')
            # Ajout de chaque variable sur un axe y différent
            figI.add_trace(
                go.Scatter(
                    x=dfI[db_daycol],
                    y=dfI[col],
                    # mode='lines',
                    # connectgaps=True,
                    name=col,
                    yaxis=f'y{i + 1}'
                )
            )
        update_layout_cols(selcols_dayI)
        figI.update_layout(
            xaxis=dict(domain=[0.25, 0.75], showline=True, linewidth=2, linecolor='black'),
            yaxis=yaxis_layout,
            yaxis2=yaxis2_layout,
            yaxis3=yaxis3_layout,
            yaxis4=yaxis4_layout,
            title_text="",
            margin=dict(l=40, r=40, t=40, b=30)
        )
    date_info = f"Données du {start_date} au {end_date}"
    return figP, figI, date_info

##############################3# CALL BACKS STAT tab
import pandas as pd
from datetime import datetime, timedelta

@app.callback(
    [
        Output('stat-range-info', 'children'),
        Output('confirm-dialog-stat', 'displayed'),
        Output('confirm-dialog-stat', 'message'),
        Output('stat-means-info', 'children')
    ],
    [Input('show-stat-btn', 'n_clicks')],
    [
        State('statperiod-dropdown', 'value'),
        State('range-picker-stat', 'start_date'),
        State('range-picker-stat', 'end_date')
    ]
)
def update_stat_values(n_clicks, selected_period, start_date, end_date):
    if n_clicks is None or n_clicks==0:
        return ["", False, "", ""]
    if not start_date or not end_date:
        return ["", True, "Sélectionnez une période", ""]

    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

    if selected_period in ['stat_day', 'stat_week', 'stat_month', 'stat_year']:
        if start_date != end_date:
            return ["ERREUR", True, "Choisir une seule date dans une modal pop-up", ""]
        if selected_period == 'stat_week':
            start_date = end_date - timedelta(days=7)
        elif selected_period == 'stat_month':
            start_date = end_date - timedelta(days=30)
        elif selected_period == 'stat_year':
            start_date = end_date - timedelta(days=365)

    if selected_period == 'stat_perso' and start_date == end_date:
        return ["ERREUR", True, "Choisir une date différente", ""]

    # Extraire les données pour l'intervalle sélectionné
    conn = sqlite3.connect(db_file)

    #query_time = f"SELECT * FROM {dbTime_name} WHERE DATE({db_timecol}) >= DATE('{start_date}') AND DATE({db_timecol}) <= DATE('{end_date}')"
    query_time = get_query_extractInterval(dbTime_name, start_date, end_date)
    df_time = pd.read_sql_query(query_time, conn)

    # query_dayP = f"SELECT * FROM {dbDayP_name} WHERE {db_daycol} >= '{start_date}' AND {db_daycol} <= '{end_date}'"
    query_dayP = get_query_extractInterval(dbDayP_name, start_date, end_date)
    df_dayP = pd.read_sql_query(query_dayP, conn)

    # query_dayI = f"SELECT * FROM {dbDayI_name} WHERE {db_daycol} >= '{start_date}' AND {db_daycol} <= '{end_date}'"
    query_dayI = get_query_extractInterval(dbDayI_name, start_date, end_date)
    df_dayI = pd.read_sql_query(query_dayI, conn)

    conn.close()

    # Calculer les moyennes
    means_time = df_time.mean(numeric_only=True)
    means_dayP = df_dayP.mean(numeric_only=True)
    means_dayI = df_dayI.mean(numeric_only=True)

    # Fonction pour diviser une liste en N parties égales
    def split_list(lst, n):
        k, m = divmod(len(lst), n)
        return [lst[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]

    # Organiser les données en sections avec trois colonnes
    def create_section(title, data):
        items = [html.P([html.U(col), f": {mean:.2f}"]) for col, mean in data.items()]
        columns = split_list(items, 3)
        return html.Div([
            html.H5(title, style={'font-weight': 'bold'}),
            html.Div([html.Div(col, className='col') for col in columns], className='row')
        ])

    means_html = html.Div([
        create_section("Moyennes des données minutes", means_time),
        create_section("Moyennes des données journalières (P)", means_dayP),
        create_section("Moyennes des données journalières (I)", means_dayI)
    ])

    date_info = f"Données du {start_date} au {end_date}"
    return [date_info, False, "", means_html]


################################ CALLBACKS - TAB update & show DB - màj datepicker upload/delete

# Callback pour mettre à jour la liste des dates après l'upload
# ou la suppression de données
@app.callback(
    [
    Output('date-picker-dbdata', 'min_date_allowed'),
     Output('date-picker-dbdata', 'max_date_allowed'),
     Output('date-picker-dbdata', 'disabled_days'),
        Output('date-picker-delete', 'min_date_allowed'),
        Output('date-picker-delete', 'max_date_allowed'),
        Output('date-picker-delete', 'disabled_days'),
     ],
    [Input('output-upload', 'children'),
     Input('output-delete', 'children')]
)
# *_ : convention pour indiquer que la fonction peut accepter un nombre arbitraire
# d'arguments, mais que ces arguments ne seront pas utilisés dans la fonction.
# comme *args pour ombre variable d'arguments positionnels (ici nom de variable _)

def update_all_dates(*_):
    all_dates = fetch_timedata_dates()
    min_date_allowed = min(all_dates)
    max_date_allowed = max(all_dates)
    disabled_days = [pd.to_datetime(date).date() for date in
                     pd.date_range(start=min_date_allowed, end=max_date_allowed).
                     difference(pd.to_datetime(all_dates))]
    #print('disabled Days = ' + ','.join(disabled_days))
    return (min_date_allowed, max_date_allowed, 
            disabled_days,min_date_allowed, 
            max_date_allowed, disabled_days)

################################ CALLBACKS - TAB STAT - VISUALISATION

# Callback pour mettre à jour les colonnes disponibles en fonction de la table sélectionnée :

@app.callback(
    Output('tabstatgraph-col', 'options'),
    [Input('tabstatgraph-db', 'value')]
)
def update_columns(selected_db):
    if selected_db:
        if selected_db == dbTime_name:
            columns = [{'label': col, 'value': col} for col in timecols2show]
        elif selected_db == dbDayP_name:
            columns = [{'label': col, 'value': col} for col in dayPcols2show]
        elif selected_db == dbDayI_name:
            columns = [{'label': col, 'value': col} for col in dayI_cols+dayIcols2show]
        return columns
    return []

# Callback pour mettre à jour texte info var

@app.callback(
    Output('tabstatgraph-varinfo', 'children'),
    [Input('tabstatgraph-col', 'value')],
    [State('tabstatgraph-db', 'value')]
)
def update_statvarinfo(selected_col, selected_db):
    if selected_col and selected_db:

        if selected_db == dbTime_name:
            desc_txt = "<b>" + selected_col + "</b> : " +\
                                    showcols_settings[selected_col]['description']

        elif selected_db == dbDayP_name:
            desc_txt = "<b>" + selected_col + "</b> : " +\
                                    dayPcols_settings[selected_col]['description']

        elif selected_db == dbDayI_name:
            desc_txt = "<b>" + selected_col + "</b> : " +\
                                    dayIcols_settings[selected_col]['description']

        else:
            return None
        return html.Div([dcc.Markdown(desc_txt,
                                      dangerously_allow_html=True)])
    return None

# Callback pour afficher le graphique en fonction de la sélection :
@app.callback(
    [Output('stat-graph', 'figure'),
     Output('confirm-dialog-statgraph', 'displayed'),
     Output('confirm-dialog-statgraph', 'message')],
     [Input('show-statgraph-btn', 'n_clicks')],
    [State('tabstatgraph-db', 'value'),
     State('tabstatgraph-col', 'value'),
     State('tabstatgraph-viz', 'value'),
     State('range-picker-stat', 'start_date'),
     State('range-picker-stat', 'end_date')]
)
def display_graph(n_clicks, selected_db, selected_col, selected_viz, start_date, end_date):
    if n_clicks is None or n_clicks==0:
        return [go.Figure(),False, ""]
    if (not selected_db or not selected_col or not selected_viz) and (not start_date or not end_date):
        return [go.Figure(),True, "Sélectionnez des données et une période"]

    if not selected_db or not selected_col or not selected_viz:
        return [go.Figure(),True, "Sélectionnez des données"]

    if not start_date or not end_date:
        return [go.Figure(), True, "Sélectionnez une période"]

    conn = sqlite3.connect(db_file)
    query = get_query_extractInterval(selected_db, start_date, end_date)

    #query = f"SELECT {db_daycol}, {selected_col} FROM {selected_db} WHERE {db_daycol} >= '{start_date}' AND {db_daycol} <= '{end_date}'"
    df = pd.read_sql_query(query, conn)
    conn.close()

    if selected_db == dbTime_name:
        xcol = db_timecol
    else:
        xcol = db_daycol
        if selected_db == dbDayI_name:
            for col in dayI_cols:
                df[col] = df[col+"_1"].fillna(0) +  df[col+"_2"].fillna(0)

    if selected_db == dbTime_name and selected_viz == 'boxplot':
        df['date'] = pd.to_datetime(df[xcol]).dt.date
        fig = px.box(df, x='date', y=selected_col, title=f'{selected_col} Box Plot par jour')
    else :
        if selected_viz == 'lineplot':
            fig = px.line(df, x=xcol, y=selected_col, title=f'{selected_col} Line Plot')
        elif selected_viz == 'barplot':
            fig = px.bar(df, x=xcol, y=selected_col, title=f'{selected_col} Bar Plot')
        elif selected_viz == 'boxplot':
            fig = px.box(df, x=xcol, y=selected_col, title=f'{selected_col} Box Plot')

    if (selected_db == dbTime_name and selected_viz == 'boxplot') or (selected_db == dbDayP_name or selected_db == dbDayI_name ):
        fig.update_layout(xaxis=dict(title='Date', tickformat='%Y-%m-%d', dtick="D1"))
    return [fig, False, ""]

@app.callback(
    Output('tabstatgraph-viz', 'options'),
    [Input('tabstatgraph-db', 'value')]
)
def update_viz_options(selected_db):
    if selected_db == dbTime_name:
        return [
            {'label': 'Line Plot', 'value': 'lineplot'},
            {'label': 'Bar Plot', 'value': 'barplot'},
            {'label': 'Box Plot', 'value': 'boxplot'}
        ]
    else:
        return [
            {'label': 'Line Plot', 'value': 'lineplot'},
            {'label': 'Bar Plot', 'value': 'barplot'}
        ]
################################ CALLBACKS - TAB 3 - GESTION DES DONNÉEs
### callback pour l'upload de nouvelles données
@app.callback(
    Output('output-upload', 'children'),
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename'),
     State('upload-data', 'last_modified')]
)
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n) for c, n in zip(list_of_contents, list_of_names)
        ]
        return children

# callback pour supprimer les données en fonction de la date
@app.callback(
    Output('output-delete', 'children'),
    [Input('delete-button', 'n_clicks')],
    [State('date-picker-delete', 'date')]
)
def delete_data(n_clicks, date):
    if n_clicks and date:
        conn = sqlite3.connect(db_file)
        c = conn.cursor()
        c.execute("DELETE FROM " + dbTime_name + " WHERE " + db_timecol + f" LIKE '{date}%'")
        conn.commit()
        conn.close()
        return html.Div(['Successfully deleted data for date: {}'.format(date)])
    return html.Div()
################################ CALLBACKS - TAB TIMEDATA - GRAPHIQUES TEMPORELS DONNEES HORAIRES
@app.callback(
    Output('time-series-graph', 'figure'),
    [Input('timedata-column-dropdown', 'value')]
)
def update_graph(selected_columns):
    if not selected_columns:
        return go.Figure()

    # Lire toutes les données de la base de données
    df = fetch_timedata()

    fig = go.Figure()

    for i, col in enumerate(selected_columns):
        # Ajout de chaque variable sur un axe y différent
        fig.add_trace(
            go.Scatter(
                x=df[db_timecol],
                y=df[col],
                mode='lines',
                name=col,
                yaxis=f'y{i + 1}'
            )
        )
    update_layout_cols(selected_columns)
    fig.update_layout(
        xaxis=dict(domain=[0.25, 0.75], showline=True, linewidth=2, linecolor='black'),
        yaxis=yaxis_layout,
        yaxis2=yaxis2_layout,
        yaxis3=yaxis3_layout,
        yaxis4=yaxis4_layout,
        title_text="", ## titre en-haut à gauche
        margin=dict(l=40, r=40, t=40, b=30)
    )
    return fig

# callback pour vérifier le nombre de variables sélectionnées et afficher la pop-up :
@app.callback(
    [Output('confirm-dialog', 'displayed'),
     Output('timedata-column-dropdown', 'value')],
    [Input('timedata-column-dropdown', 'value')]
)
def limit_selection_timedata(selected_columns):
    if len(selected_columns) >maxTimePlotVar :
        return True, selected_columns[:maxTimePlotVar]  # Afficher la pop-up et limiter la sélection à 2
    return False, selected_columns  # Ne pas afficher la pop-up

# Ajouter un callback pour mettre à jour la description
@app.callback(
    Output('timedata-column-description', 'children'),
    [Input('timedata-column-dropdown', 'value')]
)
def update_description(selected_columns):
    if selected_columns:
        desc_txt = '<br>'.join(["<b>"+selcol+"</b> : " + showcols_settings[selcol]['description']
                                for selcol in selected_columns])
        return html.Div([dcc.Markdown(desc_txt,
                                      dangerously_allow_html=True)])

    return html.P('No column selected')

############################################## MAIN CALLBACK RENDER_CONTENT

# Callback pour mettre à jour le contenu des onglets
# NB : component_property ne peut pas être choisi librement !!
@app.callback(
    Output('tabs-content', 'children'),
    [Input('tabs-example', 'value'),
     Input('date-picker-dbdata', 'date')
     ]
)
def render_content(tab, picked_date):
    if tab == 'tab-dashb':
        # return days_success_card_body
        # md = medium devices
        # md=4 signifie que cette colonne occupera 4 des 12 colonnes disponibles sur les
        return dbc.Container(dbc.Row(dbc.Col([daysInDB_card,
                                              card2, card3], md=10)))
    elif tab == 'tab-timedata':
        return html.Div([
            html.H3('Données minutes'),
            # checkboxes,
            dcc.Dropdown(
                id='timedata-column-dropdown',
                options=[{'label': col, 'value': col} for col in timecols2show],
                value=[],
                multi=True,
                placeholder="Sélectionnez des variables"
            ),
            html.Div(id='timedata-column-description'),
            dcc.Graph(id='time-series-graph')
        ])
    elif tab == 'tab-daydata':
        return html.Div([
            html.H3('Données journalières'),
            html.H4('Statistiques'),
            html.Button('Afficher (stat.)', id='show-daystat-btn', n_clicks=0),
            html.Div(id='daydata-range-infoStat', style={'marginTop': '20px'}),
            html.Div(id='analyseStat-tableDay', children=""),
            html.H4('Graphiques'),
            html.Button('Afficher (graphiques)', id='show-daygraph-btn', n_clicks=0),
            html.Div(id='daydata-range-infoGraph', style={'marginTop': '20px'}),
            html.H5('Valeurs P'),
            html.Div(id='dayPdata-column-description'),
            dcc.Dropdown(
                id='dayPdata-column-dropdown',
                options=[{'label': col, 'value': col} for col in dayPcols2show],
                value=[],
                multi=True,
                placeholder="Sélectionnez des variables"
            ),
            dcc.Graph(id='dayP-series-graph'),
            html.H5('Valeurs I'),
            html.Div(id='dayIdata-column-description'),
            dcc.Dropdown(
                id='dayIdata-column-dropdown',
                options=[{'label': col, 'value': col} for col in dayIcols2show],
                value=[],
                multi=True,
                placeholder="Sélectionnez des variables"
            ),
            dcc.Graph(id='dayI-series-graph')
        ])
    elif tab == 'tab-stat':
        return html.Div([
            html.H3('Valeur moyenne de chacune des variables'),
        dcc.Dropdown(
            id='statperiod-dropdown',
            options=[
                {'label': 'Jour', 'value': 'stat_day'},
                {'label': 'Semaine', 'value': 'stat_week'},
                {'label': 'Mois', 'value': 'stat_month'},
                {'label': 'Année', 'value': 'stat_year'},
                {'label': 'Personnalisé', 'value': 'stat_perso'}
            ],
            value='stat_day',
            placeholder="Période"
        ),
            html.Button('Afficher', id='show-stat-btn', n_clicks=0),
            html.Div(id='stat-range-info', style={'marginTop': '20px'}),
            html.Div(id='stat-means-info', style={'marginTop': '20px'}),
            html.H3('Visualisation des données'),
            dcc.Dropdown(
                id='tabstatgraph-db',
                options=[
                    {'label': 'Données horaires', 'value': dbTime_name},
                    {'label': 'Données journalières P', 'value': dbDayP_name},
                    {'label': 'Données journalières I', 'value': dbDayI_name}
                ],
                placeholder="Choisissez la table de données"
            ),
            dcc.Dropdown(
                id='tabstatgraph-col',
                placeholder="Choisissez la colonne de données"
            ),
            html.Div(id='tabstatgraph-varinfo', style={'marginTop': '20px'}),
            dcc.Dropdown(
                id='tabstatgraph-viz',
                options=[
                    {'label': 'Line Plot', 'value': 'lineplot'},
                    {'label': 'Bar Plot', 'value': 'barplot'},
                    {'label': 'Box Plot', 'value': 'boxplot'}
                ],
                placeholder="Choisissez le type de visualisation"
            ),
            html.Button('Visualiser', id='show-statgraph-btn', n_clicks=0),
            dcc.Graph(id='stat-graph')
        ])
    elif tab == 'tab-analyseGraph':
        return html.Div([
            html.H3('Analyse (graphiques)'),
        dcc.Dropdown(
            id='asGraphPeriod-dropdown',
            options=[
                {'label': 'Jour', 'value': 'as_day'},
                {'label': 'Semaine', 'value': 'as_week'},
                {'label': 'Mois', 'value': 'as_month'},
                {'label': 'Année', 'value': 'as_year'},
                {'label': 'Personnalisé', 'value': 'as_perso'},
                {'label': 'Tout', 'value': 'as_all'}
            ],
            value='as_day',
            placeholder="Période"
        ),
            html.Div(id='analyseGraph-period-subtit', children=""),

            html.Button('Afficher', id='show-asGraph-btn', n_clicks=0),


            html.H4('Répartition des fréquences '),
        dcc.Dropdown(
            id='asL-dropdown',
            options=[
                {'label': 'L1', 'value': 'as_L1'},
                {'label': 'L2', 'value': 'as_L2'},
                {'label': 'L1+L2', 'value': 'as_both'}
            ],
            value='as_L1',
            placeholder="Source"
        ),
            html.Div(id='analyseGraph-pie-chart-tit', children=""),
            html.Div([
                #html.Div(dcc.Graph(id='analyseGraph-pie-chart-global'), className='col'),
                # html.Div(dcc.Graph(id='analyseGraph-pie-chart-day'), className='col'),
                # html.Div(dcc.Graph(id='analyseGraph-pie-chart-night'), className='col')
                html.Div(id='analyseGraph-pie-chart-global', children="", className="col"),
                html.Div(id='analyseGraph-pie-chart-day', children="", className="col"),
                html.Div(id='analyseGraph-pie-chart-night', children="", className="col")
            ], className='row'),

            html.H4('Température batterie'),

            html.Div([
                html.Div(id='analyseGraph-tempbat-barplot', children="", className="col")
            ], className='row')

        ])
    elif tab == 'tab-analyseStat':
        return html.Div([
            html.H3('Analyse (chiffres)'),
        dcc.Dropdown(
            id='asStatPeriod-dropdown',
            options=[
                {'label': 'Jour', 'value': 'as_day'},
                {'label': 'Semaine', 'value': 'as_week'},
                {'label': 'Mois', 'value': 'as_month'},
                {'label': 'Année', 'value': 'as_year'},
                {'label': 'Personnalisé', 'value': 'as_perso'},
                {'label': 'Tout', 'value': 'as_all'}
            ],
            value='as_day',
            placeholder="Période"
        ),
            html.Div(id='analyseStat-period-subtit', children=""),

            html.Button('Afficher', id='show-asStat-btn', n_clicks=0),
            html.H4('Puissance de sortie ' + xtpuicol),
            html.H5('Moyenne [W]'),
            html.Div(id='analyseStat-tableMean', children=""),
            html.H5([html.Br(), 'De crête [W]']),
            html.Div(id='analyseStat-tableMax', children=""),
            html.H5([html.Br(), 'Somme [W]']),
            html.Div(id='analyseStat-tableSum', children=""),
            html.H5([html.Br(), 'Somme/# Heures [W/h]']),
            html.Div(id='analyseStat-period-hourtxt', children=""),
            html.Div(id='analyseStat-tableSumByHour', children=""),
        ])
    elif tab == 'tab-updateDB':
        return html.Div([
            html.H3('Gérer les données'),
            html.H4('Ajout de données à partir de fichier(s)'),
            dcc.Upload(
                id='upload-data',
                children=html.Button('Upload Files'),
                style={
                    'width': '100%',
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px'
                },
                multiple=True  # Allow multiple files to be uploaded
            ),
            html.Div(id='output-upload'),
            html.H4('Suppression de données'),
            dcc.DatePickerSingle(
                id='date-picker-delete',
                date=None,
                display_format='DD.MM.YYYY',
                min_date_allowed=min(fetch_timedata_dates()),
                max_date_allowed=max(fetch_timedata_dates()),
                disabled_days=[pd.to_datetime(date).date() for date in
                               pd.date_range(start=min(fetch_timedata_dates()),
                                             end=max(fetch_timedata_dates())).
                               difference(pd.to_datetime(fetch_timedata_dates()))]
            ),
            html.Button('Supprimer les données', id='delete-button', n_clicks=0),
            html.Div(id='output-delete')
        ])
    elif tab == 'tab-showDB':
        # Lire les données de la base de données
        df = fetch_timedata()
        if picked_date:
            # Lire les données de la base de données pour la date sélectionnée
            picked_df = fetch_timedata(picked_date)
            # print(picked_df.shape[0])
        else:
            picked_df = pd.DataFrame(columns=["Aucun jour sélectionné"])
        # Convertir les données en tableau interactif DataTable
        data_table_all = dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': col, 'id': col} for col in df.columns],
            page_size=10,
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left'},
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold'
            }
        )
        data_table_selected = dash_table.DataTable(
            data=picked_df.to_dict('records'),
            columns=[{'name': col, 'id': col} for col in picked_df.columns],
            page_size=10,
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left'},
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold'
            }
        )
        # Nouvelle section pour afficher le nombre de jours disponibles
        all_entries = fetch_timedata_dates()
        num_entries = len(all_entries)
        print(all_entries[0])
        all_days = set([datetime.strptime(x,
                                     '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d') for
                    x in all_entries])
        #print(list(all_days)[0])

        num_days = len(all_days)
        nb_entries = html.Div([
            html.H6(f'Nombre d\'entrées dans la base de données : {num_entries}')
        ])
        nb_days = html.Div([
            html.H6(f'Nombre de jours dans la base de données : {num_days}')
        ])
        return html.Div([
            html.Div(id='datepicker-container'),
            html.H3('Données pour le jour sélectionné'),
            data_table_selected,
            html.H3('Aperçu de la base de données'),
            data_table_all,
            nb_entries,
            nb_days
        ])

# Exécuter l'application
if __name__ == '__main__':
    app.run_server(debug=True)
