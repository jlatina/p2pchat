import pandas as pd
import sqlite3


# create a connection to the SQLite database
conn = sqlite3.connect('p2p_chat.db')

# create the client table
df_client = pd.DataFrame(columns=['IP', 'port', 'status'])
df_client.to_sql('client', conn, if_exists='replace', index=False)

# create the messages table
df_messages = pd.DataFrame(columns=['sender', 'receiver', 'msg', 'time', 'isSent'])
df_messages.to_sql('messages', conn, if_exists='replace', index=False)

# close the connection to the database
conn.close()





