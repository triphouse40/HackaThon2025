import sqlite3

# Function for adding money into the account
def add_money(user_id, account_name, amount, database):
    """Add money into a user's account and log the transaction."""
    if amount <= 0:
        return False

    with sqlite3.connect(database) as conn:
        cur = conn.execute("""
            SELECT amount FROM account
            WHERE user_id = ? AND accountName = ?
        """, (user_id, account_name))
        row = cur.fetchone()

        if not row:
            return False  # account not found

        new_balance = row[0] + amount

        # Update the account balance
        conn.execute("""
            UPDATE account
            SET amount = ?, accessDate = CURRENT_TIMESTAMP
            WHERE user_id = ? AND accountName = ?
        """, (new_balance, user_id, account_name))

        # Log the transaction
        conn.execute("""
            INSERT INTO transactions (user_id, accountName, type, amount)
            VALUES (?, ?, 'deposit', ?)
        """, (user_id, account_name, amount))

        return True



# Function for spending money out the account
def withdraw_money(user_id, amount, database, company=None, item=None, account_name="Savings"):
    """
    Withdraw money from a user's account and log the transaction with optional company/item.
    Default account_name is 'Savings'.
    """
    if amount <= 0:
        return False  # invalid amount

    with sqlite3.connect(database) as conn:
        # Make sure to pass a tuple with a comma for single values
        cur = conn.execute("""
            SELECT amount FROM account
            WHERE user_id = ?
        """, (user_id,))
        row = cur.fetchone()

        if not row:
            print("No account found")
            return False  # account not found

        current_balance = row[0]

        if amount > current_balance:
            print("Insufficient funds")
            return False  # insufficient funds

        new_balance = current_balance - amount

        # Update the account balance
        conn.execute("""
            UPDATE account
            SET amount = ?, accessDate = CURRENT_TIMESTAMP
            WHERE user_id = ? AND accountName = ?
        """, (new_balance, user_id, account_name))

        # Log the transaction with optional company and item
        conn.execute("""
            INSERT INTO transactions (user_id, accountName, type, amount, company, item)
            VALUES (?, ?, 'withdraw', ?, ?, ?)
        """, (user_id, account_name, amount, company, item))

        return True



# Getting all the transactions from the user
def get_transaction_history(user_id, database):
    """Fetch all transactions for a given user, ordered by most recent first."""
    with sqlite3.connect(database) as conn:
        cur = conn.execute("""
            SELECT type, amount, company, item, timestamp
            FROM transactions
            WHERE user_id = ?
            ORDER BY timestamp DESC
        """, (user_id,))
        transactions = cur.fetchall()
    return transactions  
