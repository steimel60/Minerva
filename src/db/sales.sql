CREATE TABLE IF NOT EXISTS customer (
    id INTEGER PRIMARY KEY,
    name TEXT,
    contact TEXT,
    billing_address TEXT
);

-- could make cost/unit pair an object
CREATE TABLE IF NOT EXISTS finished_good (
    id INTEGER PRIMARY KEY,
    name TEXT,
    cost REAL, -- per unit
    unit TEXT 
);

CREATE TABLE IF NOT EXISTS purchase (
    id INTEGER PRIMARY KEY,
    cid INTEGER,
    fgid INTEGER,
    units_ordered REAL,
    date TEXT, -- Enforce conformity to ISO-8601, use SQLITE funcs
    FOREIGN KEY(cid) REFERENCES Customer(id),
    FOREIGN KEY(fgid) REFERENCES FinishedGoods(id)
);