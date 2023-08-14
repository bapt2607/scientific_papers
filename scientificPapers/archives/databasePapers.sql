select * from articles;
select * from links;
select * from articles;
select * from authors;
select * from author_article;
DELETE FROM articles;
ALTER TABLE database_name.articles
MODIFY id INT NOT NULL AUTO_INCREMENT PRIMARY KEY;
ALTER TABLE articles ADD COLUMN original_article_id INT REFERENCES articles(id);
ALTER TABLE `database_name`.`articles`
DROP FOREIGN KEY `articles_ibfk_1`;



ALTER TABLE AuthorArticle
MODIFY article_id INT NOT NULL AUTO_INCREMENT;
ALTER TABLE `database_name`.`articles` AUTO_INCREMENT = 0;

-- Disable foreign key checks
SET FOREIGN_KEY_CHECKS = 0;

-- Perform the TRUNCATE operation
TRUNCATE TABLE links;
TRUNCATE TABLE articles;
TRUNCATE TABLE authors;
truncate table author_article;
-- Re-enable foreign key checks
SET FOREIGN_KEY_CHECKS = 1;
INSERT INTO articles (id, url) VALUES
(1,'https://peerj.com/articles/15572/');
DESCRIBE author_article;
ALTER TABLE articles MODIFY title text NULL;
TRUNCATE TABLE articles;
TRUNCATE TABLE links;
INSERT INTO links (source_id, reference_url) VALUES
(1, 'https://onlinelibrary.wiley.com/doi/10.1111/1759-7714.13603');
INSERT INTO links (source_id, reference_url) VALUES
(1, 'https://peerj.com/articles/15572/');
INSERT INTO links (source_id, reference_url) VALUES
(2, 'https://peerj.com/articles/15762/');


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
ALTER TABLE articles DROP link_id;

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
ALTER TABLE articles
DROP FOREIGN KEY articles_ibfk_1;
SHOW CREATE TABLE articles;

ALTER TABLE authors
DROP COLUMN articles_id;
SELECT *
FROM `database_name`.`articles` a
INNER JOIN `database_name`.`AuthorArticle` aa ON a.id = aa.article_id
WHERE aa.author_id = 1;
SELECT *
FROM `database_name`.`authors` a
INNER JOIN `database_name`.`author_article` aa ON a.id = aa.author_id
WHERE aa.article_id = 3;
SELECT *
FROM articles
where original_article_id=1;


SELECT a.*
FROM `database_name`.`articles` a
INNER JOIN `database_name`.`AuthorArticle` aa ON a.id = aa.article_id
INNER JOIN `database_name`.`authors` auth ON aa.author_id = auth.id
WHERE auth.first_name = 'Lili';

SELECT auth.*
FROM `database_name`.`authors` auth
INNER JOIN `database_name`.`author_article` aa ON auth.id = aa.author_id
INNER JOIN `database_name`.`articles` a ON aa.article_id = a.id
WHERE a.title = 'Pan-cancer Immunogenomic Analyses Reveal Genotype-Immunophenotype Relationships and Predictors of Response to Checkpoint Blockade';

ALTER TABLE articles ADD author_extraction_successful BOOLEAN;
ALTER TABLE articles DROP COLUMN author_extraction_successful;
CREATE TABLE author_article (
    author_id INT,
    article_id INT,
    FOREIGN KEY (author_id) REFERENCES authors(id),
    FOREIGN KEY (article_id) REFERENCES articles(id),
    PRIMARY KEY (author_id, article_id)
);
        CREATE TABLE IF NOT EXISTS reference_links (
            id INT AUTO_INCREMENT PRIMARY KEY,
            original_article_id INT NOT NULL,
            FOREIGN KEY (original_article_id) REFERENCES articles(id)
        );
ALTER TABLE articles
MODIFY extraction_successful INT;
ALTER TABLE articles
MODIFY extraction_successful INT DEFAULT 0;
ALTER TABLE articles
RENAME COLUMN ref TO reference_parsed;

