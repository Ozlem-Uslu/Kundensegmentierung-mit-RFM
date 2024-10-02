###############################################################
# Kundensegmentierung mit RFM (Customer Segmentation with RFM)
###############################################################


###############################################################
# 1. Datenverständnis(Data Understanding)
###############################################################

#Importieren der wesentlichen Bibliotheken
import datetime as dt
import pandas as pd

#Anpassung, um eine bessere Beobachtung zu ermöglichen
pd.set_option('display.max_columns', None)
pd.set_option('display.float_format', lambda x: '%.3f' % x)

#Datensatz einlesen
df_ = pd.read_excel("RFM Analysis/online_retail_II.xlsx", sheet_name="Year 2010-2011")
df = df_.copy()
df.head()
#Daten ansehen und beschreiben
def check_df(dataframe):
    print("##################### Shape #####################")
    print(dataframe.shape)
    print("##################### Types #####################")
    print(dataframe.dtypes)
    print("##################### Head #####################")
    print(dataframe.head(3))
    print("##################### Tail #####################")
    print(dataframe.tail(3))
    print("##################### NA #####################")
    print(dataframe.isnull().sum())
    print("##################### Nunique #####################")
    print(dataframe.nunique())
check_df(df)

###############################################################
# 2. Datenvorbereitung(Data Preparation)
###############################################################
# Die fehlenden Werte aus dem Datensatz löschen
df.isnull().sum()
df.dropna(inplace=True)

#die fünf am häufigsten bestellten Produkte vom höchsten zum niedrigsten Wert auflisten
df.groupby("Description").agg({"Quantity":"sum"}).sort_values("Quantity", ascending=False).head()

# „C“ auf Rechnungen weist auf stornierte Transaktionen hin.
# Abgebrochene Transaktionen aus dem Datensatz entfernen.
df[df["Invoice"].str.contains("C", na=False)] # Invoice mit C
df = df[~df["Invoice"].str.contains("C", na=False)] #Invoice ohne C

# Eine Variable mit dem Namen „TotalPrice“, die den Gesamterlös pro Rechnung darstellt, erstellen
df["TotalPrice"] = df["Price"] * df["Quantity"]
df.head()

# Die Größe überprüfen, nachdem die Datensatz bereinigt wurde
df.shape

###############################################################
# 3. RFM-Metriken berechnen(Calculating RFM Metrics)
###############################################################
# Erläutern wir zunächst die grundlegenden Konzepte von RFM.
# Recency(Aktualität): Gibt Auskunft über die Zeit, die seit dem letzten Einkauf des Kunden vergangen ist.
# Sie kann in Tagen, Wochen oder Monaten ausgedrückt werden.
# Frequency(Häufigkeit): Zeigt an, wie oft der Kunde Einkäufe tätigt.
# Monetary(Monetär): Der Gesamtbetrag, den der Kunde für seine Einkäufe ausgibt.

df.head()

#für Recency das heutige Datum als (2011, 12, 11) annehmen
today_date = dt.datetime(2011, 12, 11)

# Metrik von Recency, Frequency ve Monetary für den Kunden berechnen
df.groupby("Customer ID").agg({"InvoiceDate" : lambda InvoiceDate: (today_date - InvoiceDate.max()).days,
                               "Invoice" : lambda Invoice : Invoice.nunique(),
                               "TotalPrice" : lambda TotalPrice : TotalPrice.sum()})

# Die von berechneten Metriken einer Variablen namens "rfm" zuweisen
rfm = df.groupby("Customer ID").agg({"InvoiceDate" : lambda InvoiceDate: (today_date - InvoiceDate.max()).days,
                               "Invoice" : lambda Invoice : Invoice.nunique(),
                               "TotalPrice" : lambda TotalPrice : TotalPrice.sum()})
rfm.head()

# Die Namen der von erstellten Metriken in „Recency“, „Frequency“ und „Monetary“ ändern
rfm.columns = ["Recency", "Frequency", "Monetary"]

# Den Datensatz nach „Monetary>0“ filtern
rfm.describe()
rfm = rfm[rfm["Monetary"] > 0]

#Die Größe vom Datensatz "rfm" überprüfen
rfm.shape

###############################################################
# 4. Berechnung der RFM-Scores(Calculating RFM Scores)
###############################################################
# Die Metriken von Recency, Frequency ve Monetary in Werte zwischen 1 und 5 konvertieren
rfm["Recency_Score"] = pd.qcut(rfm["Recency"], 5, labels=[5, 4, 3, 2, 1])
rfm["Frequency_Score"] = pd.qcut(rfm["Frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
rfm["Monatery_Score"] = pd.qcut(rfm["Monetary"], 5, labels=[1, 2, 3, 4, 5])

# Recency_Score und Frequency_Score als einzelne Variable ausdrücken und sie als RF_SCORE speichern
rfm["RF_SCORE"] = (rfm["Recency_Score"].astype(str) + rfm["Frequency_Score"].astype(str))

###############################################################
# 5. Erstellen und Analysieren von RFM-Segmenten (Creating & Analysing RFM Segments)
###############################################################

# RF-Nomenklatur
seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_Risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}

# RF-Scores mit Hilfe von seg_map in Segmente konvertieren
rfm["Segment"] = rfm["RF_SCORE"].replace(seg_map, regex= True)

# Die zur Klasse „at_Risk“ gehörenden Kunden-IDs auswählen und diese in Excel ausdrucken
new_df = pd.DataFrame()
new_df["at_Risk_ID"] = rfm[rfm["Segment"] == "at_Risk"].index
new_df["at_Risk_ID"] = new_df["at_Risk_ID"].astype(int)

new_df.to_excel("at_Risk.xlsx")
