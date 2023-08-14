-- MySQL Script generated by MySQL Workbench
-- lun. 14 août 2023 10:18:50
-- Model: New Model    Version: 1.0
-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema database_name
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema database_name
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `database_name` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci ;
USE `database_name` ;

-- -----------------------------------------------------
-- Table `database_name`.`articles`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `database_name`.`articles` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `url` VARCHAR(1024) NOT NULL,
  `title` TEXT NULL DEFAULT NULL,
  `abstract` TEXT NULL DEFAULT NULL,
  `content` TEXT NULL DEFAULT NULL,
  `parsed` INT NULL DEFAULT '0',
  `reference_parsed` TINYINT(1) NULL DEFAULT '0',
  `original_article_id` INT NULL DEFAULT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
AUTO_INCREMENT = 542
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `database_name`.`authors`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `database_name`.`authors` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `first_name` VARCHAR(255) NULL DEFAULT NULL,
  `last_name` VARCHAR(255) NULL DEFAULT NULL,
  `affiliation` VARCHAR(255) NULL DEFAULT NULL,
  `email` VARCHAR(255) NULL DEFAULT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
AUTO_INCREMENT = 138
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `database_name`.`author_article`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `database_name`.`author_article` (
  `author_id` INT NOT NULL,
  `article_id` INT NOT NULL,
  PRIMARY KEY (`author_id`, `article_id`),
  INDEX `article_id` (`article_id` ASC) VISIBLE,
  CONSTRAINT `author_article_ibfk_1`
    FOREIGN KEY (`author_id`)
    REFERENCES `database_name`.`authors` (`id`),
  CONSTRAINT `author_article_ibfk_2`
    FOREIGN KEY (`article_id`)
    REFERENCES `database_name`.`articles` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
