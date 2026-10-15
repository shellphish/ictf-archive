-- MySQL dump 10.10
--
-- Host: localhost    Database: ipal_development
-- ------------------------------------------------------
-- Server version	5.0.22

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `contacts_users`
--

DROP TABLE IF EXISTS `contacts_users`;
CREATE TABLE `contacts_users` (
  `user_id` int(11) NOT NULL,
  `contact_id` int(11) NOT NULL,
  KEY `contacts_users_user_id_index` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `contacts_users`
--


/*!40000 ALTER TABLE `contacts_users` DISABLE KEYS */;
LOCK TABLES `contacts_users` WRITE;
UNLOCK TABLES;
/*!40000 ALTER TABLE `contacts_users` ENABLE KEYS */;

--
-- Table structure for table `currencies`
--

DROP TABLE IF EXISTS `currencies`;
CREATE TABLE `currencies` (
  `id` int(11) NOT NULL auto_increment,
  `symbol` varchar(255) default NULL,
  `name` varchar(255) default NULL,
  `description` varchar(255) default NULL,
  `rate` float NOT NULL,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `currencies`
--


/*!40000 ALTER TABLE `currencies` DISABLE KEYS */;
LOCK TABLES `currencies` WRITE;
INSERT INTO `currencies` VALUES (1,'EUR','Euro','The euro (currency sign: â‚¬, banking code EUR) is the official currency of the European Union member states of Austria, Belgium, Finland, France, Germany, Greece, Ireland, Italy, Luxembourg, the Netherlands, Portugal, and Spain - also known as the Eurozo',1.3),(2,'JPY','Japanese Yen','The yen or en (Japanese: å††, en, in older Japanese yen) is the currency of Japan. It is also widely used as a reserve currency after the United States dollar and euro. The ISO 4217 codes for the yen are JPY and 392. The Latinised symbol is Â¥, while in J',115),(3,'GBP','Pound Sterling','The pound (symbol: Â£; ISO code: GBP), divided into 100 pence, is the official currency of the United Kingdom and the Crown Dependencies. The slang term \"quid\" is very common in the UK.',1.97),(4,'TWD','New Taiwan Dollar','The New Taiwan dollar (currency code TWD and common abbreviation NT$), or simply Taiwan dollar, is the official currency of the Republic of China within the areas of Taiwan, Penghu, Kinmen, and Matsu since 1949. Originally issued by the Bank of Taiwan, it',0.03),(5,'AUD','Australian Dollar','The Australian dollar (currency code AUD) has been, since 1966, the currency of the Commonwealth of Australia, including Christmas Island, Cocos (Keeling) Islands, and Norfolk Island, as well as the independent Pacific Island states of Kiribati, Nauru and',0.79),(6,'CAD','Canadian Dollar','The dollar (currency code CAD) has been the currency of Canada since 1858. It is normally abbreviated with the dollar sign $, or C$ to distinguish it from other dollar-denominated currencies.',0.87),(7,'HKD','Hong Kong Dollar','The Hong Kong dollar (currency code HKD) is the currency of the Hong Kong Special Administrative Region of the People\'s Republic of China, and has been the currency of Hong Kong since 1937. It is normally abbreviated with the dollar sign $, or alternative',0.13),(8,'CHF','Swiss Franc','The franc (ISO 4217: CHF or 756) is the currency and legal tender of Switzerland and Liechtenstein. Franc banknotes are issued by the central bank of Switzerland, the Swiss National Bank, while coins are issued by the federal mint, Swissmint.',0.83),(9,'BRL','Brazilian Real','The real (symbol: R$, ISO 4217 code: BRL, plural: reais) is the currency of Brazil. It is also the name of the earliest Brazilian currency (see from the Colonial period to 1942.)',0.47),(10,'RMB','Renminbi','The renminbi or ren min bi or the yuan is the official currency in the mainland of the People\'s Republic of China (PRC). It is issued by the People\'s Bank of China, the monetary authority of the PRC. The official ISO 4217 abbreviation is CNY, although als',0.12);
UNLOCK TABLES;
/*!40000 ALTER TABLE `currencies` ENABLE KEYS */;

--
-- Table structure for table `deposits`
--

DROP TABLE IF EXISTS `deposits`;
CREATE TABLE `deposits` (
  `id` int(11) NOT NULL auto_increment,
  `user_id` int(11) NOT NULL,
  `amount` int(11) NOT NULL,
  `orig_rate` float NOT NULL,
  `curr_rate` float NOT NULL,
  `currency_id` int(11) NOT NULL default '1',
  PRIMARY KEY  (`id`),
  KEY `deposits_user_id_index` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `deposits`
--


/*!40000 ALTER TABLE `deposits` DISABLE KEYS */;
LOCK TABLES `deposits` WRITE;
UNLOCK TABLES;
/*!40000 ALTER TABLE `deposits` ENABLE KEYS */;

--
-- Table structure for table `schema_info`
--

DROP TABLE IF EXISTS `schema_info`;
CREATE TABLE `schema_info` (
  `version` int(11) default NULL
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `schema_info`
--


/*!40000 ALTER TABLE `schema_info` DISABLE KEYS */;
LOCK TABLES `schema_info` WRITE;
INSERT INTO `schema_info` VALUES (8);
UNLOCK TABLES;
/*!40000 ALTER TABLE `schema_info` ENABLE KEYS */;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` int(11) NOT NULL auto_increment,
  `login` varchar(255) default NULL,
  `email` varchar(255) default NULL,
  `crypted_password` varchar(40) default NULL,
  `salt` varchar(40) default NULL,
  `admin` tinyint(1) default NULL,
  `description` varchar(255) default NULL,
  `created_at` datetime default NULL,
  `updated_at` datetime default NULL,
  `remember_token` varchar(255) default NULL,
  `remember_token_expires_at` datetime default NULL,
  `image_link` varchar(255) default 'thumb_1.jpg',
  PRIMARY KEY  (`id`),
  KEY `users_login_index` (`login`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `users`
--


/*!40000 ALTER TABLE `users` DISABLE KEYS */;
LOCK TABLES `users` WRITE;
UNLOCK TABLES;
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

