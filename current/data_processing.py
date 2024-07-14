import pandas as pd
import re
from settings import *

def clean_cols(myl):
    #  myl = [re.sub(r'\[.*\]', '', x) for x in myl]
    myl = [re.sub(r'[-\[\]\+ \(\)°%]', '_', x.strip()) for x in myl]
    myl = [re.sub(r'_+', '_', x) for x in myl]
    myl = [x.strip("_") for x in myl]
    return myl


def getheadercols(r1, r2, r3):
    # les headers ont un champ de moins que les valeurs
    l1 = r1.split(';') + ["missing"]
    l2 = r2.split(';') + [""]
    l3 = r3.split(';') + [""]
    assert len(l1) == len(l2)
    assert len(l1) == len(l3)
    for i in range(1, len(l1)):
        if l1[i] == '':
            l1[i] = l1[i - 1]
    # enlever caractères spéciaux et unité
    l1 = clean_cols(l1)
    # Concatenate the first three rows to form new column names
    new_columns = [f'{l1[i]}_{l2[i]}_{l3[i]}' for i in range(len(l1))]
    new_columns = [re.sub(r'_+', '_', x) for x in new_columns]
    return clean_cols(new_columns)


def process_header(file_path):
    with open(file_path, encoding='latin1') as f:
        # lire les 3 lignes du header
        # de ce que je comprends, il y a un ";" pour marquer la fin de ligne
        lines = [f.readline().strip().rstrip(";") for _ in range(3)]
    new_columns = getheadercols(lines[0], lines[1], lines[2])
    return new_columns


def file2tables(file_path):
    print("> START processing " + file_path)
    error_msg = ""
    ok_msg = ""

    # Process the header to get new column names
    new_columns = process_header(file_path)

    # lire le reste des données à partirde la 4ème ligne
    # lire au maximum nrows=60 * 24, et ensuite vérifier qu'elles contiennent
    # toutes des donneés
    # try :
    data = pd.read_csv(file_path, skiprows=nHeaderSkip, encoding=enc,
                       sep=csvSep, header=None)

    ###############################################################
    ##################### EXTRAIRE LES DONNÉES TIME
    ###############################################################

    curr_day = data[0][0].split(' ')[0]

    time_data = data[data[0].str.match(r"^\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}$")]

    time_data.loc[:, 0] = pd.to_datetime(time_data.iloc[:, 0],
                        format='%d.%m.%Y %H:%M').dt.strftime('%Y-%m-%d %H:%M:%S')

    n0time, n0cols = time_data.shape
    assert n0time <= 60 * 24
    ## si j ai bien compris  la ligne est délimitée par ; en fin de ligne
    # donc al denrire colonne est toujours vide, vérifier et l'enlever
    assert time_data.iloc[:, n0cols - 1].isna().all()
    time_data = time_data.iloc[:, :(n0cols - 1)]
    ntime, ncols = time_data.shape
    assert ncols == n0cols - 1
    assert ncols == len(new_columns)
    assert ntime == n0time
    time_data.columns = new_columns

    if ntime < 60 * 24:
        error_msg += file_path + " - WARNING : missing 'time' data (available : " + str(ntime) + "/" + str(60 * 24)
    elif ntime == 60 * 24:
        ok_msg += file_path + " - SUCCESS reading 'time' data "

    assert time_data['missing'].isna().all()
    time_data.drop(columns=['missing'], inplace=True)
    time_data.rename(columns={time_data.columns[0]: db_timecol}, inplace=True)
    assert time_data.columns.isin(time_real_cols + time_txt_cols).all()

    time_missingcols = list(set(time_real_cols + time_txt_cols) - set(time_data.columns))

    if len(time_missingcols) > 0:
        error_msg += "\n"+ file_path + " - WARNING : missing 'time' data columns (" + ','.join(time_missingcols) + ")\n"
    else:
        ok_msg += "\n"+ file_path + " - SUCCESS found all 'time' data columns\n"

    ###############################################################
    ##################### EXTRAIRE LES DONNÉES DAY P
    ###############################################################
    dayP_dataL = data[data[0].str.match(r"^P\d{4}")]
    # vérifier qu'il n'y a pas plus de données que ce que je lis
    assert dayP_dataL.iloc[:, nColsDayP].isna().all()
    dayP_datam = dayP_dataL.melt(id_vars=[0],
                                 value_vars=list(dayP_dataL.columns)[1:nColsDayP],
                                 var_name='variable',
                                 value_name='value')
    dayP_datam.iloc[:, 0] = dayP_datam.iloc[:, 0] + "_" + dayP_datam.iloc[:, 1].astype(str)
    dayP_datam.drop(columns=['variable'], inplace=True)
    dayP_data = dayP_datam.T
    dayP_data.columns = dayP_data.iloc[0]
    dayP_data = dayP_data[1:]
    dayP_data.insert(0, day_txt_cols[0], curr_day)

    ndayP, ndayPcols = dayP_data.shape
    assert ndayP == 1
    if ndayP == 0:
        error_msg += "\n"+ file_path + " - WARNING : no 'dayP' data found"
    else :
        ok_msg += file_path + " - SUCCESS reading 'dayP' data "

    assert ndayPcols <= len(dayP_real_cols) + len(day_txt_cols)

    dayP_missingcols = list(set(dayP_real_cols + day_txt_cols) - set(dayP_data.columns))

    if len(dayP_missingcols) > 0:
        error_msg += "\n"+ file_path + " - WARNING : missing 'dayP' data columns (" + \
                     ','.join(dayP_missingcols) + ")\n"
    else:
        ok_msg += "\n"+ file_path + " - SUCCESS found all 'dayP' data columns\n"

    ###############################################################
    ##################### EXTRAIRE LES DONNÉES DAY I
    ###############################################################

    dayI_dataL = data[data[0].str.match(r"^I\d{4}")]
    # vérifier qu'il n'y a pas plus de données que ce que je lis
    assert dayI_dataL.iloc[:, nColsDayI].isna().all()
    dayI_datam = dayI_dataL.melt(id_vars=[0],
                                 value_vars=list(dayI_dataL.columns)[1:nColsDayI],
                                 var_name='variable',
                                 value_name='value')
    dayI_datam.iloc[:, 0] = dayI_datam.iloc[:, 0] + "_" + dayI_datam.iloc[:, 1].astype(str)
    dayI_datam.drop(columns=['variable'], inplace=True)
    dayI_data = dayI_datam.T
    dayI_data.columns = dayI_data.iloc[0]
    dayI_data = dayI_data[1:]
    dayI_data.insert(0, day_txt_cols[0], curr_day)

    ndayI, ndayIcols = dayI_data.shape
    assert ndayI <= 1
    if ndayI == 0:
        error_msg += "\n"+ file_path + " - WARNING : no 'dayI' data found\n"
    else :
        ok_msg += file_path + " - SUCCESS reading 'dayI' data\n"

    assert ndayIcols <= len(dayI_real_cols) + len(day_txt_cols)

    dayI_missingcols = list(set(dayI_real_cols + day_txt_cols) - set(dayI_data.columns))

    if len(dayI_missingcols) > 0:
        error_msg += "\n"+ file_path + " - WARNING : missing 'dayI' data columns (" + \
                     ','.join(dayI_missingcols) + ")\n"
    else:
        ok_msg += "\n"+ file_path + " - SUCCESS found all 'dayI' data columns\n"

    print("> END processing " + file_path)

    return {"time_data" : time_data,
            "dayP_data" : dayP_data,
            "dayI_data" : dayI_data,
            "error" : error_msg,
            "success" : ok_msg}
