class ConfigVars:
    '''DB config'''
    dbvars = {
        'database': 'postgres',
        'user': 'postgres',
        'password': 'Finserv@2023',
        'host': '127.0.0.1',
        'port': '5432'
    }
    
    '''Table names and col names'''
    ownerTable = 'owners'
    petTable = 'pets'
    ownershipTable = 'ownership'
    tableCols = {
        ownerTable: (
            ('owner_id', 'int generated always as identity primary key'),
            ('owner_name', 'varchar(40) not null')
        ),
        petTable: (
            ('pet_id', 'int generated always as identity primary key'),
            ('pet_name', 'varchar(40) not null'),
            ('pet_price', 'int not null'),
            ('pet_category', 'varchar(40) not null)')
        ),
        ownershipTable: (
            ('owner_id', 'int not null'),
            ('pet_id', 'int not null')
        )
    }
    tableConstraints = {
        ownershipTable: (
            f"constraint fk_owner foreign key ({tableCols[ownershipTable][0][0]}) references {ownerTable} ({tableCols[ownerTable][0][0]}) on delete cascade",
            f"constraint fk_pet foreign key ({tableCols[ownershipTable][1][0]}) references {petTable} ({tableCols[petTable][0][0]}) on delete cascade)"
        )
    }