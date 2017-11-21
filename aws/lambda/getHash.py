import pg8000, json

with open('config.json', 'r') as configFile:
    config = json.load(configFile)

dbConfig = config['Database']
sqlConfig = config['SQL']


def getData(db,sql):
    print('Executing SQL statement...')

    data = {}

    pgCursor = db.cursor()
    pgCursor.execute(sql)
    data['data'] = pgCursor.fetchall()
    data['columns'] = pgCursor.description

    return data


def handler(event, context):

    # Build SQL based on event
    sql = sqlConfig['hash'].format(event['table_name'], event['hash'])

    print(sql)

    # Open database connection
    pg = pg8000.connect(host=dbConfig['Host'], port=dbConfig['Port'], database=dbConfig['Database'], user=dbConfig['User'], password=dbConfig['Password'])

    # Get hashes
    detail = getData(pg, sql)

    #print(json.dumps(detail['data'][0][0],indent=1))

    # Close database connection
    pg.close()

    return detail['data'][0][0]