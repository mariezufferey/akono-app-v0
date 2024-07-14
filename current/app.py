from settings import *
from utils_fcts import *
import plotly.express as px
from datetime import timedelta
import pandas as pd
import numpy as np
from dash import dash_table
import pandas as pd
from datetime import datetime, timedelta
from app_settings import *




##################################### TODO IN PROCESS : dashboard
# https://dash.gallery/dash-manufacture-spc-dashboard/
# https://github.com/plotly/dash-sample-apps/blob/main/apps/dash-manufacture-spc-dashboard/app.py


## prend les dates seulement dayP -> assume partt les mm !!

dayPdata_columns = get_daydata_columns("P")
dayIdata_columns = get_daydata_columns("I")
timedata_columns = get_timedata_columns()
timecols2show = [x for x in timedata_columns if not showcols_settings[x] == "NA"]
dayPcols2show = [x for x in dayPdata_columns if not x == db_daycol]
dayIcols2show = [x for x in dayIdata_columns if not x == db_daycol]

# Initialiser l'application Dash avec suppression des exceptions de callback
app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.BOOTSTRAP, FONT_AWESOME],
                suppress_callback_exceptions=True)

# Définir la mise en page de l'application

all_confirm_dialogs = [dcc.ConfirmDialog(id=x,message='')
                       for x in ['confirm-dialog-dashboard',
                                 'confirm-dialog-stat',
                                 'confirm-dialog-statgraph',
                                 'confirm-dialog-evotime',
                                 'confirm-dialog-evoDayIDBgraph',
                                 'confirm-dialog-evoTimeDBgraph',
                                 'confirm-dialog-evoDayPDBgraph',
                                 'confirm-dialog-analyseGraph',
                                 ]]

all_maxvar_dialogs = [dcc.ConfirmDialog(id=x,message=popupmsg_maxvar)
                       for x in ['confirm-dialog',
                                 'confirm-dialog-daydataP',
                                 'confirm-dialog-daydataI',
                                 ]]
all_range_pickers = [get_range_picker(x) for x in [
                    'range-picker-dashboard',
                    'range-picker-stat',
                        'range-picker-evotime',
                        'range-picker-analyseGraph'
                            ]]




app.layout = html.Div([
    dcc.Tabs(id="tabs-example", value='tab-dashb', children=[  # value ici définit l'onglet par défaut
        dcc.Tab(label='Dashboard', value='tab-dashb',
                className='mytab', selected_className='mytab-slctd'),
        dcc.Tab(label='Evolution temporelle', value='tab-evotime',
                className='mytab', selected_className='mytab-slctd'),
        dcc.Tab(label='Statistiques', value='tab-stat',
                className='mytab', selected_className='mytab-slctd'),
        dcc.Tab(label='Analyse (graphes)', value='tab-analyseGraph',
                className='mytab', selected_className='mytab-slctd'),
        dcc.Tab(label='Gérer les données', value='tab-updateDB',
                className='mytab', selected_className='mytab-slctd'),
        dcc.Tab(label='Base de données', value='tab-showDB',
                className='mytab', selected_className='mytab-slctd')
    ]),
    dcc.DatePickerSingle(
        id='date-picker-dbdata',
        date=None,
        display_format='DD.MM.YYYY',
        min_date_allowed=min(fetch_timedata_dates()),
        max_date_allowed=max(fetch_timedata_dates()),
        disabled_days=[pd.to_datetime(date).date() for date in
                       pd.date_range(start=min(fetch_timedata_dates()),
                                     end=max(fetch_timedata_dates())).
                       difference(pd.to_datetime(fetch_timedata_dates()))],
        style={'display': 'none'}  # Initialement caché
        # attention : pd.date_range(...).retourne un DatetimeIndex
        # pd.to_datetime pour convertir all_dates aussi en DatetimeIndex pr comparer
    )] +
                      all_range_pickers +
                      all_maxvar_dialogs +
                      all_confirm_dialogs+
    [html.Div(id='tabs-content')]

)


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

        chargeTotal_dayI = round(dayI_df[ahCharge_dayIcol + "_1"].fillna(0).sum(), 2)
        dechargeTotal_dayI = round(dayI_df[ahDecharge_dayIcol + "_1"].fillna(0).sum(), 2)
        rendementTot_dayI = round(dechargeTotal_dayI / chargeTotal_dayI * 100, 2)
        nCycles = round(chargeTotal_dayI / 90)
        return (f'{num_days} jours',
                [f'{num_daysI} jours',
                 html.Br(),
                 html.B("Charge batterie total [Ah]"), " (" + ahCharge_dayIcol + ") :\t" + \
                 str(chargeTotal_dayI),
                 html.Br(),
                 html.B("Rendement batterie total [%]"), " (" + ahDecharge_dayIcol + "/" + \
                 ahCharge_dayIcol + ") :\t" + \
                 str(rendementTot_dayI) + " %",
                 html.Br(),
                 html.B("# Cycles"), " (" + ahCharge_dayIcol + "/90) :\t" + \
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
    Output('range-picker-evotime', 'style'),
    [Input('tabs-example', 'value')]
)
def show_hide_evotimedatepicker(tab):
    if tab == 'tab-evotime':
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
@app.callback(
    Output('range-picker-dashboard', 'style'),
    [Input('tabs-example', 'value')]
)
def show_hide_dashboarddatepicker(tab):
    if tab == 'tab-dashb':
        return {'display': 'block', 'margin': '20px 0'}  # Afficher le DatePickerSingle
    else:
        return {'display': 'none'}  # Cacher le DatePickerSingle


################################################################################################
################################ CALLBACKS - TAB DASHBOARD		tab-dashb
################################################################################################


@app.callback(
    Output('dashboard-graph-varinfo', 'children'),
    [Input('dashboard-device-choice', 'value')]
)
def update_dashboardvarinfo(selected_device, selected_db=dbTime_name):
    if selected_device :
        desc_txt = selected_device
    else:
        return None
    return html.Div([dcc.Markdown(desc_txt,
                                  dangerously_allow_html=True)])


# Callback pour afficher le graphique en fonction de la sélection :
@app.callback(
    [Output('dashboard-graph', 'figure'),
     Output('confirm-dialog-dashboard', 'displayed'),
     Output('confirm-dialog-dashboard', 'message'),
     Output('dashboard-range-info', 'children')],

    [Input('show-dashboard-btn', 'n_clicks')],
    [

        State('dashboard-device-choice', 'value'),
        State('range-picker-dashboard', 'start_date'),
        State('range-picker-dashboard', 'end_date'),
        State('dashboardperiod-dropdown', 'value')]
)
def display_dashboard_graph(n_clicks, selected_device,
                            start_date, end_date, selected_period):
    if selected_device == "XTender":
        selected_col = 'XT_Transfert_I3020_L2'
    else:
        selected_col = 'Solar_power_ALL_kW_I17999_ALL'
    selected_viz = 'lineplot'

    selected_db = dbTime_name
    if n_clicks is None or n_clicks == 0:
        return [go.Figure(), False, "", ""]
    if (not selected_db or not selected_col or not selected_viz) and (not start_date or not end_date):
        return [go.Figure(), True, "Sélectionnez des données et une période", "Sélectionnez des données et une période"]

    if not selected_db or not selected_col or not selected_viz:
        return [go.Figure(), True, "Sélectionnez des données", "Sélectionnez des données"]

    if selected_period == "stat_all":
        date_info = f"Toutes les données disponibles"
        query = get_query_extractInterval(selected_db, None, None)
    else:
        if not start_date or not end_date:
            return [go.Figure(), True, "Sélectionnez une période", "Sélectionnez une période"]

        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        if selected_period in ['stat_day', 'stat_week', 'stat_month', 'stat_year']:
            if start_date != end_date:
                return ["ERREUR", True, "Choisir une seule date dans une modal pop-up", ""]
            start_date = get_startrange_date(end_date, selected_period)

        if selected_period == 'stat_perso' and start_date == end_date:
            return [go.Figure(), True, "Choisir une date différente", "Choisir une date différente"]

        date_info = f"Données du {start_date} au {end_date}"
        query = get_query_extractInterval(selected_db, start_date, end_date)

    conn = sqlite3.connect(db_file)
    df = pd.read_sql_query(query, conn)
    conn.close()

    if selected_db == dbTime_name:
        xcol = db_timecol
    else:
        xcol = db_daycol
        if selected_db == dbDayI_name:
            for col in dayI_cols:
                df[col] = df[col + "_1"].fillna(0) + df[col + "_2"].fillna(0)

    if selected_db == dbTime_name and selected_viz == 'boxplot':
        df['date'] = pd.to_datetime(df[xcol]).dt.date
        fig = px.box(df, x='date', y=selected_col, title=f'{selected_col} Box Plot par jour')
    else:
        if selected_viz == 'lineplot':
            fig = px.line(df, x=xcol, y=selected_col, title=f'{selected_col} Line Plot')
        elif selected_viz == 'barplot':
            fig = px.bar(df, x=xcol, y=selected_col, title=f'{selected_col} Bar Plot')
        elif selected_viz == 'boxplot':
            fig = px.box(df, x=xcol, y=selected_col, title=f'{selected_col} Box Plot')

    if (selected_db == dbTime_name and selected_viz == 'boxplot') or (
            selected_db == dbDayP_name or selected_db == dbDayI_name):
        fig.update_layout(xaxis=dict(title='Date', tickformat='%Y-%m-%d', dtick="D1"))
    return [fig, False, "", date_info]


##################################################################################
######################################### CALL BACK tab analyse GRAPH
##################################################################################

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


# # callback pour vérifier le nombre de variables sélectionnées et afficher la pop-up :
# callback pour vérifier le nombre de variables sélectionnées et afficher la pop-up :
@app.callback(
    [Output('confirm-dialog-daydataP', 'displayed'),
     Output('dayPdata-column-dropdown', 'value')],
    [Input('dayPdata-column-dropdown', 'value')]
)
def limit_selection_dayPdata(selected_columns):
    if len(selected_columns) > maxTimePlotVar:
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
    if len(selected_columns) > maxTimePlotVar:
        return True, selected_columns[:maxTimePlotVar]  # Afficher la pop-up et limiter la sélection à 2
    return False, selected_columns  # Ne pas afficher la pop-up


# Ajouter un callback pour mettre à jour la description - dayP data
@app.callback(
    Output('dayPdata-column-description', 'children'),
    [Input('dayPdata-column-dropdown', 'value')]
)
def update_dayP_description(selected_columns):
    if selected_columns:
        # print(';'.join(showcols_settings.keys()))
        desc_txt = '<br>'.join(["<b>" + selcol + "</b> : " + \
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
        # print(';'.join(showcols_settings.keys()))
        desc_txt = '<br>'.join(["<b>" + selcol + "</b> : " + \
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
def update_analyse_pie_chart(n_clicks, selected_period, selected_L,
                             start_date, end_date):
    if n_clicks is None or n_clicks == 0:
        return "", "", "", "", "", "", False, ""
    if selected_period != 'stat_all' and (not start_date or not end_date):
        return "", "", "", "", "", "", True, "Sélectionnez une période"

    if selected_period != 'stat_all':
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        if selected_period in ['stat_day', 'stat_week', 'stat_month', 'stat_year']:
            if start_date != end_date:
                return "", "", "", "", "", "", True, "Choisir une seule date dans une modal pop-up"
            start_date = get_startrange_date(end_date, selected_period)

        if selected_period == 'stat_perso' and start_date == end_date:
            return "", "", "", "", "", "", True, "Choisir une date différente"

    # Extraire les données pour l'intervalle sélectionné
    conn = sqlite3.connect(db_file)
    if selected_period == 'stat_all':
        query = f"SELECT * FROM {dbTime_name}"
        interval_txt = " (tout)"
        interval_txt = " Toutes les données"
    else:
        query = get_query_extractInterval(dbTime_name, start_date, end_date)
        # interval_txt = ("(" + start_date.strftime('%d/%m/%Y') +" - " +
        #                 end_date.strftime('%d/%m/%Y') + ")")
        interval_txt = ("Période : " + start_date.strftime('%d/%m/%Y') + " - " +
                        end_date.strftime('%d/%m/%Y'))
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
        html.H4("Répartition fréquences (" + calcol_txt + ")"),
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
        title="Global"
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

    assert df.shape[0] == (df_night.shape[0] + df_day.shape[0])

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



################################################################################################
################################ CALLBACKS - TAB EVOTIME - VISUALISATIONS   tab-evotime
################################################################################################


@app.callback(
    Output('evotimeTimeDB-graph-varinfo', 'children'),
    [Input('evotimeTimeDB-graph-col', 'value')]
)
def update_evotimevarinfo(selected_col, selected_db=dbTime_name):
    if selected_col and selected_db:
        desc_txt = get_var_desc(selected_col, selected_db)
    else:
        return None
    return html.Div([dcc.Markdown(desc_txt,
                                  dangerously_allow_html=True)])

# Callback pour afficher le graphique en fonction de la sélection :
@app.callback(
    [Output('evotimeTimeDB-graph', 'figure'),
     Output('confirm-dialog-evoTimeDBgraph', 'displayed'),
     Output('confirm-dialog-evoTimeDBgraph', 'message'),
     Output('evotime-range-info', 'children')],

    [Input('show-evotimeTimeDBgraph-btn', 'n_clicks')],
    [
        State('evotimeTimeDB-graph-col', 'value'),
        State('evotimeTimeDB-graph-viz', 'value'),
        State('range-picker-evotime', 'start_date'),
        State('range-picker-evotime', 'end_date'),
        State('evotimeperiod-dropdown', 'value')]
)
def display_evoTimeDB_graph(n_clicks, selected_col, selected_viz,
                            start_date, end_date, selected_period):
    selected_db = dbTime_name
    if n_clicks is None or n_clicks == 0:
        return [go.Figure(), False, "", ""]
    if (not selected_db or not selected_col or not selected_viz) and (not start_date or not end_date):
        return [go.Figure(), True, "Sélectionnez des données et une période", "Sélectionnez des données et une période"]

    if not selected_db or not selected_col or not selected_viz:
        return [go.Figure(), True, "Sélectionnez des données","Sélectionnez des données"]

    if selected_period == "stat_all":
        date_info = f"Toutes les données disponibles"
        query = get_query_extractInterval(selected_db, None, None)
    else :
        if not start_date or not end_date:
            return [go.Figure(), True, "Sélectionnez une période", "Sélectionnez une période"]

        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        if selected_period in ['stat_day', 'stat_week', 'stat_month', 'stat_year']:
            if start_date != end_date:
                return ["ERREUR", True, "Choisir une seule date dans une modal pop-up", ""]
            start_date = get_startrange_date(end_date, selected_period)

        if selected_period == 'stat_perso' and start_date == end_date:
            return [go.Figure(), True, "Choisir une date différente", "Choisir une date différente"]

        date_info = f"Données du {start_date} au {end_date}"
        query = get_query_extractInterval(selected_db, start_date, end_date)

    conn = sqlite3.connect(db_file)
    df = pd.read_sql_query(query, conn)
    conn.close()

    if selected_db == dbTime_name:
        xcol = db_timecol
    else:
        xcol = db_daycol
        if selected_db == dbDayI_name:
            for col in dayI_cols:
                df[col] = df[col + "_1"].fillna(0) + df[col + "_2"].fillna(0)

    if selected_db == dbTime_name and selected_viz == 'boxplot':
        df['date'] = pd.to_datetime(df[xcol]).dt.date
        fig = px.box(df, x='date', y=selected_col, title=f'{selected_col} Box Plot par jour')
    else:
        if selected_viz == 'lineplot':

            shapes = []
            threshold = 56
            above_threshold = df[df[selected_col] > threshold]

            if not above_threshold.empty:
                segments = []
                start_idx = None

                for i in range(len(df)):
                    if df.iloc[i][selected_col] > threshold:
                        if start_idx is None:
                            start_idx = i
                    else:
                        if start_idx is not None:
                            segments.append((start_idx, i - 1))
                            start_idx = None
                if start_idx is not None:
                    segments.append((start_idx, len(df) - 1))

                for segment in segments:
                    shapes.append({
                        'type': 'rect',
                        'xref': 'x',
                        'yref': 'paper',
                        'x0': df.iloc[segment[0]][xcol],
                        'y0': 0,
                        'x1': df.iloc[segment[1]][xcol],
                        'y1': 1,
                        'fillcolor': 'red',
                        'opacity': 0.3,
                        'line': {
                            'width': 0,
                        }
                    })

            fig = go.Figure()

            fig.add_trace(go.Scatter(x=df[xcol], y=df[selected_col],
                                     mode='lines', name=f'{selected_col} Line Plot',
                                     line=dict(color='blue')))

            fig.update_layout(shapes=shapes, title=f'{selected_col} Line Plot')

            
            # # fig = px.line(df, x=xcol, y=selected_col, title=f'{selected_col} Line Plot')
            # threshold = 56
            # df['color'] = np.where(df[selected_col] > threshold, 'red', 'blue')
            # threshold = 56
            # fig = go.Figure()
            # ######################### I HAVE STOPPED HERE !!!!!!!!!!!!!!!!!!!!
            # segment_x = []
            # segment_y = []
            # current_color = 'blue'
            #
            # for i in range(len(df)):
            #     if i > 0 and (df.iloc[i][selected_col] > threshold and current_color == 'blue') or (df.iloc[i][selected_col] <= threshold and current_color == 'red'):
            #         fig.add_trace(go.Scatter(x=segment_x, y=segment_y,
            #                                  mode='lines', line=dict(color=current_color)))
            #         segment_x = [df.iloc[i-1][xcol], df.iloc[i][xcol]]
            #         segment_y = [df.iloc[i-1][selected_col], df.iloc[i][selected_col]]
            #         current_color = 'red' if current_color == 'blue' else 'blue'
            #     else:
            #         segment_x.append(df.iloc[i][xcol])
            #         segment_y.append(df.iloc[i][selected_col])
            #
            # fig.add_trace(go.Scatter(x=segment_x, y=segment_y,
            #                          mode='lines', line=dict(color=current_color)))
            # fig.update_layout(title=f'{selected_col} Line Plot')
        elif selected_viz == 'barplot':
            fig = px.bar(df, x=xcol, y=selected_col, title=f'{selected_col} Bar Plot')
        elif selected_viz == 'boxplot':
            fig = px.box(df, x=xcol, y=selected_col, title=f'{selected_col} Box Plot')

    if (selected_db == dbTime_name and selected_viz == 'boxplot') or (
            selected_db == dbDayP_name or selected_db == dbDayI_name):
        fig.update_layout(xaxis=dict(title='Date', tickformat='%Y-%m-%d', dtick="D1"))
    return [fig, False, "", date_info]


############################### ###############################
############################### CALL BACKS STAT tab-stat
############################### ###############################

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
    if n_clicks is None or n_clicks == 0:
        return ["", False, "", ""]


    if selected_period == "stat_all":
        query_time = get_query_extractInterval(dbTime_name, None, None)
    else :
        if not start_date or not end_date:
            return ["", True, "Sélectionnez une période", ""]
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        # query_time = f"SELECT * FROM {dbTime_name} WHERE DATE({db_timecol}) >= DATE('{start_date}') AND DATE({db_timecol}) <= DATE('{end_date}')"
        query_time = get_query_extractInterval(dbTime_name, start_date, end_date)

        if selected_period in ['stat_day', 'stat_week', 'stat_month', 'stat_year']:
            if start_date != end_date:
                return ["ERREUR", True, "Choisir une seule date dans une modal pop-up", ""]
            start_date = get_startrange_date(end_date, selected_period)

        if selected_period == 'stat_perso' and start_date == end_date:
            return ["ERREUR", True, "Choisir une date différente", ""]

    # Extraire les données pour l'intervalle sélectionné
    conn = sqlite3.connect(db_file)

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




################################ CALLBACKS - TAB STAT - VISUALISATION

# Callback pour mettre à jour les colonnes disponibles en fonction de la table sélectionnée :

@app.callback(
    Output('tabstatgraph-col', 'options'),
    [Input('tabstatgraph-db', 'value')]
)
def update_stat_columns(selected_db):
    if selected_db:
        if selected_db == dbTime_name:
            columns = [{'label': col, 'value': col} for col in timecols2show]
        elif selected_db == dbDayP_name:
            columns = [{'label': col, 'value': col} for col in dayPcols2show]
        elif selected_db == dbDayI_name:
            columns = [{'label': col, 'value': col} for col in dayI_cols + dayIcols2show]
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
            desc_txt = "<b>" + selected_col + "</b> : " + \
                       showcols_settings[selected_col]['description']

        elif selected_db == dbDayP_name:
            desc_txt = "<b>" + selected_col + "</b> : " + \
                       dayPcols_settings[selected_col]['description']

        elif selected_db == dbDayI_name:
            desc_txt = "<b>" + selected_col + "</b> : " + \
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
    if n_clicks is None or n_clicks == 0:
        return [go.Figure(), False, ""]
    if (not selected_db or not selected_col or not selected_viz) and (not start_date or not end_date):
        return [go.Figure(), True, "Sélectionnez des données et une période"]

    if not selected_db or not selected_col or not selected_viz:
        return [go.Figure(), True, "Sélectionnez des données"]

    if not start_date or not end_date:
        return [go.Figure(), True, "Sélectionnez une période"]

    conn = sqlite3.connect(db_file)
    query = get_query_extractInterval(selected_db, start_date, end_date)

    # query = f"SELECT {db_daycol}, {selected_col} FROM {selected_db} WHERE {db_daycol} >= '{start_date}' AND {db_daycol} <= '{end_date}'"
    df = pd.read_sql_query(query, conn)
    conn.close()

    if selected_db == dbTime_name:
        xcol = db_timecol
    else:
        xcol = db_daycol
        if selected_db == dbDayI_name:
            for col in dayI_cols:
                df[col] = df[col + "_1"].fillna(0) + df[col + "_2"].fillna(0)

    if selected_db == dbTime_name and selected_viz == 'boxplot':
        df['date'] = pd.to_datetime(df[xcol]).dt.date
        fig = px.box(df, x='date', y=selected_col, title=f'{selected_col} Box Plot par jour')
    else:
        if selected_viz == 'lineplot':
            fig = px.line(df, x=xcol, y=selected_col, title=f'{selected_col} Line Plot')
        elif selected_viz == 'barplot':
            fig = px.bar(df, x=xcol, y=selected_col, title=f'{selected_col} Bar Plot')
        elif selected_viz == 'boxplot':
            fig = px.box(df, x=xcol, y=selected_col, title=f'{selected_col} Box Plot')

    if (selected_db == dbTime_name and selected_viz == 'boxplot') or (
            selected_db == dbDayP_name or selected_db == dbDayI_name):
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
    # print('disabled Days = ' + ','.join(disabled_days))
    return (min_date_allowed, max_date_allowed,
            disabled_days, min_date_allowed,
            max_date_allowed, disabled_days)

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
        title_text="",  ## titre en-haut à gauche
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
    if len(selected_columns) > maxTimePlotVar:
        return True, selected_columns[:maxTimePlotVar]  # Afficher la pop-up et limiter la sélection à 2
    return False, selected_columns  # Ne pas afficher la pop-up


# Ajouter un callback pour mettre à jour la description
@app.callback(
    Output('timedata-column-description', 'children'),
    [Input('timedata-column-dropdown', 'value')]
)
def update_description(selected_columns):
    if selected_columns:
        desc_txt = '<br>'.join(["<b>" + selcol + "</b> : " + showcols_settings[selcol]['description']
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
        return html.Div([
            html.H3('Contenu de la base de données'),
            get_period_dropdown('dashboardperiod-dropdown'),

            dcc.Dropdown(
                id='dashboard-device-choice',
                placeholder="Choisissez l'appareil",
                options=['XTender', 'Variotrack']
            ),
            html.Div(id='dashboard-graph-varinfo', style={'marginTop': '20px'}),

            html.Button('Afficher', id='show-dashboard-btn', n_clicks=0),
            html.Div(id='dashboard-range-info', style={'marginTop': '20px'}),

            dcc.Graph(id='dashboard-graph'),
            dbc.Container(dbc.Row(dbc.Col([timeDB_card,
                            dayPDB_card, dayIDB_card], md=10)))
        ])
    elif tab == 'tab-evotime':
        return html.Div([
            html.H3('Aperçu dans le temps'),

            html.H4(dbTime_name + ' database'),
            get_period_dropdown('evotimeperiod-dropdown'),
            html.Button('Afficher', id='show-evotime-btn', n_clicks=0),
            html.Div(id='evotime-range-info', style={'marginTop': '20px'}),

            dcc.Dropdown(
                id='evotimeTimeDB-graph-col',
                placeholder="Choisissez la colonne de données",
                options=[{'label': col, 'value': col} for col in timecols2show]
            ),
            html.Div(id='evotimeTimeDB-graph-varinfo', style={'marginTop': '20px'}),
            dcc.Dropdown(
                id='evotimeTimeDB-graph-viz',
                options=[
                    {'label': 'Line Plot', 'value': 'lineplot'},
                    {'label': 'Bar Plot', 'value': 'barplot'},
                    {'label': 'Box Plot', 'value': 'boxplot'}
                ],
                placeholder="Choisissez le type de visualisation"
            ),
            html.Button('Visualiser', id='show-evotimeTimeDBgraph-btn',
                        n_clicks=0),
            dcc.Graph(id='evotimeTimeDB-graph')
        ])
    elif tab == 'tab-stat':
        return html.Div([
            html.H3('Valeur moyenne de chacune des variables'),
            get_period_dropdown('statperiod-dropdown'),
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
            get_period_dropdown('asGraphPeriod-dropdown'),
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
                html.Div(id='analyseGraph-pie-chart-global', children="", className="col"),
                html.Div(id='analyseGraph-pie-chart-day', children="", className="col"),
                html.Div(id='analyseGraph-pie-chart-night', children="", className="col")
            ], className='row'),

            html.H4('Température batterie'),

            html.Div([
                html.Div(id='analyseGraph-tempbat-barplot', children="", className="col")
            ], className='row')

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
        # print(list(all_days)[0])

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
