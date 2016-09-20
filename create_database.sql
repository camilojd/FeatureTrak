-- as mysql's `root`
CREATE DATABASE IF NOT EXISTS featuretrak CHARACTER SET utf8 COLLATE utf8_general_ci;
GRANT ALL PRIVILEGES ON featuretrak.* To 'enders'@'localhost' IDENTIFIED BY 'game';

CREATE DATABASE IF NOT EXISTS featuretrak_test CHARACTER SET utf8 COLLATE utf8_general_ci;
GRANT ALL PRIVILEGES ON featuretrak_test.* To 'travis'@'localhost' IDENTIFIED BY '';
