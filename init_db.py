import sqlite3

def init_db():
    conn = sqlite3.connect('schooler.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            name TEXT NOT NULL,
            lastname TEXT NOT NULL,
            email TEXT NOT NULL,
            hash TEXT NOT NULL
        )
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            start TEXT NOT NULL,
            end TEXT NOT NULL,
            description TEXT,
            url TEXT,
            color TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
        CREATE TABLE IF NOT EXISTS subjects (
            subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            subject TEXT NOT NULL,
            teacher TEXT,
            color TEXT,
            average FLOAT,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
        CREATE TABLE IF NOT EXISTS criteria (
            criteria_id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER,
            criteria TEXT NOT NULL,
            percentage INTEGER NOT NULL,
            average FLOAT,
            FOREIGN KEY (subject_id) REFERENCES subjects (subject_id)
            ON DELETE CASCADE
        )
        CREATE TABLE IF NOT EXISTS grades (
            criteria_id INTEGER,
            task TEXT NOT NULL,
            grade INTEGER NOT NULL,
            FOREIGN KEY (criteria_id) REFERENCES criteria (criteria_id)
            ON DELETE CASCADE
        )
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
            ON DELETE CASCADE
        );
       
                          
    ''')
    
    conn.commit()
    conn.close()
    
    if __name__ == '__main__':
        init_db()