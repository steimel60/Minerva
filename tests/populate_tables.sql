
INSERT INTO account VALUES 
    ('Matt', '123ASDhghj!'),
    ('Dylan', 'fghjkTYUIO6578$$');

INSERT INTO customer (name, contact, billing_address) VALUES
    ('sammy', '704-111-2222', '123 blue whale dr.'),
    ('milo', '987-123-4567', '777 chesterton fence ln.');

INSERT INTO finished_good (name, cost, unit) VALUES
    ('beer', '5.55', 'drum'),
    ('wine', '10.99', 'cask');

INSERT INTO purchase (cid, fgid, units_ordered, date) VALUES
    (1, 1, 2, '2021-10-09'),
    (1, 2, 2, '2021-10-08');