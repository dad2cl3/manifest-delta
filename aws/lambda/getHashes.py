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

    sql = sqlConfig['hashes'].format(event['table_name'])

    if event['action'] == 'inserts':
        manifest = sqlConfig['inserts'].format(event['manifest_id'])
    elif event['action'] == 'updates':
        manifest = sqlConfig['updates'].format(event['manifest_id'])
    elif event['action'] == 'deletes':
        manifest = sqlConfig['deletes'].format(event['manifest_id'])

    sql += manifest

    print(sql)

    # Open database connection
    pg = pg8000.connect(host=dbConfig['Host'], port=dbConfig['Port'], database=dbConfig['Database'], user=dbConfig['User'], password=dbConfig['Password'])

    # Get hashes
    hashes = getData(pg, sql)
    hashList = []
    for hash in hashes['data']:
        hashList.append(hash[0])

    hashDict = {}
    hashDict['hashes'] = hashList

    # Close database connection
    pg.close()

    return hashDict