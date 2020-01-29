# dbreak
A development database debugging tool that lets you set breakpoints and issue direct queries to one or more databases. Extensible via plugins to allow you to query a wide range of database types, both SQL and NoSQL.

Requires Python 3.6+

## Installation
Install from PyPi using pip:

```
pip install dbreak
```
The base dbreak package includes support for DB API-compliant connections, such as the following:

* sqlite3 (built-in)
* psycopg2
* pymysql

Add support for additional connection types by installing plugins:

* [dbreak-sqlalchemy](https://github.com/jrhege/dbreak-sqlalchemy)
* [dbreak-redis](https://github.com/jrhege/dbreak-redis)

## Usage
Your main interaction will be with the show_console() function. This pauses the application and lets you query any database connections you've provided.

### Basic Usage
Example using a SQLite in-memory database:
```
import sqlite3
import dbreak

# Set up a SQLite connection as you normally would
connection = sqlite3.connect(":memory:")

# Add a table
connection.execute("create table foobar(x int, y int)")

# Add a row
connection.execute("insert into foobar select 1, 2")

# Pause execution and enter the console
dbreak.start_console(connection)
```

Once the start_console command is encountered you'll enter an interactive console where you can query the database using the connections you've provided:

```
Starting debug session on connection 'db[0]'.
You may issue database commands by simply typing them and pressing enter.

Use !help for a list of special commands.
Use !exit to quit the debugger and resume the application.

db[0]> select * from foobar

===  ===
  x    y
===  ===
  1    2
===  ===
(1 row(s) returned)
```

### Multiple Connections
If you have multiple database connections, you can name them via arguments to the show_console() command for easier access in the shell. Connections can be of the same type or different (for example, one shell could handle connections to both MySQL and Redis databases).

Example using two SQLite connections:

```
import sqlite3
import dbreak

# Set up a couple of SQLite connections
connection1 = sqlite3.connect(":memory:")
connection2 = sqlite3.connect(":memory:")

# Pause execution and enter the console
dbreak.start_console(
    conn1=connection1,
    conn2=connection2,
    starting_connection="conn1"
)
```
The `starting_connection` parameter takes a string that indicates what connection the shell should use initially. The other parameters act as names for the connections and can be anything you want.
 
Once inside the shell you can then use special commands (described via !help) to list and switch between the connections:

```
Starting debug session on connection 'conn1'.
You may issue database commands by simply typing them and pressing enter.

Use !help for a list of special commands.
Use !exit to quit the debugger and resume the application.

conn1> !connections

=================  ==============  =======================  ======================
Connection Name    Wrapper Type    Raw Connection Module    Raw Connection Class
=================  ==============  =======================  ======================
conn1              DBAPIWrapper    sqlite3                  Connection
conn2              DBAPIWrapper    sqlite3                  Connection
=================  ==============  =======================  ======================
(2 row(s) returned)

conn1> !switch conn2
conn2> 
```
Note that the name of the current connection is shown at the input prompt.