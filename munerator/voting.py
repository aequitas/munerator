from CodernityDB.database import Database


def main(argv):
    db = Database('db')
    db.create()

    for x in range(100):
        print(db.insert(dict(x=x)))

    for curr in db.all('id'):
        print(curr)

if __name__ == '__main__':
    main()
