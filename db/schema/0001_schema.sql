-- MySQL dump 10.13  Distrib 5.6.31, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: mlb_stats
-- ------------------------------------------------------
-- Server version	5.6.31-0ubuntu0.15.10.1

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
-- Table structure for table `atbats`
--

DROP TABLE IF EXISTS `atbats`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `atbats` (
  `abid` bigint(20) NOT NULL,
  `play_guid` varchar(64) DEFAULT NULL,
  `game_date` date NOT NULL,
  `gid` varchar(30) NOT NULL,
  `bid` int(11) NOT NULL,
  `pid` int(11) NOT NULL,
  `abno` smallint(6) NOT NULL,
  `des` varchar(550) DEFAULT NULL,
  `balls` smallint(6) NOT NULL,
  `strikes` smallint(6) NOT NULL,
  `outs` smallint(6) NOT NULL,
  `event` varchar(255) NOT NULL,
  `home_runs` smallint(6) NOT NULL,
  `away_runs` smallint(6) NOT NULL,
  `risp` smallint(6) NOT NULL,
  `runner_first` smallint(6) NOT NULL,
  `runner_second` smallint(6) NOT NULL,
  `runner_third` smallint(6) NOT NULL,
  `rbi` smallint(6) NOT NULL,
  PRIMARY KEY (`abid`),
  KEY `gid` (`gid`),
  KEY `bid` (`bid`),
  KEY `pid` (`pid`),
  CONSTRAINT `atbats_ibfk_1` FOREIGN KEY (`gid`) REFERENCES `games` (`gid`),
  CONSTRAINT `atbats_ibfk_2` FOREIGN KEY (`bid`) REFERENCES `players` (`pid`),
  CONSTRAINT `atbats_ibfk_3` FOREIGN KEY (`pid`) REFERENCES `players` (`pid`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `games`
--

DROP TABLE IF EXISTS `games`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `games` (
  `gid` varchar(30) NOT NULL,
  `game_date` date NOT NULL,
  `vid` smallint(6) NOT NULL,
  `home_team` varchar(5) NOT NULL,
  `away_team` varchar(5) NOT NULL,
  `h_losses` smallint(6) NOT NULL,
  `h_wins` smallint(6) NOT NULL,
  `h_hits` smallint(6) NOT NULL,
  `h_runs` smallint(6) NOT NULL,
  `h_errors` smallint(6) NOT NULL,
  `a_losses` smallint(6) NOT NULL,
  `a_wins` smallint(6) NOT NULL,
  `a_hits` smallint(6) NOT NULL,
  `a_runs` smallint(6) NOT NULL,
  `a_errors` smallint(6) NOT NULL,
  PRIMARY KEY (`gid`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `gamestats_batter`
--

DROP TABLE IF EXISTS `gamestats_batter`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `gamestats_batter` (
  `gid` varchar(30) NOT NULL,
  `pid` int(11) NOT NULL,
  `game_date` date NOT NULL,
  `pa` tinyint(4) DEFAULT NULL,
  `ab` tinyint(4) NOT NULL,
  `hits` tinyint(4) NOT NULL,
  `runs` tinyint(4) NOT NULL,
  `hr` tinyint(4) NOT NULL,
  `bb` tinyint(4) NOT NULL,
  `so` tinyint(4) NOT NULL,
  `rbi` tinyint(4) NOT NULL,
  `1b` tinyint(4) DEFAULT NULL,
  `2b` tinyint(4) DEFAULT NULL,
  `3b` tinyint(4) DEFAULT NULL,
  `sb` tinyint(4) DEFAULT NULL,
  `cs` tinyint(4) NOT NULL,
  `lob` tinyint(4) NOT NULL,
  `bo` smallint(6) NOT NULL,
  `sac` tinyint(4) NOT NULL,
  `sf` tinyint(4) NOT NULL,
  `hbp` tinyint(4) NOT NULL,
  KEY `gid` (`gid`),
  KEY `pid` (`pid`),
  CONSTRAINT `gamestats_batter_ibfk_1` FOREIGN KEY (`gid`) REFERENCES `games` (`gid`),
  CONSTRAINT `gamestats_batter_ibfk_2` FOREIGN KEY (`pid`) REFERENCES `players` (`pid`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `gamestats_pitcher`
--

DROP TABLE IF EXISTS `gamestats_pitcher`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `gamestats_pitcher` (
  `gid` varchar(30) NOT NULL,
  `pid` int(11) NOT NULL,
  `game_date` date NOT NULL,
  `hits` tinyint(4) NOT NULL,
  `runs` tinyint(4) NOT NULL,
  `er` tinyint(4) NOT NULL,
  `hr` tinyint(4) NOT NULL,
  `bb` tinyint(4) NOT NULL,
  `so` tinyint(4) NOT NULL,
  `bf` tinyint(4) NOT NULL,
  `outs` tinyint(4) NOT NULL,
  `strikes` smallint(6) NOT NULL,
  `pitches` smallint(6) NOT NULL,
  KEY `gid` (`gid`),
  KEY `pid` (`pid`),
  CONSTRAINT `gamestats_pitcher_ibfk_1` FOREIGN KEY (`gid`) REFERENCES `games` (`gid`),
  CONSTRAINT `gamestats_pitcher_ibfk_2` FOREIGN KEY (`pid`) REFERENCES `players` (`pid`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pitches`
--

DROP TABLE IF EXISTS `pitches`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pitches` (
  `game_date` date NOT NULL,
  `play_guid` varchar(64) DEFAULT NULL,
  `sv_id` varchar(30) DEFAULT NULL,
  `pid` int(11) NOT NULL,
  `bid` int(11) NOT NULL,
  `gid` varchar(30) NOT NULL,
  `abid` bigint(20) NOT NULL,
  `des` varchar(30) DEFAULT NULL,
  `result` char(1) NOT NULL,
  `balls` int(11) NOT NULL,
  `strikes` int(11) NOT NULL,
  `outs` int(11) NOT NULL,
  `start_speed` float DEFAULT NULL,
  `end_speed` float DEFAULT NULL,
  `sz_top` float DEFAULT NULL,
  `sz_bot` float DEFAULT NULL,
  `pfx_x` float DEFAULT NULL,
  `pfx_z` float DEFAULT NULL,
  `px` float DEFAULT NULL,
  `pz` float DEFAULT NULL,
  `x0` float DEFAULT NULL,
  `y0` float DEFAULT NULL,
  `z0` float DEFAULT NULL,
  `vx0` float DEFAULT NULL,
  `vy0` float DEFAULT NULL,
  `vz0` float DEFAULT NULL,
  `ax` float DEFAULT NULL,
  `ay` float DEFAULT NULL,
  `az` float DEFAULT NULL,
  `break_y` float DEFAULT NULL,
  `break_angle` float DEFAULT NULL,
  `break_length` float DEFAULT NULL,
  `pitch_type` char(2) DEFAULT NULL,
  `type_confidence` float DEFAULT NULL,
  `zone` int(11) DEFAULT NULL,
  `nasty` int(11) DEFAULT NULL,
  `spin_dir` float DEFAULT NULL,
  `spin_rate` float DEFAULT NULL,
  KEY `gid` (`gid`),
  KEY `pid` (`pid`),
  KEY `bid` (`bid`),
  KEY `abid` (`abid`),
  CONSTRAINT `pitches_ibfk_1` FOREIGN KEY (`gid`) REFERENCES `games` (`gid`),
  CONSTRAINT `pitches_ibfk_2` FOREIGN KEY (`pid`) REFERENCES `players` (`pid`),
  CONSTRAINT `pitches_ibfk_3` FOREIGN KEY (`bid`) REFERENCES `players` (`pid`),
  CONSTRAINT `pitches_ibfk_4` FOREIGN KEY (`abid`) REFERENCES `atbats` (`abid`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `players`
--

DROP TABLE IF EXISTS `players`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `players` (
  `name` varchar(30) NOT NULL,
  `pid` int(11) NOT NULL,
  `pos` varchar(5) NOT NULL,
  `team` varchar(10) NOT NULL,
  `bats` varchar(2) NOT NULL,
  `throws` varchar(2) NOT NULL,
  PRIMARY KEY (`pid`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2016-09-28 13:57:07
