import psycopg2
import psycopg2.extras
import json

DB_CONFIG = {
    "dbname": "wikigamer",
    "user": "carterashley-smith",
    "password": "",
    "host": "localhost",
    "port": "5432",
}

def get_conn():
    return psycopg2.connect(**DB_CONFIG)


def save_page(username: str, riot_data: dict, steam_data: dict, sections: list, platform: str = "riot"):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO pages (username, platform, riot_data, steam_data, sections)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (username) DO UPDATE SET
                riot_data = EXCLUDED.riot_data,
                steam_data = EXCLUDED.steam_data,
                sections = EXCLUDED.sections
        """, (
            username,
            platform,
            json.dumps(riot_data),
            json.dumps(steam_data),
            json.dumps(sections),
        ))
        conn.commit()
        return True
    except Exception as e:
        print("DB save error:", e)
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()


def get_page(username: str):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        # Increment view count and return page
        cur.execute("""
            UPDATE pages SET view_count = view_count + 1
            WHERE username = %s
            RETURNING *
        """, (username,))
        row = cur.fetchone()
        conn.commit()
        return dict(row) if row else None
    except Exception as e:
        print("DB get error:", e)
        return None
    finally:
        cur.close()
        conn.close()


def search_pages(query: str) -> list:
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute("""
            SELECT username, platform, view_count, created_at
            FROM pages
            WHERE username ILIKE %s
            ORDER BY view_count DESC
            LIMIT 20
        """, (f"%{query}%",))
        rows = cur.fetchall()
        return [dict(r) for r in rows]
    except Exception as e:
        print("DB search error:", e)
        return []
    finally:
        cur.close()
        conn.close()


def browse_pages(page: int = 1, sort: str = "recent") -> dict:
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        order = "created_at DESC" if sort == "recent" else "view_count DESC"
        offset = (page - 1) * 20
        cur.execute(f"""
            SELECT username, platform, view_count, created_at
            FROM pages
            ORDER BY {order}
            LIMIT 20 OFFSET %s
        """, (offset,))
        rows = cur.fetchall()

        cur.execute("SELECT COUNT(*) FROM pages")
        total = cur.fetchone()["count"]

        return {"results": [dict(r) for r in rows], "total": total}
    except Exception as e:
        print("DB browse error:", e)
        return {"results": [], "total": 0}
    finally:
        cur.close()
        conn.close()