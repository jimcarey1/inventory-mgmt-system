from piccolo.table import Table
from piccolo.columns import Varchar, Timestamp, Email

import datetime
from enum import Enum

class Role(Enum):
    user = 'user'
    staff = 'staff'
    admin = 'admin'

class User(Table, tablename='users'):
    username = Varchar(length=30, unique=True, index=True)
    email = Email(unique=True)
    password = Varchar()
    role = Varchar(default='user', choices=Role)
    created_on = Timestamp()
    updated_on = Timestamp(auto_update=datetime.datetime.now)