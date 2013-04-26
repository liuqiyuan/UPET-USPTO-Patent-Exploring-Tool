set foreign_key_checks=0;

set @path='/content/qliu14/uspto_patents/CSV_G/'

# LODA "REPLACE"
# *****
# This is very important to replace sth. existed in the records

# APPLICATION
LOAD DATA LOCAL INFILE '/content/qliu14/uspto_patents/CSV_G/application.csv'
IGNORE INTO TABLE uspto_patents.APPLICATION
FIELDS TERMINATED BY '\t'
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n';

# AGENT
LOAD DATA LOCAL INFILE '/content/qliu14/uspto_patents/CSV_G/agent.csv'
IGNORE INTO TABLE uspto_patents.AGENT_G
FIELDS TERMINATED BY '\t'
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n';

# ASSIGNEE
LOAD DATA LOCAL INFILE '/content/qliu14/uspto_patents/CSV_G/assignee.csv'
IGNORE INTO TABLE uspto_patents.ASSIGNEE_G
FIELDS TERMINATED BY '\t'
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n';

# EXAMINER
LOAD DATA LOCAL INFILE '/content/qliu14/uspto_patents/CSV_G/examiner.csv'
IGNORE INTO TABLE uspto_patents.EXAMINER_G
FIELDS TERMINATED BY '\t'
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n';

# FORPATCIT
LOAD DATA LOCAL INFILE '/content/qliu14/uspto_patents/CSV_G/forpatcit.csv'
IGNORE INTO TABLE uspto_patents.FORPATCIT_G
FIELDS TERMINATED BY '\t'
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n';

# GRACIT
LOAD DATA LOCAL INFILE '/content/qliu14/uspto_patents/CSV_G/gracit.csv'
IGNORE INTO TABLE uspto_patents.GRACIT_G
FIELDS TERMINATED BY '\t'
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n';

# GRANTS
LOAD DATA LOCAL INFILE '/content/qliu14/uspto_patents/CSV_G/grants.csv'
IGNORE INTO TABLE uspto_patents.GRANTS
FIELDS TERMINATED BY '\t'
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n';

# INTCLASS
LOAD DATA LOCAL INFILE '/content/qliu14/uspto_patents/CSV_G/intclass.csv'
IGNORE INTO TABLE uspto_patents.INTCLASS_G
FIELDS TERMINATED BY '\t'
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n';

# INVENTOR
LOAD DATA LOCAL INFILE '/content/qliu14/uspto_patents/CSV_G/inventor.csv'
IGNORE INTO TABLE uspto_patents.INVENTOR_G
FIELDS TERMINATED BY '\t'
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n';

# NONPATCIT
LOAD DATA LOCAL INFILE '/content/qliu14/uspto_patents/CSV_G/nonpatcit.csv'
IGNORE INTO TABLE uspto_patents.NONPATCIT_G
FIELDS TERMINATED BY '\t'
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n';

#Query OK, 15672586 rows affected, 2 warnings (16 min 52.19 sec)
#Records: 15672595  Deleted: 0  Skipped: 9  Warnings: 2

# PUBCIT
LOAD DATA LOCAL INFILE '/content/qliu14/uspto_patents/CSV_G/pubcit.csv'
IGNORE INTO TABLE uspto_patents.PUBCIT_G
FIELDS TERMINATED BY '\t'
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n';
#Query OK, 6872747 rows affected, 20 warnings (4 min 45.21 sec)
#Records: 6872748  Deleted: 0  Skipped: 1  Warnings: 18

# USCLASS
LOAD DATA LOCAL INFILE '/content/qliu14/uspto_patents/CSV_G/usclass.csv'
IGNORE INTO TABLE uspto_patents.USCLASS_G
FIELDS TERMINATED BY '\t'
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n';

#Query OK, 17933014 rows affected, 778 warnings (8 min 41.91 sec)
#Records: 17933030  Deleted: 0  Skipped: 16  Warnings: 778

set foreign_key_checks=1;