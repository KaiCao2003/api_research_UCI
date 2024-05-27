import random
import sqlite3
import time
import logging
import schedule
from datetime import datetime
from uuid import uuid4
import threading
import mail
import engine

# Setup logging
logging.basicConfig(filename='dataset_log.txt', level=logging.INFO,
                    format='%(asctime)s - %(message)s')

# Create an SQLite database (or connect to it if it exists)
conn = sqlite3.connect('dataset.db', check_same_thread=False)
cursor = conn.cursor()

# Create a table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS dataset (
    code TEXT,
    email TEXT,
    status TEXT,
    id TEXT,
    finished BOOLEAN,
    last_change_time TEXT
)
''')
conn.commit()


# Functions definition
def received(code, email, received_time):
    cursor.execute('SELECT * FROM dataset WHERE code = ? AND finished = ?', (code, False))
    record = cursor.fetchone()

    if record:
        email_list = record[1].split(',')
        if email in email_list:
            logging.info(f"Email {email} already exists for code {code}, not logging.")
            return False
        else:
            email_list.append(email)
            cursor.execute('''
            UPDATE dataset
            SET email = ?, last_change_time = ?
            WHERE code = ? AND finished = ?
            ''', (','.join(email_list), received_time, code, False))
            logging.info(f"Added email {email} to existing code {code}.")
    else:
        cursor.execute('''
        INSERT INTO dataset (code, email, status, id, finished, last_change_time)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (code, email, '', str(uuid4()), False, received_time))
        logging.info(f"Created new record for code {code} with email {email}.")

    conn.commit()
    mail.confirmation_email([email], code)
    return True
  

def give_up(code, email_list, current_time):
    mail.fail_email(code,email_list, current_time)


def check(code):
    status = engine.send_request(code)[4]
    return [code, status]

def add_or_update_record(code, email):
    received_time = datetime.now().isoformat()
    success = received(code, email, received_time)
    if success:
        check_status(code)  # Initial check when record is first added
        schedule.every(1).seconds.do(check_status, code).tag(code)
    return success


def periodic_check():
    cursor.execute('SELECT code FROM dataset WHERE finished = ?', (False,))
    codes = [row[0] for row in cursor.fetchall()]

    for code in codes:
        schedule.every(1).seconds.do(check_status, code).tag(code)


def check_status(code):
    result = check(code)
    status_from_check = result[1]

    cursor.execute('SELECT email, status, finished FROM dataset WHERE code = ? AND finished = ?', (code, False))
    record = cursor.fetchone()

    if record:
        email_list = record[0].split(',')
        status_from_db = record[1]
        finished = record[2]

        if finished:
            logging.info(f"Code {code} already finished")
            return

        if status_from_check in ["OPEN", 'Waitl']:
            if status_from_db == 'FULL' or status_from_db == 'NewOnly:
                success = mail.update_email(email_list, code)
                if success:
                    cursor.execute('UPDATE dataset SET finished = ?, last_change_time = ? WHERE code = ?',
                                   (True, datetime.now().isoformat(), code))
                    conn.commit()
                    logging.info(f"Successfully sent email list for code {code} to {email_list}")
                else:
                    give_up(code, email_list, datetime.now().isoformat())
                    logging.info(f"Failed to send email list for code {code}, gave up")
        # Update the status in the database after comparison
        if status_from_check is not status_from_db:
            cursor.execute('UPDATE dataset SET status = ?, last_change_time = ? WHERE code = ?',
                           (status_from_check, datetime.now().isoformat(), code))
            conn.commit()
            logging.info(f"Updated status for code {code} from {status_from_db} to {status_from_check}")


def run_periodic_check():
    while True:
        schedule.run_pending()
        time.sleep(1)


def initialize_scheduler():
    periodic_check()
    scheduler_thread = threading.Thread(target=run_periodic_check)
    scheduler_thread.daemon = True
    scheduler_thread.start()


initialize_scheduler()
