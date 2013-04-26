SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

DROP SCHEMA IF EXISTS `uspto_patents` ;
CREATE SCHEMA IF NOT EXISTS `uspto_patents` DEFAULT CHARACTER SET utf8 ;
USE `uspto_patents` ;

-- -----------------------------------------------------
-- Table `uspto_patents`.`APPLICATION_PAIR`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `uspto_patents`.`APPLICATION_PAIR` ;

CREATE  TABLE IF NOT EXISTS `uspto_patents`.`APPLICATION_PAIR` (
  `ApplicationID` VARCHAR(20) NOT NULL COMMENT 'Application Number/ Document ID' ,
  `FileDate` DATE NULL ,
  `AppType` VARCHAR(45) NULL COMMENT 'Application Type' ,
  `ExaminerName` VARCHAR(100) NULL ,
  `GroupArtUnit` VARCHAR(45) NULL ,
  `ConfirmationNum` VARCHAR(45) NULL ,
  `AttorneyDNum` VARCHAR(45) NULL ,
  `ClassSubclass` VARCHAR(45) NULL ,
  `InventorFName` VARCHAR(100) NULL ,
  `CustomerNum` VARCHAR(45) NULL ,
  `Status` VARCHAR(200) NULL ,
  `StatusDate` DATE NULL ,
  `Location` VARCHAR(100) NULL ,
  `LocationDate` DATE NULL ,
  `PubNoEarliest` VARCHAR(45) NULL ,
  `PubDateEarliest` DATE NULL ,
  `PatentNum` VARCHAR(45) NULL ,
  `PatentIssueDate` DATE NULL ,
  `TitleInvention` VARCHAR(500) NULL ,
  PRIMARY KEY (`ApplicationID`) )
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `uspto_patents`.`GRANTS`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `uspto_patents`.`GRANTS` ;

CREATE  TABLE IF NOT EXISTS `uspto_patents`.`GRANTS` (
  `GrantID` VARCHAR(20) NOT NULL ,
  `Title` VARCHAR(500) NULL ,
  `IssueDate` DATE NULL ,
  `Kind` VARCHAR(2) NULL ,
  `USSeriesCode` VARCHAR(2) NULL ,
  `Abstract` TEXT NULL ,
  `ClaimsNum` INT NULL ,
  `DrawingsNum` INT NULL ,
  `FiguresNum` INT NULL ,
  `ApplicationID` VARCHAR(20) NOT NULL ,
  `Claims` TEXT NULL ,
  `FileDate` DATE NULL ,
  `AppType` VARCHAR(45) NULL ,
  `AppNoOrig` VARCHAR(10) NULL ,
  `SourceName` VARCHAR(100) NULL ,
  PRIMARY KEY (`GrantID`) )
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `uspto_patents`.`PUBLICATIONS`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `uspto_patents`.`PUBLICATIONS` ;

CREATE  TABLE IF NOT EXISTS `uspto_patents`.`PUBLICATIONS` (
  `PublicationID` VARCHAR(20) NOT NULL ,
  `Title` VARCHAR(500) NULL ,
  `PublishDate` DATE NULL ,
  `Kind` VARCHAR(2) NULL ,
  `USSeriesCode` VARCHAR(2) NULL ,
  `Abstract` TEXT NULL ,
  `ClaimsNum` INT NULL ,
  `DrawingsNum` INT NULL ,
  `FiguresNum` INT NULL ,
  `ApplicationID` VARCHAR(20) NOT NULL ,
  `Claims` TEXT NULL ,
  `FileDate` DATE NULL ,
  `AppType` VARCHAR(45) NULL ,
  `SourceName` VARCHAR(100) NULL ,
  PRIMARY KEY (`PublicationID`) )
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `uspto_patents`.`INTCLASS_P`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `uspto_patents`.`INTCLASS_P` ;

CREATE  TABLE IF NOT EXISTS `uspto_patents`.`INTCLASS_P` (
  `PublicationID` VARCHAR(20) NOT NULL ,
  `Position` INT NOT NULL ,
  `Section` VARCHAR(10) NULL ,
  `Class` VARCHAR(20) NULL ,
  `Subclass` VARCHAR(10) NULL ,
  `MainGroup` VARCHAR(10) NULL ,
  `SubGroup` VARCHAR(10) NULL ,
  PRIMARY KEY (`PublicationID`, `Position`) ,
  INDEX `fk_publicationid_PUBLICATION_INTERNATIONALCLASS_P` (`PublicationID` ASC) ,
  CONSTRAINT `fk_publicationid_PUBLICATION_INTERNATIONALCLASS_P`
    FOREIGN KEY (`PublicationID` )
    REFERENCES `uspto_patents`.`PUBLICATIONS` (`PublicationID` )
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `uspto_patents`.`USCLASS_P`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `uspto_patents`.`USCLASS_P` ;

CREATE  TABLE IF NOT EXISTS `uspto_patents`.`USCLASS_P` (
  `PublicationID` VARCHAR(20) NOT NULL COMMENT 'WorkingNo' ,
  `Position` INT NOT NULL ,
  `Class` VARCHAR(3) NULL ,
  `Subclass` VARCHAR(6) NULL ,
  PRIMARY KEY (`PublicationID`, `Position`) ,
  INDEX `fk_publicationid_PUBLICATION_USCLASS_P` (`PublicationID` ASC) ,
  CONSTRAINT `fk_publicationid_PUBLICATION_USCLASS_P`
    FOREIGN KEY (`PublicationID` )
    REFERENCES `uspto_patents`.`PUBLICATIONS` (`PublicationID` )
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `uspto_patents`.`INVENTOR_P`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `uspto_patents`.`INVENTOR_P` ;

CREATE  TABLE IF NOT EXISTS `uspto_patents`.`INVENTOR_P` (
  `PublicationID` VARCHAR(20) NOT NULL ,
  `Position` INT NOT NULL ,
  `FirstName` VARCHAR(100) NULL ,
  `LastName` VARCHAR(100) NULL ,
  `City` VARCHAR(100) NULL ,
  `State` VARCHAR(100) NULL ,
  `Country` VARCHAR(100) NULL ,
  `Nationality` VARCHAR(100) NULL ,
  `Residence` VARCHAR(100) NULL COMMENT 'Residence Country' ,
  PRIMARY KEY (`PublicationID`, `Position`) ,
  INDEX `fk_PublicationID_Inventor_p` (`PublicationID` ASC) ,
  CONSTRAINT `fk_PublicationID_Inventor_p`
    FOREIGN KEY (`PublicationID` )
    REFERENCES `uspto_patents`.`PUBLICATIONS` (`PublicationID` )
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `uspto_patents`.`ATTORNEY`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `uspto_patents`.`ATTORNEY` ;

CREATE  TABLE IF NOT EXISTS `uspto_patents`.`ATTORNEY` (
  `ApplicationID` VARCHAR(20) NOT NULL ,
  `Position` INT NOT NULL ,
  `RegNo` VARCHAR(20) NULL ,
  `FirstName` VARCHAR(45) NULL ,
  `LastName` VARCHAR(45) NULL ,
  `Phone` VARCHAR(45) NULL ,
  PRIMARY KEY (`ApplicationID`, `Position`) ,
  INDEX `FK_ApplicationID_APPLICATION_ATTORNEY` (`ApplicationID` ASC) ,
  CONSTRAINT `FK_ApplicationID_APPLICATION_ATTORNEY`
    FOREIGN KEY (`ApplicationID` )
    REFERENCES `uspto_patents`.`APPLICATION_PAIR` (`ApplicationID` )
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `uspto_patents`.`FOREIGNPRIORITY`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `uspto_patents`.`FOREIGNPRIORITY` ;

CREATE  TABLE IF NOT EXISTS `uspto_patents`.`FOREIGNPRIORITY` (
  `ApplicationID` VARCHAR(20) NOT NULL ,
  `Position` INT NOT NULL ,
  `Country` VARCHAR(100) NULL ,
  `Priority` VARCHAR(45) NULL ,
  `PriorityDate` DATE NULL ,
  INDEX `fk_applicationid_foreignpriority` (`ApplicationID` ASC) ,
  PRIMARY KEY (`ApplicationID`, `Position`) ,
  CONSTRAINT `fk_applicationid_foreignpriority`
    FOREIGN KEY (`ApplicationID` )
    REFERENCES `uspto_patents`.`APPLICATION_PAIR` (`ApplicationID` )
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `uspto_patents`.`TRANSACTION`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `uspto_patents`.`TRANSACTION` ;

CREATE  TABLE IF NOT EXISTS `uspto_patents`.`TRANSACTION` (
  `ApplicationID` VARCHAR(20) NOT NULL ,
  `Position` INT NOT NULL ,
  `Description` TINYTEXT NULL ,
  `Date` DATE NULL ,
  INDEX `fk_applicationid_transaction` (`ApplicationID` ASC) ,
  PRIMARY KEY (`ApplicationID`, `Position`) ,
  CONSTRAINT `fk_applicationid_transaction`
    FOREIGN KEY (`ApplicationID` )
    REFERENCES `uspto_patents`.`APPLICATION_PAIR` (`ApplicationID` )
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `uspto_patents`.`CORRESPONDENCE`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `uspto_patents`.`CORRESPONDENCE` ;

CREATE  TABLE IF NOT EXISTS `uspto_patents`.`CORRESPONDENCE` (
  `ApplicationID` VARCHAR(20) NOT NULL ,
  `Name` VARCHAR(100) NULL ,
  `Address` TINYTEXT NULL ,
  `CustomerNum` VARCHAR(45) NULL ,
  PRIMARY KEY (`ApplicationID`) ,
  INDEX `FK_ApplicationID_APPLICATION_CORRESPONDENCE` (`ApplicationID` ASC) ,
  CONSTRAINT `FK_ApplicationID_APPLICATION_CORRESPONDENCE`
    FOREIGN KEY (`ApplicationID` )
    REFERENCES `uspto_patents`.`APPLICATION_PAIR` (`ApplicationID` )
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `uspto_patents`.`CONTINUITY_PARENT`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `uspto_patents`.`CONTINUITY_PARENT` ;

CREATE  TABLE IF NOT EXISTS `uspto_patents`.`CONTINUITY_PARENT` (
  `ApplicationID` VARCHAR(20) NOT NULL ,
  `Position` INT NOT NULL ,
  `Description` VARCHAR(100) NULL ,
  `ParentNum` VARCHAR(45) NULL ,
  `FileDate` DATE NULL ,
  `ParentStatus` VARCHAR(45) NULL ,
  `PatentNum` VARCHAR(45) NULL ,
  INDEX `FK_ApplicationID_CONTINUITY_PARENT` (`ApplicationID` ASC) ,
  PRIMARY KEY (`Position`, `ApplicationID`) ,
  CONSTRAINT `FK_ApplicationID_CONTINUITY_PARENT`
    FOREIGN KEY (`ApplicationID` )
    REFERENCES `uspto_patents`.`APPLICATION_PAIR` (`ApplicationID` )
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `uspto_patents`.`CONTINUITY_CHILD`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `uspto_patents`.`CONTINUITY_CHILD` ;

CREATE  TABLE IF NOT EXISTS `uspto_patents`.`CONTINUITY_CHILD` (
  `ApplicationID` VARCHAR(20) NOT NULL ,
  `Position` INT NOT NULL ,
  `Description` TINYTEXT NULL ,
  INDEX `FK_ApplicationID_CONTINUITY_CHILD` (`ApplicationID` ASC) ,
  PRIMARY KEY (`ApplicationID`, `Position`) ,
  CONSTRAINT `FK_ApplicationID_CONTINUITY_CHILD`
    FOREIGN KEY (`ApplicationID` )
    REFERENCES `uspto_patents`.`APPLICATION_PAIR` (`ApplicationID` )
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `uspto_patents`.`ADJUSTMENT`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `uspto_patents`.`ADJUSTMENT` ;

CREATE  TABLE IF NOT EXISTS `uspto_patents`.`ADJUSTMENT` (
  `ApplicationID` VARCHAR(20) NOT NULL ,
  `PriorAfter` TINYINT(1) NULL COMMENT 'prior to August 28, 2010 OR After' ,
  `FileDate` DATE NULL ,
  `IssueDate` DATE NULL ,
  `PreIssuePetitions` VARCHAR(45) NULL ,
  `PostIssuePetitions` VARCHAR(45) NULL ,
  `USPTOAdjustDays` VARCHAR(45) NULL ,
  `USPTODelayDays` VARCHAR(45) NULL ,
  `ThreeYears` VARCHAR(45) NULL ,
  `APPLDelayDays` VARCHAR(45) NULL ,
  `TotalTermAdjustDays` VARCHAR(45) NULL ,
  `ADelays` VARCHAR(45) NULL ,
  `BDelays` VARCHAR(45) NULL ,
  `CDelays` VARCHAR(45) NULL ,
  `OverlapDays` VARCHAR(45) NULL ,
  `NonOverlapDelays` VARCHAR(45) NULL ,
  `PTOManualAdjust` VARCHAR(45) NULL ,
  PRIMARY KEY (`ApplicationID`) ,
  INDEX `FK_ApplicationID_APPLICATION_ADJUSTMENT` (`ApplicationID` ASC) ,
  CONSTRAINT `FK_ApplicationID_APPLICATION_ADJUSTMENT`
    FOREIGN KEY (`ApplicationID` )
    REFERENCES `uspto_patents`.`APPLICATION_PAIR` (`ApplicationID` )
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `uspto_patents`.`ADJUSTMENTDESC`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `uspto_patents`.`ADJUSTMENTDESC` ;

CREATE  TABLE IF NOT EXISTS `uspto_patents`.`ADJUSTMENTDESC` (
  `ApplicationID` VARCHAR(20) NOT NULL ,
  `Position` INT NOT NULL COMMENT 'after: Number	Date	Contents Description	      PTO(Days)    APPL(Days)	Start \\\\n   prior: Date	Contents Description	PTO(Days)	APPL(Days)' ,
  `PriorAfter` TINYINT(1) NULL ,
  `Number` INT NULL ,
  `Date` DATE NULL ,
  `ContentDesc` TINYTEXT NULL ,
  `PTODays` VARCHAR(45) NULL ,
  `APPLDays` VARCHAR(45) NULL ,
  `Start` VARCHAR(45) NULL ,
  PRIMARY KEY (`ApplicationID`, `Position`) ,
  INDEX `FK_ApplicationID_APPLICATION_ADJUSTMENTDESC` (`ApplicationID` ASC) ,
  CONSTRAINT `FK_ApplicationID_APPLICATION_ADJUSTMENTDESC`
    FOREIGN KEY (`ApplicationID` )
    REFERENCES `uspto_patents`.`APPLICATION_PAIR` (`ApplicationID` )
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `uspto_patents`.`EXTENSION`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `uspto_patents`.`EXTENSION` ;

CREATE  TABLE IF NOT EXISTS `uspto_patents`.`EXTENSION` (
  `ApplicationID` VARCHAR(20) NOT NULL ,
  `FileDate` DATE NULL ,
  `USPTOAdjustDays` INT NULL ,
  `USPTODelays` INT NULL ,
  `CorrectDelays` INT NULL ,
  `TotalExtensionDays` INT NULL ,
  PRIMARY KEY (`ApplicationID`) ,
  INDEX `FK_ApplicatoinID_APPLICATION_EXTENSION` (`ApplicationID` ASC) ,
  CONSTRAINT `FK_ApplicatoinID_APPLICATION_EXTENSION`
    FOREIGN KEY (`ApplicationID` )
    REFERENCES `uspto_patents`.`APPLICATION_PAIR` (`ApplicationID` )
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `uspto_patents`.`EXTENSIONDESC`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `uspto_patents`.`EXTENSIONDESC` ;

CREATE  TABLE IF NOT EXISTS `uspto_patents`.`EXTENSIONDESC` (
  `ApplicationID` VARCHAR(20) NOT NULL ,
  `Position` INT NOT NULL ,
  `Date` DATE NULL ,
  `Description` TINYTEXT NULL ,
  `PTODays` VARCHAR(45) NULL ,
  `APPLDays` VARCHAR(45) NULL ,
  PRIMARY KEY (`ApplicationID`, `Position`) ,
  INDEX `FK_ApplicationID_APPLICAITON_EXTENSIONDESC` (`ApplicationID` ASC) ,
  CONSTRAINT `FK_ApplicationID_APPLICAITON_EXTENSIONDESC`
    FOREIGN KEY (`ApplicationID` )
    REFERENCES `uspto_patents`.`APPLICATION_PAIR` (`ApplicationID` )
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `uspto_patents`.`AGENT_P`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `uspto_patents`.`AGENT_P` ;

CREATE  TABLE IF NOT EXISTS `uspto_patents`.`AGENT_P` (
  `PublicationID` VARCHAR(20) NOT NULL COMMENT 'attorney' ,
  `Position` INT NOT NULL ,
  `OrgName` VARCHAR(200) NULL ,
  `LastName` VARCHAR(100) NULL ,
  `FirstName` VARCHAR(100) NULL ,
  `Country` VARCHAR(100) NULL ,
  PRIMARY KEY (`PublicationID`, `Position`) ,
  INDEX `FK_PublicationID_PUBLICATION_AGENT_P` (`PublicationID` ASC) ,
  CONSTRAINT `FK_PublicationID_PUBLICATION_AGENT_P`
    FOREIGN KEY (`PublicationID` )
    REFERENCES `uspto_patents`.`PUBLICATIONS` (`PublicationID` )
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `uspto_patents`.`ASSIGNEE_P`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `uspto_patents`.`ASSIGNEE_P` ;

CREATE  TABLE IF NOT EXISTS `uspto_patents`.`ASSIGNEE_P` (
  `PublicationID` VARCHAR(20) NOT NULL ,
  `Position` INT NOT NULL ,
  `OrgName` VARCHAR(200) NULL COMMENT '\\\"United States of America as represented by the Administrator of the National Aeronautics and Space Administration\\\" >100' ,
  `Role` VARCHAR(45) NULL ,
  `City` VARCHAR(100) NULL ,
  `State` VARCHAR(100) NULL ,
  `Country` VARCHAR(100) NULL ,
  PRIMARY KEY (`PublicationID`, `Position`) ,
  INDEX `FK_PublicationID_PUBLICATION_ASSIGNEE_P` (`PublicationID` ASC) ,
  CONSTRAINT `FK_PublicationID_PUBLICATION_ASSIGNEE_P`
    FOREIGN KEY (`PublicationID` )
    REFERENCES `uspto_patents`.`PUBLICATIONS` (`PublicationID` )
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `uspto_patents`.`EXAMINER_P`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `uspto_patents`.`EXAMINER_P` ;

CREATE  TABLE IF NOT EXISTS `uspto_patents`.`EXAMINER_P` (
  `PublicationID` VARCHAR(20) NOT NULL ,
  `Position` INT NOT NULL ,
  `LastName` VARCHAR(100) NULL ,
  `FirstName` VARCHAR(100) NULL ,
  `Department` VARCHAR(100) NULL ,
  PRIMARY KEY (`PublicationID`, `Position`) ,
  INDEX `fk_publicationid_Publication_Examiner_p` (`PublicationID` ASC) ,
  CONSTRAINT `fk_publicationid_Publication_Examiner_p`
    FOREIGN KEY (`PublicationID` )
    REFERENCES `uspto_patents`.`PUBLICATIONS` (`PublicationID` )
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `uspto_patents`.`NONPATCIT_P`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `uspto_patents`.`NONPATCIT_P` ;

CREATE  TABLE IF NOT EXISTS `uspto_patents`.`NONPATCIT_P` (
  `PublicationID` VARCHAR(20) NOT NULL ,
  `Position` INT NOT NULL ,
  `Citation` TEXT NULL ,
  `Category` VARCHAR(100) NULL ,
  INDEX `fk_PublicationID_PUBLICATION_NPCITATION_P` (`PublicationID` ASC) ,
  PRIMARY KEY (`PublicationID`, `Position`) ,
  CONSTRAINT `fk_PublicationID_PUBLICATION_NPCITATION_P`
    FOREIGN KEY (`PublicationID` )
    REFERENCES `uspto_patents`.`PUBLICATIONS` (`PublicationID` )
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `uspto_patents`.`USCLASSIFICATION`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `uspto_patents`.`USCLASSIFICATION` ;

CREATE  TABLE IF NOT EXISTS `uspto_patents`.`USCLASSIFICATION` (
  `ClassID` INT(9) NOT NULL AUTO_INCREMENT COMMENT 'WorkingNo' ,
  `Class` VARCHAR(3) NULL ,
  `Subclass` VARCHAR(6) NULL ,
  `Indent` VARCHAR(2) NULL ,
  `SubclsSqsNum` VARCHAR(4) NULL ,
  `NextHigherSub` VARCHAR(6) NULL ,
  `Title` VARCHAR(200) NULL ,
  PRIMARY KEY (`ClassID`) )
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `uspto_patents`.`PUBCIT_P`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `uspto_patents`.`PUBCIT_P` ;

CREATE  TABLE IF NOT EXISTS `uspto_patents`.`PUBCIT_P` (
  `PublicationID` VARCHAR(20) NOT NULL ,
  `Position` INT NOT NULL ,
  `CitedID` VARCHAR(20) NULL ,
  `Kind` VARCHAR(10) NULL COMMENT 'identify whether citedDoc is a document or foreign patent' ,
  `Name` VARCHAR(100) NULL ,
  `Date` DATE NULL ,
  `Country` VARCHAR(100) NULL ,
  `Category` VARCHAR(100) NULL ,
  PRIMARY KEY (`PublicationID`, `Position`) ,
  INDEX `FK_PublicationID_PUBLICATION_PCITATION_P` (`PublicationID` ASC) ,
  CONSTRAINT `FK_PublicationID_PUBLICATION_PCITATION_P`
    FOREIGN KEY (`PublicationID` )
    REFERENCES `uspto_patents`.`PUBLICATIONS` (`PublicationID` )
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `uspto_patents`.`INTCLASS_G`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `uspto_patents`.`INTCLASS_G` ;

CREATE  TABLE IF NOT EXISTS `uspto_patents`.`INTCLASS_G` (
  `GrantID` VARCHAR(20) NOT NULL ,
  `Position` INT NOT NULL ,
  `Section` VARCHAR(10) NULL ,
  `Class` VARCHAR(20) NULL ,
  `Subclass` VARCHAR(10) NULL ,
  `MainGroup` VARCHAR(10) NULL ,
  `SubGroup` VARCHAR(10) NULL ,
  PRIMARY KEY (`GrantID`, `Position`) ,
  INDEX `fk_publicationid_PUBLICATION_INTERNATIONALCLASS_P` (`GrantID` ASC) ,
  CONSTRAINT `FK_GrantID_GRANT_INTERNATIONALCLASS_G`
    FOREIGN KEY (`GrantID` )
    REFERENCES `uspto_patents`.`GRANTS` (`GrantID` )
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `uspto_patents`.`NONPATCIT_G`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `uspto_patents`.`NONPATCIT_G` ;

CREATE  TABLE IF NOT EXISTS `uspto_patents`.`NONPATCIT_G` (
  `GrantID` VARCHAR(20) NOT NULL ,
  `Position` INT NOT NULL ,
  `Citation` TEXT NULL ,
  `Category` VARCHAR(100) NULL ,
  INDEX `fk_PublicationID_PUBLICATION_NPCITATION_P` (`GrantID` ASC) ,
  PRIMARY KEY (`GrantID`, `Position`) ,
  CONSTRAINT `FK_GrantID_GRANT_NPCITATION_G`
    FOREIGN KEY (`GrantID` )
    REFERENCES `uspto_patents`.`GRANTS` (`GrantID` )
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `uspto_patents`.`INVENTOR_G`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `uspto_patents`.`INVENTOR_G` ;

CREATE  TABLE IF NOT EXISTS `uspto_patents`.`INVENTOR_G` (
  `GrantID` VARCHAR(20) NOT NULL ,
  `Position` INT NOT NULL ,
  `FirstName` VARCHAR(100) NULL ,
  `LastName` VARCHAR(100) NULL ,
  `City` VARCHAR(100) NULL ,
  `State` VARCHAR(100) NULL ,
  `Country` VARCHAR(100) NULL ,
  `Nationality` VARCHAR(100) NULL ,
  `Residence` VARCHAR(100) NULL COMMENT 'Residence Country' ,
  PRIMARY KEY (`GrantID`, `Position`) ,
  INDEX `fk_PublicationID_Inventor_p` (`GrantID` ASC) ,
  CONSTRAINT `FK_GrantID_GRANT_INVENTOR_G`
    FOREIGN KEY (`GrantID` )
    REFERENCES `uspto_patents`.`GRANTS` (`GrantID` )
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `uspto_patents`.`USCLASS_G`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `uspto_patents`.`USCLASS_G` ;

CREATE  TABLE IF NOT EXISTS `uspto_patents`.`USCLASS_G` (
  `GrantID` VARCHAR(20) NOT NULL COMMENT 'WorkingNo' ,
  `Position` INT NOT NULL ,
  `Class` VARCHAR(3) NULL ,
  `Subclass` VARCHAR(6) NULL ,
  PRIMARY KEY (`GrantID`, `Position`) ,
  INDEX `fk_publicationid_PUBLICATION_USCLASS_P` (`GrantID` ASC) ,
  CONSTRAINT `FK_GrantID_GRANT_USLCASS_G`
    FOREIGN KEY (`GrantID` )
    REFERENCES `uspto_patents`.`GRANTS` (`GrantID` )
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `uspto_patents`.`PUBCIT_G`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `uspto_patents`.`PUBCIT_G` ;

CREATE  TABLE IF NOT EXISTS `uspto_patents`.`PUBCIT_G` (
  `GrantID` VARCHAR(20) NOT NULL ,
  `Position` INT NOT NULL ,
  `CitedID` VARCHAR(20) NULL ,
  `Kind` VARCHAR(10) NULL COMMENT 'identify whether citedDoc is a document or foreign patent' ,
  `Name` VARCHAR(100) NULL ,
  `Date` DATE NULL ,
  `Country` VARCHAR(100) NULL ,
  `Category` VARCHAR(100) NULL ,
  PRIMARY KEY (`GrantID`, `Position`) ,
  INDEX `FK_PublicationID_PUBLICATION_PCITATION_P` (`GrantID` ASC) ,
  CONSTRAINT `FK_GrantID_GRANT_PCITATION_G`
    FOREIGN KEY (`GrantID` )
    REFERENCES `uspto_patents`.`GRANTS` (`GrantID` )
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `uspto_patents`.`AGENT_G`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `uspto_patents`.`AGENT_G` ;

CREATE  TABLE IF NOT EXISTS `uspto_patents`.`AGENT_G` (
  `GrantID` VARCHAR(20) NOT NULL COMMENT 'attorney' ,
  `Position` INT NOT NULL ,
  `OrgName` VARCHAR(200) NULL ,
  `LastName` VARCHAR(100) NULL ,
  `FirstName` VARCHAR(100) NULL ,
  `Country` VARCHAR(100) NULL ,
  PRIMARY KEY (`GrantID`, `Position`) ,
  INDEX `FK_PublicationID_PUBLICATION_AGENT_P` (`GrantID` ASC) ,
  CONSTRAINT `FK_GrantID_GRANT_AGENT_G`
    FOREIGN KEY (`GrantID` )
    REFERENCES `uspto_patents`.`GRANTS` (`GrantID` )
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `uspto_patents`.`ASSIGNEE_G`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `uspto_patents`.`ASSIGNEE_G` ;

CREATE  TABLE IF NOT EXISTS `uspto_patents`.`ASSIGNEE_G` (
  `GrantID` VARCHAR(20) NOT NULL ,
  `Position` INT NOT NULL ,
  `OrgName` VARCHAR(200) NULL COMMENT '\\\"United States of America as represented by the Administrator of the National Aeronautics and Space Administration\\\" >100' ,
  `Role` VARCHAR(45) NULL ,
  `City` VARCHAR(100) NULL ,
  `State` VARCHAR(100) NULL ,
  `Country` VARCHAR(100) NULL ,
  PRIMARY KEY (`GrantID`, `Position`) ,
  INDEX `FK_PublicationID_PUBLICATION_ASSIGNEE_P` (`GrantID` ASC) ,
  CONSTRAINT `FK_GrantID_GRANT_ASSIGNEE_G`
    FOREIGN KEY (`GrantID` )
    REFERENCES `uspto_patents`.`GRANTS` (`GrantID` )
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `uspto_patents`.`EXAMINER_G`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `uspto_patents`.`EXAMINER_G` ;

CREATE  TABLE IF NOT EXISTS `uspto_patents`.`EXAMINER_G` (
  `GrantID` VARCHAR(20) NOT NULL ,
  `Position` INT NOT NULL ,
  `LastName` VARCHAR(100) NULL ,
  `FirstName` VARCHAR(100) NULL ,
  `Department` VARCHAR(100) NULL ,
  PRIMARY KEY (`GrantID`, `Position`) ,
  INDEX `FK_GrantID_GRANT_EXAMINER_G` (`GrantID` ASC) ,
  CONSTRAINT `FK_GrantID_GRANT_EXAMINER_G`
    FOREIGN KEY (`GrantID` )
    REFERENCES `uspto_patents`.`GRANTS` (`GrantID` )
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `uspto_patents`.`GRACIT_P`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `uspto_patents`.`GRACIT_P` ;

CREATE  TABLE IF NOT EXISTS `uspto_patents`.`GRACIT_P` (
  `PublicationID` VARCHAR(20) NOT NULL ,
  `Position` INT NOT NULL ,
  `CitedID` VARCHAR(20) NULL ,
  `Kind` VARCHAR(10) NULL COMMENT 'identify whether citedDoc is a document or foreign patent' ,
  `Name` VARCHAR(100) NULL ,
  `Date` DATE NULL ,
  `Country` VARCHAR(100) NULL ,
  `Category` VARCHAR(100) NULL ,
  PRIMARY KEY (`PublicationID`, `Position`) ,
  INDEX `FK_PublicationID_PUBLICATION_PCITATION_P` (`PublicationID` ASC) ,
  CONSTRAINT `FK_PublicationID_PUBLICATION_PCITATION_P0`
    FOREIGN KEY (`PublicationID` )
    REFERENCES `uspto_patents`.`PUBLICATIONS` (`PublicationID` )
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `uspto_patents`.`FORPATCIT_P`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `uspto_patents`.`FORPATCIT_P` ;

CREATE  TABLE IF NOT EXISTS `uspto_patents`.`FORPATCIT_P` (
  `PublicationID` VARCHAR(20) NOT NULL ,
  `Position` INT NOT NULL ,
  `CitedID` VARCHAR(20) NULL ,
  `Kind` VARCHAR(10) NULL COMMENT 'identify whether citedDoc is a document or foreign patent' ,
  `Name` VARCHAR(100) NULL ,
  `Date` DATE NULL ,
  `Country` VARCHAR(100) NULL ,
  `Category` VARCHAR(100) NULL ,
  PRIMARY KEY (`PublicationID`, `Position`) ,
  INDEX `FK_PublicationID_PUBLICATION_PCITATION_P` (`PublicationID` ASC) ,
  CONSTRAINT `FK_PublicationID_PUBLICATION_PCITATION_P1`
    FOREIGN KEY (`PublicationID` )
    REFERENCES `uspto_patents`.`PUBLICATIONS` (`PublicationID` )
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `uspto_patents`.`GRACIT_G`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `uspto_patents`.`GRACIT_G` ;

CREATE  TABLE IF NOT EXISTS `uspto_patents`.`GRACIT_G` (
  `GrantID` VARCHAR(20) NOT NULL ,
  `Position` INT NOT NULL ,
  `CitedID` VARCHAR(20) NULL ,
  `Kind` VARCHAR(10) NULL COMMENT 'identify whether citedDoc is a document or foreign patent' ,
  `Name` VARCHAR(100) NULL ,
  `Date` DATE NULL ,
  `Country` VARCHAR(100) NULL ,
  `Category` VARCHAR(100) NULL ,
  PRIMARY KEY (`GrantID`, `Position`) ,
  INDEX `FK_PublicationID_PUBLICATION_PCITATION_P` (`GrantID` ASC) ,
  CONSTRAINT `FK_GrantID_GRANT_PCITATION_G0`
    FOREIGN KEY (`GrantID` )
    REFERENCES `uspto_patents`.`GRANTS` (`GrantID` )
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `uspto_patents`.`FORPATCIT_G`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `uspto_patents`.`FORPATCIT_G` ;

CREATE  TABLE IF NOT EXISTS `uspto_patents`.`FORPATCIT_G` (
  `GrantID` VARCHAR(20) NOT NULL ,
  `Position` INT NOT NULL ,
  `CitedID` VARCHAR(20) NULL ,
  `Kind` VARCHAR(10) NULL COMMENT 'identify whether citedDoc is a document or foreign patent' ,
  `Name` VARCHAR(100) NULL ,
  `Date` DATE NULL ,
  `Country` VARCHAR(100) NULL ,
  `Category` VARCHAR(100) NULL ,
  PRIMARY KEY (`GrantID`, `Position`) ,
  INDEX `FK_PublicationID_PUBLICATION_PCITATION_P` (`GrantID` ASC) ,
  CONSTRAINT `FK_GrantID_GRANT_PCITATION_G00`
    FOREIGN KEY (`GrantID` )
    REFERENCES `uspto_patents`.`GRANTS` (`GrantID` )
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;



SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
