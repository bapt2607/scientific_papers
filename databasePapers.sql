select * from articles;
select * from links;
DELETE FROM articles;

TRUNCATE TABLE articles;
TRUNCATE TABLE links;
INSERT INTO links (source_id, reference_url) VALUES
(1, 'https://peerj.com/articles/15572/');

ALTER TABLE links ADD UNIQUE (reference_url(191));
ALTER TABLE links DROP FOREIGN KEY source_id;
SHOW CREATE TABLE links;
SELECT reference_url, COUNT(*)
FROM links
GROUP BY reference_url
HAVING COUNT(*) > 1;

CREATE TABLE articles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    url VARCHAR(1024) NOT NULL,
    title TEXT NOT NULL,
    abstract TEXT,
    content TEXT
);

ALTER TABLE links
CHANGE COLUMN article_url source_id INT NOT NULL;
ALTER TABLE articles
ADD COLUMN extraction_successful BOOLEAN DEFAULT FALSE;
ALTER TABLE articles
ADD COLUMN reference_extraction_successful BOOLEAN DEFAULT FALSE;

ALTER TABLE articles
ADD COLUMN links_id INT;
ALTER TABLE articles
ADD FOREIGN KEY (links_id) REFERENCES links(id);

ALTER TABLE authors
ADD COLUMN articles_id INT;
ALTER TABLE authors
ADD FOREIGN KEY (articles_id) REFERENCES articles(id);

SET SQL_SAFE_UPDATES = 0;
DELETE FROM articles;
SET SQL_SAFE_UPDATES = 1;
ALTER TABLE links DROP FOREIGN KEY links_ibfk_1;

CREATE TABLE authors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    affiliation VARCHAR(255),
    email VARCHAR(255)
);

ALTER USER 'root'@'localhost' IDENTIFIED BY '';
UNINSTALL PLUGIN validate_password;
ALTER USER 'root'@'localhost' IDENTIFIED BY '12345678';
INSTALL PLUGIN validate_password SONAME 'validate_password.so';

SET GLOBAL validate_password.policy = LOW;
ALTER USER 'user_name'@'localhost' IDENTIFIED BY '';
SET GLOBAL validate_password.policy = MEDIUM;  -- Ou la valeur que vous aviez précédemment

