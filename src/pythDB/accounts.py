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
def withdraw_money(user_id, account_name, amount, database):
    """Withdraw money from a user's account and log the transaction."""
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

        current_balance = row[0]

        if amount > current_balance:
            return False  # insufficient funds

        new_balance = current_balance - amount

        # Update the account balance
        conn.execute("""
            UPDATE account
            SET amount = ?, accessDate = CURRENT_TIMESTAMP
            WHERE user_id = ? AND accountName = ?
        """, (new_balance, user_id, account_name))

        # Log the transaction
        conn.execute("""
            INSERT INTO transactions (user_id, accountName, type, amount)
            VALUES (?, ?, 'withdraw', ?)
        """, (user_id, account_name, amount))

        return True
