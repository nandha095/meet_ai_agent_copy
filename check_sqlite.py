import sqlite3

conn = sqlite3.connect("meeting_agent.db")
cursor = conn.cursor()

print("📦 Tables:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
print(cursor.fetchall())

print("\n📧 Google tokens:")
cursor.execute("SELECT * FROM google_tokens")
print(cursor.fetchall())

print("\n📨 Outlook tokens:")
cursor.execute("SELECT * FROM outlook_tokens")
print(cursor.fetchall())

print("\n📄 Proposals:")
cursor.execute("SELECT id, status, provider FROM proposals")
print(cursor.fetchall())

conn.close()
