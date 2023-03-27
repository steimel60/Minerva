from typing import Optional
import sqlite3

import db

# make this enum
SQL_QUERIES = {
    "customer purchases": """
        SELECT 
            c.name, 
            fg.name, fg.cost, 
            p.units_ordered,
            fg.cost * p.units_ordered as cost,
            p.date 
        FROM purchase as p 
        JOIN customer as c on p.cid = c.id 
        JOIN finished_good as fg on p.fgid = fg.id 
        WHERE c.name = ?
    """,
}

def get_customer_purchases(
    conn: sqlite3.Connection,
    customer: str
) -> Optional[tuple]:
    return db.generate_sql_result(
        conn, 
        SQL_QUERIES["customer purchases"], 
        (customer,)
    )