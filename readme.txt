Create table in with name erp_app.db # Manual process 
qlite3 erp_app.db
sqlite> CREATE TABLE users (
   ...> id INTEGER PRIMARY KEY AUTOINCREMENT,
   ...> username TEXT UNIQUE NOT NULL,
   ...> password TEXT NOT NULL,
   ...> role TEXT NOT NULL
   ...> );
