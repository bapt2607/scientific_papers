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
  `title` TEXT NOT NULL,
  `abstract` TEXT NULL DEFAULT NULL,
  `content` TEXT NULL DEFAULT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
AUTO_INCREMENT = 8
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `database_name`.`links`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `database_name`.`links` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `article_url` VARCHAR(1024) NOT NULL,
  `reference_url` VARCHAR(1024) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `reference_url` (`reference_url`(191) ASC) VISIBLE)
ENGINE = InnoDB
AUTO_INCREMENT = 398
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
