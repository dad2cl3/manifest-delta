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

def getCurrentVersion(db):
    print('Getting the current manifest version...')

    data = getData(db, sqlConfig['current_version'])['data']

    currentVersion = {}
    currentVersion['manifest_id'] = data[0][0]
    currentVersion['current_version'] = data[0][1]['version']
    currentVersion['current_path'] = 'https://www.bungie.net' + data[0][1]['path']
    #print(currentVersion)

    return currentVersion

def getChanges(db, version):
    print('Getting the delta counts...')

    data = getData(db, sqlConfig['changes'].format(version))

    columns = data['columns']

    headers = []
    for column in columns:
        headers.append(column[0].decode('utf8').replace('_', ' ').title())

    changeCounts = []
    for row in data['data']:
        table = {}

        for i in range(len(row)):
            table[columns[i][0].decode('utf8')] = row[i]

        changeCounts.append(table)

    #print(changeCounts)

    changes = {}
    changes['headers'] = headers
    changes['changes'] = changeCounts

    return changes

def handler (event, context):

    # Open the database connection
    pg = pg8000.connect(host=dbConfig['Host'], port=dbConfig['Port'], database=dbConfig['Database'], user=dbConfig['User'], password=dbConfig['Password'])

    # Get the current version
    currentVersion = getCurrentVersion(pg)

    # Get the changes
    changes = getChanges(pg, currentVersion['manifest_id'])

    response = dict(list(currentVersion.items()) + list(changes.items()))

    # Close the database connection
    pg.close()

    return response