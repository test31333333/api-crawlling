import json
import mysql.connector
def stor_data_in_db():
    with open("test.json", "r", encoding="utf-8") as f:
        articles = json.load(f)

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="cawlling"
    )
    cursor = conn.cursor()

    for article in articles:
        try:
            cursor.execute("""
                INSERT INTO articles (id, url, title, topics, date, image_url, author, content)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                article.get("id"),
                article.get("URL"),
                article.get("Title"),
                article.get("Topics"),
                article.get("Date"),
                article.get("Image URL"),
                article.get("Author"),
                article.get("Content")
            ))
        except Exception as e:
            print(f"Failed to insert article ID {article.get('id')}: {e}")

    conn.commit()
    cursor.close()
    conn.close()

    print("Data inserted into MySQL successfully.")
stor_data_in_db()