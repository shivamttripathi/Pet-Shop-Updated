import psycopg2
from petConfig import *

class DBConnection:
    # class members
    conn = None
    cur = None
    # config vars
    ownerCols = ConfigVars.tableCols[ConfigVars.ownerTable]
    petCols = ConfigVars.tableCols[ConfigVars.petTable]
    ownershipCols = ConfigVars.tableCols[ConfigVars.ownershipTable]
    ownershipCons = ConfigVars.tableConstraints[ConfigVars.ownershipTable]
    
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(DBConnection, cls).__new__(cls)
        return cls.instance
    
    def __init__(self):
        pass
    
    @classmethod
    def dbConnect(cls):
        if not cls.conn:
            cls.conn = psycopg2.connect(
                database=ConfigVars.dbvars['database'],
                user=ConfigVars.dbvars['user'],
                password=ConfigVars.dbvars['password'],
                host=ConfigVars.dbvars['host'],
                port=ConfigVars.dbvars['port']
            )
            cls.cur = cls.conn.cursor()
            cls.createTables()
    
    @classmethod
    def getConnection(cls):
        DBConnection.dbConnect()
        return cls.conn
    
    @classmethod
    def createTables(cls):
        DBConnection.dbConnect()
        
        cls.cur.execute(f"CREATE TABLE IF NOT EXISTS {ConfigVars.ownerTable} ({cls.ownerCols[0][0]} {cls.ownerCols[0][1]}, {cls.ownerCols[1][0]} {cls.ownerCols[1][1]});")
        
        cls.cur.execute(f"CREATE TABLE IF NOT EXISTS {ConfigVars.petTable} ({cls.petCols[0][0]} {cls.petCols[0][1]}, {cls.petCols[1][0]} {cls.petCols[1][1]}, {cls.petCols[2][0]} {cls.petCols[2][1]}, {cls.petCols[3][0]} {cls.petCols[3][1]};")
        
        cls.cur.execute(f"CREATE TABLE IF NOT EXISTS {ConfigVars.ownershipTable} ({cls.ownershipCols[0][0]} {cls.ownershipCols[0][1]}, {cls.ownershipCols[1][0]} {cls.ownershipCols[1][1]}, {cls.ownershipCons[0]}, {cls.ownershipCons[1]};")
        cls.conn.commit()
    
    @classmethod
    def selectTable(cls, tname, condition = None, additions = ''):
        DBConnection.dbConnect()
        if condition:
            cls.cur.execute(f"SELECT * FROM {tname} WHERE {condition}{additions};")
        else:
            cls.cur.execute(f"SELECT * FROM {tname}{additions};")
        rows = cls.cur.fetchall()
        return rows
    
    @classmethod
    def insertTable(cls, tname, params):
        DBConnection.dbConnect()
        if len(params) == 1:
            cls.cur.execute(f"INSERT INTO {tname}({cls.ownerCols[1][0]}) VALUES ('{params[0]}');")
        elif len(params) == 3:
            cls.cur.execute(f"INSERT INTO {tname} ({cls.petCols[1][0]}, {cls.petCols[2][0]}, {cls.petCols[3][0]}) VALUES ('{params[0]}', {params[1]}, '{params[2]}');")
        else:
            cls.cur.execute(f"INSERT INTO {tname} VALUES ({params[0]}, {params[1]});")
        cls.conn.commit()
    
    @classmethod
    def deleteTable(cls, tname, condition=None):
        DBConnection.dbConnect()
        if condition:
            cls.cur.execute(f"DELETE FROM {tname} WHERE {condition};")
        cls.conn.commit()
    
    @classmethod
    def updateTable(cls, tname, setCols=None, condition=None):
        DBConnection.dbConnect()
        if setCols and condition:
            cls.cur.execute(f"UPDATE {tname} SET {setCols} WHERE {condition}")
        cls.conn.commit()
    
    @classmethod
    def closeDbConnection(cls):
        if cls.conn:
            cls.cur.close()
            cls.conn.close()
            cls.cur = None
            cls.conn = None