-- MySQL dump 10.13  Distrib 5.7.16, for osx10.11 (x86_64)
--
-- Host: localhost    Database: db_weixin
-- ------------------------------------------------------
-- Server version	5.7.16

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
-- Current Database: `db_weixin`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `db_weixin` /*!40100 DEFAULT CHARACTER SET utf8 */;

USE `db_weixin`;

--
-- Table structure for table `tb_weixin_account`
--

DROP TABLE IF EXISTS `tb_weixin_account`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tb_weixin_account` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自增id',
  `weixin_id` varchar(45) NOT NULL COMMENT '微信号',
  `weixin_name` varchar(64) NOT NULL COMMENT '微信名称',
  `insert_time` timestamp NULL DEFAULT NULL,
  `update_time` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `name_UNIQUE` (`weixin_name`),
  UNIQUE KEY `account_UNIQUE` (`weixin_id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tb_weixin_account`
--

LOCK TABLES `tb_weixin_account` WRITE;
/*!40000 ALTER TABLE `tb_weixin_account` DISABLE KEYS */;
/*!40000 ALTER TABLE `tb_weixin_account` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tb_weixin_article`
--

DROP TABLE IF EXISTS `tb_weixin_article`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tb_weixin_article` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `uid` varchar(64) NOT NULL,
  `account_id` int(11) NOT NULL,
  `title` tinytext NOT NULL,
  `abstract` text,
  `content` longtext,
  `author` varchar(64) DEFAULT NULL,
  `publish_time` date DEFAULT NULL,
  `query` varchar(64) DEFAULT NULL COMMENT '搜索条件',
  `source` varchar(32) DEFAULT NULL COMMENT '来源',
  `insert_time` timestamp NULL DEFAULT NULL,
  `update_time` timestamp NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `uid_UNIQUE` (`uid`),
  KEY `account_id_fk_idx` (`account_id`),
  CONSTRAINT `account_id_fk` FOREIGN KEY (`account_id`) REFERENCES `tb_weixin_account` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tb_weixin_article`
--

LOCK TABLES `tb_weixin_article` WRITE;
/*!40000 ALTER TABLE `tb_weixin_article` DISABLE KEYS */;
/*!40000 ALTER TABLE `tb_weixin_article` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2016-12-06 16:37:24
