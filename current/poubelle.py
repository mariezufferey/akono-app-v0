
row1="v7.6;XT-Ubat- (MIN) [Vdc];;XT-Uin [Vac];;XT-Iin [Aac];;XT-Pout [kVA];;XT-Pout+ [kVA];;XT-Fout [Hz];;XT-Fin [Hz];;XT-Phase [];;XT-Mode [];;XT-Transfert [];;XT-E CMD [];;XT-Aux 1 [];;XT-Aux 2 [];;XT-Ubat [Vdc];;XT-Ibat [Adc];;XT-Pin a [kW];;XT-Pout a [kW];;XT-Tp1+ (MAX) [°C];;BSP-Ubat [Vdc];BSP-Ibat [Adc];BSP-SOC [%];BSP-Tbat [°C];Solar power (ALL) [kW];DEV XT-DBG1 [];DEV BSP-locE [];DEV SYS MSG;DEV SYS SCOM ERR;"
row2=";I3090;I3090;I3113;I3113;I3116;I3116;I3098;I3098;I3097;I3097;I3110;I3110;I3122;I3122;I3010;I3010;I3028;I3028;I3020;I3020;I3086;I3086;I3054;I3054;I3055;I3055;I3092;I3092;I3095;I3095;I3119;I3119;I3101;I3101;I3103;I3103;I7030;I7031;I7032;I7033;I17999;I3140;I7059;I17997;I17998;"
row3=";L1;L2;L1;L2;L1;L2;L1;L2;L1;L2;L1;L2;L1;L2;L1;L2;L1;L2;L1;L2;L1;L2;L1;L2;L1;L2;L1-1;L2-2;L1-1;L2-2;L1-1;L2-2;L1-1;L2-2;L1-1;L2-2;1;1;1;1;ALL;1;1;1;1;"
row4="15.12.2023 00:00;50.19;50.12;0;0;0;0;0.29;0.12;0.29;0.12;50.00;50.00;0;0;4;4;1;1;0;0;0;1;0;0;1;1;50.12;50.00;-3.00;-2.00;-0.00;-0.00;0.14;0.05;42.00;40.00;50.31;-4.73;83.06;28.00;0;61440.00;0;;0;;"

row1.count(";")
row2.count(";")
row3.count(";")
row4.count(";")

dcc.DatePickerRange(
    id='range-picker-daydata',
    # date=None,
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
get_range_picker('range-picker-evotime'),
# dcc.DatePickerRange(
#     id='range-picker-evotime',
#     # date=None,
#     display_format='DD.MM.YYYY',  ## prend les dates seulement dayP -> assume partt les mm !!
#     min_date_allowed=min(fetch_dayPdata_dates(dbDayP_name)),
#     max_date_allowed=max(fetch_dayPdata_dates(dbDayP_name)),
#     disabled_days=[pd.to_datetime(date).date() for date in
#                    pd.date_range(start=min(fetch_dayPdata_dates(dbDayP_name)),
#                                  end=max(fetch_dayPdata_dates(dbDayP_name))).
#                    difference(pd.to_datetime(fetch_dayPdata_dates(dbDayP_name)))],
#     minimum_nights=0,
#     style={'display': 'none'}  # Initialement caché
# ),
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

dcc.ConfirmDialog(
    id='confirm-dialog-evotime',
    message=''
),
dcc.ConfirmDialog(
    id='confirm-dialog-evoTimeDBgraph',
    message=''
),
dcc.ConfirmDialog(
    id='confirm-dialog-evoDayIDBgraph',
    message=''
),
dcc.ConfirmDialog(
    id='confirm-dialog-evoDayPDBgraph',
    message=''
),
# dcc.ConfirmDialog(
#     id='confirm-dialog-stat',
#     message=''
# ), dcc.ConfirmDialog(
#     id='confirm-dialog-statgraph',
#     message=''
# ),
dcc.ConfirmDialog(
    id='confirm-dialog-analyseGraph',
    message=''
), dcc.ConfirmDialog(
    id='confirm-dialog-daydataP',
    message=popupmsg_maxvar
), dcc.ConfirmDialog(
    id='confirm-dialog-daydataI',
    message=popupmsg_maxvar
)] + all_confirm_dialogs
