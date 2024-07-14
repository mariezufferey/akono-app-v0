from settings import *

tabname2tablab = dict()
tabname2tablab[dbTime_name] = "mesures minutées"
tabname2tablab[dbDayP_name] = "bilans journaliers P"
tabname2tablab[dbDayI_name] = "bilans journaliers I"

timeDB_card = dbc.CardGroup(
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

# Exemple de dayPDB_card ajoutée pour démonstration
dayPDB_card = dbc.CardGroup(
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

# Exemple de dayPDB_card ajoutée pour démonstration
dayIDB_card = dbc.CardGroup(
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
