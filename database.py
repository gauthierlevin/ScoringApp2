import pyodbc

server = 'serveurscoringapp.database.windows.net'
database = 'ScoringApp'
username = 'GLEVINTR'
password = 'p$lastOdi73'
driver= '{SQL Server}'

cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = cnxn.cursor()

