-- MySQL dump 10.13  Distrib 8.0.41, for Win64 (x86_64)
--
-- Host: localhost    Database: MonitoramentoSustentabilidade
-- ------------------------------------------------------
-- Server version	8.0.41-0ubuntu0.24.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `consumos_brutos`
--

DROP TABLE IF EXISTS `consumos_brutos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `consumos_brutos` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `Agua` int DEFAULT NULL,
  `Energia` int DEFAULT NULL,
  `fk_relatorio` int DEFAULT NULL,
  `data_insercao` date DEFAULT NULL,
  `residuos_reciclaveis` decimal(10,2) DEFAULT NULL,
  `residuos_nao_reciclaveis` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `b_unique` (`data_insercao`,`fk_relatorio`),
  KEY `bruto_relatorio_fk` (`fk_relatorio`),
  CONSTRAINT `bruto_relatorio_fk` FOREIGN KEY (`fk_relatorio`) REFERENCES `relatorios` (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `consumos_normalizados`
--

DROP TABLE IF EXISTS `consumos_normalizados`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `consumos_normalizados` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `Agua` float DEFAULT NULL,
  `Energia` float DEFAULT NULL,
  `Residuos` float DEFAULT NULL,
  `Transporte` float DEFAULT NULL,
  `fk_relatorio` int DEFAULT NULL,
  `data_insercao` date DEFAULT NULL,
  `ISP` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  UNIQUE KEY `n_unique` (`data_insercao`,`fk_relatorio`),
  KEY `norm_relatorio_fk` (`fk_relatorio`),
  CONSTRAINT `norm_relatorio_fk` FOREIGN KEY (`fk_relatorio`) REFERENCES `relatorios` (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=20 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `graficos`
--

DROP TABLE IF EXISTS `graficos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `graficos` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `Tipo_grafico` varchar(100) NOT NULL,
  `Tipo_armazenado` varchar(100) NOT NULL,
  `Construcao` mediumtext,
  `fk_relatorios_id` int NOT NULL,
  PRIMARY KEY (`ID`),
  KEY `fk_relatorios_id_idx` (`fk_relatorios_id`),
  CONSTRAINT `fk_relatorios_id1` FOREIGN KEY (`fk_relatorios_id`) REFERENCES `relatorios` (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=181 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `notificacoes`
--

DROP TABLE IF EXISTS `notificacoes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notificacoes` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `Titulo` varchar(100) NOT NULL,
  `Conteudo` varchar(500) NOT NULL,
  `fk_consumos_normalizados_id` int DEFAULT NULL,
  `fk_consumos_brutos_id` int DEFAULT NULL,
  PRIMARY KEY (`ID`),
  KEY `fk_consumos_normalizados_id` (`fk_consumos_normalizados_id`),
  KEY `fk_consumos_brutos_id` (`fk_consumos_brutos_id`),
  CONSTRAINT `notificacoes_ibfk_1` FOREIGN KEY (`fk_consumos_normalizados_id`) REFERENCES `consumos_normalizados` (`ID`),
  CONSTRAINT `notificacoes_ibfk_2` FOREIGN KEY (`fk_consumos_brutos_id`) REFERENCES `consumos_brutos` (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `relatorios`
--

DROP TABLE IF EXISTS `relatorios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `relatorios` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `fk_id_usuario` int NOT NULL,
  `Data_inicio` date NOT NULL,
  `Data_fim` date NOT NULL,
  `ISS` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  KEY `fk_id_usuario_idx` (`fk_id_usuario`),
  CONSTRAINT `fk_id_usuario` FOREIGN KEY (`fk_id_usuario`) REFERENCES `usuarios` (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `reset_password`
--

DROP TABLE IF EXISTS `reset_password`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `reset_password` (
  `email_usuario` varchar(100) NOT NULL,
  `token_atual` varchar(100) NOT NULL,
  `tempo_limite` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `transporte`
--

DROP TABLE IF EXISTS `transporte`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `transporte` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `Tipo_veiculo` varchar(100) NOT NULL,
  `Distancia` decimal(10,2) NOT NULL,
  `fk_consumos_brutos_id` int NOT NULL,
  PRIMARY KEY (`ID`),
  KEY `fk_consumos_brutos_id_idx` (`fk_consumos_brutos_id`),
  CONSTRAINT `fk_consumos_brutos_id` FOREIGN KEY (`fk_consumos_brutos_id`) REFERENCES `consumos_brutos` (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=37 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios` (
  `ID` int NOT NULL AUTO_INCREMENT,
  `CPF` varchar(100) NOT NULL,
  `Email` varchar(100) NOT NULL,
  `Senha` varchar(100) NOT NULL,
  `ISI` float DEFAULT NULL,
  `Pontos` int DEFAULT NULL,
  `Sustentabilidade` varchar(25) DEFAULT NULL,
  `nome` varchar(100) DEFAULT NULL,
  `data_nascimento` date DEFAULT NULL,
  `data_cadastro` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-05-25 15:49:35
