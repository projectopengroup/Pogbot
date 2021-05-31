import sqlite3
import base64
import os


def get_or_request_token():
    # Making our connection to the sqllite3 database.
    conn = sqlite3.connect('prefs.db')
    # Setting this connection to strings/
    conn.text_factory = str
    # Creating our SQL cursor.
    cur = conn.cursor()
    # Executing a query that selects everything from the table called configs.
    cur.execute('SELECT * FROM configs')
    # Pulling data from the cursor by fetching everything.
    data = cur.fetchall()
    # Setting the bot token variable by looking for the second columns value in the data.
    BotToken = (data[0][1])
    # If the BotToken is it's default value of "None" then do this stuff.
    if "None" not in BotToken:
        print("Status: Bot token found! Loading bot...'")
        # Convert base64 string to bytes
        base64_bytes = BotToken.encode("ascii")
        # Decode base64 bytes to bytes
        fromBytes = base64.b64decode(base64_bytes)
        # Convert to string
        BotToken = fromBytes.decode("ascii")
    else:
        print("Status: No bot token found!, prompting user for input")
        # Request bot token from user input.
        BotToken = input("Enter bot token: ")
        # Change string to bytes
        toBytes = BotToken.encode("ascii")
        # Make bytes base64
        base64_bytes = base64.b64encode(toBytes)
        # Change bytes back to a base64 encoded string
        base64_token = base64_bytes.decode("ascii")
        # Update the database with the provided BotToken in Base64.
        cur.execute(f"UPDATE configs SET BotToken = '{base64_token}' WHERE BotToken = 'None'")
        # Commit the database changes.
        conn.commit()

    # Close the database connection
    conn.close()
    return BotToken


def reset_token(bottoken):
    # Pull up the database again
    conn = sqlite3.connect('prefs.db')
    # Create our SQL cursor.
    cur = conn.cursor()
    # Reset our Token to "None"
    cur.execute(f"UPDATE configs SET BotToken = 'None' WHERE BotToken = '{bottoken}'")
    # Commit Database
    conn.commit()
    # Close Database
    conn.close()
