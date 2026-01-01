-- MySQL dump 10.13  Distrib 8.0.44, for Linux (x86_64)
--
-- Host: localhost    Database: image_db
-- ------------------------------------------------------
-- Server version	8.0.44

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `image_tags`
--

DROP TABLE IF EXISTS `image_tags`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `image_tags` (
  `image_id` int NOT NULL,
  `tag_id` int NOT NULL,
  PRIMARY KEY (`image_id`,`tag_id`),
  KEY `tag_id` (`tag_id`),
  CONSTRAINT `image_tags_ibfk_1` FOREIGN KEY (`image_id`) REFERENCES `images` (`id`),
  CONSTRAINT `image_tags_ibfk_2` FOREIGN KEY (`tag_id`) REFERENCES `tags` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `image_tags`
--

LOCK TABLES `image_tags` WRITE;
/*!40000 ALTER TABLE `image_tags` DISABLE KEYS */;
INSERT INTO `image_tags` VALUES (9,3),(10,3),(11,4),(12,4),(11,5),(20,5),(46,5),(11,6),(11,7),(11,8),(20,8),(11,9),(12,10),(12,11),(12,12),(12,13),(12,14),(13,14),(20,14),(21,14),(29,14),(38,14),(41,14),(44,14),(45,14),(46,14),(15,15),(19,15),(22,15),(23,15),(24,15),(19,16),(22,16),(19,17),(19,18),(18,19),(19,19),(22,19),(13,20),(13,21),(13,22),(13,23),(16,24),(16,25),(21,25),(42,25),(44,25),(45,25),(16,26),(16,27),(16,28),(18,29),(18,30),(22,30),(18,31),(18,32),(21,34),(38,34),(41,34),(45,34),(21,35),(28,35),(30,35),(47,35),(21,36),(29,36),(38,36),(41,36),(42,36),(45,36),(20,38),(20,39),(22,42),(7,43),(7,44),(23,45),(24,45),(23,46),(23,47),(9,48),(21,49),(21,50),(7,51),(24,52),(24,53),(24,54),(25,55),(27,55),(25,56),(25,57),(25,58),(25,59),(27,60),(27,61),(27,62),(27,63),(29,69),(42,69),(44,69),(29,70),(45,70),(29,71),(30,72),(30,73),(28,74),(30,74),(47,74),(28,75),(30,75),(47,75),(28,76),(46,76),(47,76),(28,77),(47,77),(31,78),(32,78),(33,78),(34,78),(35,78),(36,78),(31,79),(32,79),(33,79),(34,79),(35,79),(36,79),(31,80),(31,81),(32,81),(33,81),(34,81),(35,81),(36,81),(31,82),(32,83),(33,83),(34,83),(35,83),(32,84),(33,85),(34,86),(35,87),(36,88),(36,89),(37,90),(37,91),(37,92),(37,93),(37,94),(38,95),(41,95),(38,96),(39,97),(40,97),(39,98),(40,98),(39,99),(39,100),(40,100),(39,101),(40,101),(40,102),(41,103),(42,104),(44,104),(42,105),(43,106),(43,107),(43,108),(43,109),(43,110),(44,111),(46,112),(46,113);
/*!40000 ALTER TABLE `image_tags` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `images`
--

DROP TABLE IF EXISTS `images`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `images` (
  `id` int NOT NULL AUTO_INCREMENT,
  `filename` varchar(255) NOT NULL,
  `file_path` varchar(255) NOT NULL,
  `thumbnail_path` varchar(255) DEFAULT NULL,
  `file_size` int NOT NULL,
  `width` int DEFAULT NULL,
  `height` int DEFAULT NULL,
  `capture_date` timestamp NULL DEFAULT (now()),
  `location` varchar(255) DEFAULT NULL,
  `category` varchar(50) DEFAULT NULL,
  `view_count` int DEFAULT NULL,
  `owner_id` bigint DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT (now()),
  PRIMARY KEY (`id`),
  KEY `owner_id` (`owner_id`),
  KEY `ix_images_id` (`id`),
  CONSTRAINT `images_ibfk_1` FOREIGN KEY (`owner_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=48 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `images`
--

LOCK TABLES `images` WRITE;
/*!40000 ALTER TABLE `images` DISABLE KEYS */;
INSERT INTO `images` VALUES (1,'logo.jpg','static/uploads/781bac11-f02d-46ed-82d1-be0538d00440.jpg','static/thumbnails/781bac11-f02d-46ed-82d1-be0538d00440.jpg',28334,400,400,'2025-12-25 21:50:54','Shanghai','其他',2,1,'2025-12-25 13:50:53'),(7,'背景.png','static/uploads/8f88f3be-8e7e-4694-b954-028edb1ea77b.png','static/thumbnails/8f88f3be-8e7e-4694-b954-028edb1ea77b.png',1541,431,374,'2025-12-25 23:27:38','杭州','其他',17,2,'2025-12-25 15:27:38'),(8,'屏幕截图 2024-04-24 202725.png','static/uploads/6c888b24-6eb7-4be6-8bec-118fe0032162.png','static/thumbnails/6c888b24-6eb7-4be6-8bec-118fe0032162.png',10162,181,197,'2025-12-25 23:27:52',NULL,'其他',15,2,'2025-12-25 15:27:52'),(9,'猫猫虫','static/uploads/f155da88-48c7-4db5-a322-b3f389b08823.png','static/thumbnails/f155da88-48c7-4db5-a322-b3f389b08823.png',32477,196,179,'2025-12-25 23:28:00','杭州','人像',29,2,'2025-12-25 15:28:00'),(10,'edited_屏幕截图 2024-04-24 202826.png','static/uploads/0b7e19f4-eec3-41d9-948a-c6f3142925d4.png','static/thumbnails/0b7e19f4-eec3-41d9-948a-c6f3142925d4.png',17482,144,111,'2025-12-25 23:32:44',NULL,'其他',12,2,'2025-12-25 15:32:43'),(11,'屏幕截图 2024-03-25 142227.png','static/uploads/44f3c7df-c227-41ee-b892-2d35f8254a5b.png','static/thumbnails/44f3c7df-c227-41ee-b892-2d35f8254a5b.png',218435,1929,1193,'2025-12-28 15:14:10',NULL,'其他',4,2,'2025-12-28 07:14:09'),(12,'屏幕截图 2024-03-24 212131.png','static/uploads/3052f060-9131-4947-b534-6e4f44874d26.png','static/thumbnails/3052f060-9131-4947-b534-6e4f44874d26.png',100129,813,1033,'2025-12-28 15:31:09',NULL,'其他',4,2,'2025-12-28 07:31:08'),(13,'屏幕截图 2024-03-30 210408.png','static/uploads/374b3683-e59e-4d9e-99fc-5933ce80f7e5.png','static/thumbnails/374b3683-e59e-4d9e-99fc-5933ce80f7e5.png',24115,801,113,'2025-12-28 22:45:06',NULL,'其他',16,2,'2025-12-28 14:45:06'),(14,'屏幕截图 2024-03-26 013006.png','static/uploads/69a6ed0b-db44-4f45-8088-51d2a533e68a.png','static/thumbnails/69a6ed0b-db44-4f45-8088-51d2a533e68a.png',530,12,104,'2025-12-28 22:45:06',NULL,'其他',5,2,'2025-12-28 14:45:06'),(15,'屏幕截图 2024-04-01 130827.png','static/uploads/e091bd92-4521-42ce-92db-db1dbf6a34f6.png','static/thumbnails/e091bd92-4521-42ce-92db-db1dbf6a34f6.png',7091,792,89,'2025-12-28 22:45:06','杭州','人像',11,2,'2025-12-28 14:45:06'),(16,'屏幕截图 2024-03-29 114643.png','static/uploads/eed93333-a077-409c-bbf9-a4569990c0b1.png','static/thumbnails/eed93333-a077-409c-bbf9-a4569990c0b1.png',46993,677,559,'2025-12-28 22:45:06',NULL,'其他',22,2,'2025-12-28 14:45:06'),(17,'屏幕截图 2024-03-24 212131.png','static/uploads/71cd76e4-71a7-4340-a2d7-16479562c1dc.png','static/thumbnails/71cd76e4-71a7-4340-a2d7-16479562c1dc.png',100129,813,1033,'2025-12-28 22:45:06',NULL,'其他',1,2,'2025-12-28 14:45:06'),(18,'屏幕截图 2024-04-01 130837.png','static/uploads/ba08b76f-bd74-4ee4-bdbc-9f246f0aa349.png','static/thumbnails/ba08b76f-bd74-4ee4-bdbc-9f246f0aa349.png',7018,798,87,'2025-12-28 22:45:06',NULL,'其他',0,2,'2025-12-28 14:45:06'),(19,'屏幕截图 2024-04-01 130934.png','static/uploads/c38eb79f-e182-46c1-baa1-8d1b093f98dc.png','static/thumbnails/c38eb79f-e182-46c1-baa1-8d1b093f98dc.png',7476,807,91,'2025-12-28 22:45:06','温州','其他',1,2,'2025-12-28 14:45:06'),(20,'屏幕截图 2024-03-25 142227.png','static/uploads/7608a4a5-45a4-407b-b4f8-8ad8dbe87304.png','static/thumbnails/7608a4a5-45a4-407b-b4f8-8ad8dbe87304.png',218435,1929,1193,'2025-12-28 22:45:06',NULL,'其他',5,2,'2025-12-28 14:45:06'),(21,'屏幕截图 2024-03-24 212131.png','static/uploads/1ebca528-a5dd-4f1c-9832-0194de099abb.png','static/thumbnails/1ebca528-a5dd-4f1c-9832-0194de099abb.png',100129,813,1033,'2025-12-28 22:45:06',NULL,'其他',20,2,'2025-12-28 14:45:06'),(22,'edited_屏幕截图 2024-04-01 130827.png','static/uploads/61114d8f-9d6e-447a-9825-0ec7c6b7bafb.png','static/thumbnails/61114d8f-9d6e-447a-9825-0ec7c6b7bafb.png',17217,320,36,'2025-12-28 22:51:07',NULL,'其他',13,2,'2025-12-28 14:51:06'),(23,'edited_edited_屏幕截图 2024-04-01 130827.png','static/uploads/414605fc-d14c-43bb-9201-00c1912b1732.png','static/thumbnails/414605fc-d14c-43bb-9201-00c1912b1732.png',17458,36,320,'2025-12-29 00:38:18',NULL,'其他',14,2,'2025-12-28 16:38:18'),(24,'edited_edited_edited_屏幕截图 2024-04-01 130827.png','static/uploads/4eb8fb54-56f5-4059-87fe-eaab6c60032b.png','static/thumbnails/4eb8fb54-56f5-4059-87fe-eaab6c60032b.png',17508,36,320,'2025-12-29 01:34:54',NULL,'其他',7,2,'2025-12-28 17:34:53'),(25,'Screenshot_20251225_025920_com.tencent.mm_edit_32015704177055.jpg','static/uploads/ffd9f4e0-6ed0-40b1-9da9-b4f91b89621e.jpg','static/thumbnails/ffd9f4e0-6ed0-40b1-9da9-b4f91b89621e.jpg',743694,2800,1840,'2025-12-29 11:58:17',NULL,'其他',9,4,'2025-12-29 03:58:17'),(26,'Screenshot_20251229_115852_com.huawei.browser.jpg','static/uploads/a6ce92d7-1619-4c5e-a695-ee0c45a2c861.jpg','static/thumbnails/a6ce92d7-1619-4c5e-a695-ee0c45a2c861.jpg',510054,1840,2800,'2025-12-29 12:04:58',NULL,'其他',7,4,'2025-12-29 04:04:57'),(27,'Screenshot_20251225_025920_com.tencent.mm_edit_32015704177055.jpg','static/uploads/b24d666a-ce28-4b03-9a14-bb203b47edee.jpg','static/thumbnails/b24d666a-ce28-4b03-9a14-bb203b47edee.jpg',743694,2800,1840,'2025-12-29 12:04:58',NULL,'其他',4,4,'2025-12-29 04:04:58'),(28,'屏幕截图 2024-03-25 160227.png','static/uploads/cb112693-e47f-4b2a-be7e-036a9935bb9c.png','static/thumbnails/cb112693-e47f-4b2a-be7e-036a9935bb9c.png',128146,587,1059,'2025-12-29 23:22:58',NULL,'其他',4,2,'2025-12-29 15:22:58'),(29,'屏幕截图 2024-03-24 212151.png','static/uploads/4f877408-188e-4c8f-b944-ca1b3e34410e.png','static/thumbnails/4f877408-188e-4c8f-b944-ca1b3e34410e.png',93428,910,944,'2025-12-29 23:22:58',NULL,'其他',0,2,'2025-12-29 15:22:58'),(30,'edited_屏幕截图 2024-03-25 160227.png','static/uploads/c3017a38-eb97-41e4-b4e5-fc474a7e0154.png','static/thumbnails/c3017a38-eb97-41e4-b4e5-fc474a7e0154.png',70835,222,400,'2025-12-29 23:23:23',NULL,'其他',1,2,'2025-12-29 15:23:23'),(31,'edited_屏幕截图 2024-04-24 202725.png','static/uploads/5df79382-8596-4238-aa7f-87b53147e0a0.png','static/thumbnails/5df79382-8596-4238-aa7f-87b53147e0a0.png',19984,197,181,'2025-12-29 23:36:39',NULL,'其他',12,2,'2025-12-29 15:36:39'),(32,'edited_edited_屏幕截图 2024-04-24 202725.png','static/uploads/d6eb30cb-5aa5-4457-8f40-1e0be3626832.png','static/thumbnails/d6eb30cb-5aa5-4457-8f40-1e0be3626832.png',10254,272,272,'2025-12-30 00:10:28',NULL,'其他',7,2,'2025-12-29 16:10:27'),(33,'edited_edited_edited_屏幕截图 2024-04-24 202725.png','static/uploads/5251a233-6611-47bd-a4b1-919ad5c7fcd1.png','static/thumbnails/5251a233-6611-47bd-a4b1-919ad5c7fcd1.png',15721,408,408,'2025-12-30 00:19:18',NULL,'其他',3,2,'2025-12-29 16:19:18'),(34,'edited_edited_屏幕截图 2024-04-24 202725.png','static/uploads/d20035f3-86c7-47e4-8d66-efc8ec461195.png','static/thumbnails/d20035f3-86c7-47e4-8d66-efc8ec461195.png',9855,272,272,'2025-12-30 00:37:15',NULL,'其他',0,2,'2025-12-29 16:37:15'),(35,'edited_edited_屏幕截图 2024-04-24 202725.png','static/uploads/cf16c71b-9aef-429c-ae50-e11c17e61356.png','static/thumbnails/cf16c71b-9aef-429c-ae50-e11c17e61356.png',9357,260,255,'2025-12-30 00:37:36',NULL,'其他',4,2,'2025-12-29 16:37:36'),(36,'edited_edited_屏幕截图 2024-04-24 202725.png','static/uploads/e237426f-4b36-40f9-9c50-dcb7b57104eb.png','static/thumbnails/e237426f-4b36-40f9-9c50-dcb7b57104eb.png',6836,181,197,'2025-12-30 00:46:15',NULL,'其他',0,2,'2025-12-29 16:46:15'),(37,'屏幕截图 2025-12-27 143221.png','static/uploads/d5e801eb-0cf6-49eb-889e-bb909b638f4b.png','static/thumbnails/d5e801eb-0cf6-49eb-889e-bb909b638f4b.png',23386,584,458,'2025-12-31 17:36:35',NULL,'其他',2,2,'2025-12-31 09:36:34'),(38,'屏幕截图 2024-03-24 212131.png','static/uploads/0f562fbb-04de-45fe-a237-56211c0c4ede.png','static/thumbnails/0f562fbb-04de-45fe-a237-56211c0c4ede.png',100129,813,1033,'2025-12-31 19:51:43',NULL,'其他',4,2,'2025-12-31 11:51:43'),(39,'wx_camera_1767096660730.jpg','static/uploads/5044dd05-a9aa-4df1-962e-d0729cdcda9c.jpg','static/thumbnails/5044dd05-a9aa-4df1-962e-d0729cdcda9c.jpg',1350232,1920,1080,'2025-12-31 19:53:26',NULL,'其他',4,2,'2025-12-31 11:53:25'),(40,'edited_wx_camera_1767096660730.jpg','static/uploads/759c0b05-f304-4b69-ae7f-735276861cab.jpg','static/thumbnails/759c0b05-f304-4b69-ae7f-735276861cab.jpg',461963,1080,1800,'2025-12-31 19:59:43',NULL,'其他',12,2,'2025-12-31 11:59:42'),(41,'屏幕截图 2024-03-24 212131.png','static/uploads/ea7facb4-e2b1-4541-8b59-b071cec1fc46.png','static/thumbnails/ea7facb4-e2b1-4541-8b59-b071cec1fc46.png',100129,813,1033,'2025-12-31 19:04:27',NULL,'其他',2,2,'2025-12-31 19:04:27'),(42,'屏幕截图 2024-03-24 212151.png','static/uploads/4ccc3ef7-7151-47b0-8922-17f085b07ca3.png','static/thumbnails/4ccc3ef7-7151-47b0-8922-17f085b07ca3.png',93428,910,944,'2025-12-31 19:08:44',NULL,'其他',4,2,'2025-12-31 19:08:44'),(43,'屏幕截图 2024-04-15 222009.png','static/uploads/1aaa0506-7da4-425c-82db-9f6c8c420f19.png','static/thumbnails/1aaa0506-7da4-425c-82db-9f6c8c420f19.png',22868,478,351,'2025-12-31 19:09:12',NULL,'其他',1,2,'2025-12-31 19:09:12'),(44,'edited_屏幕截图 2024-03-24 212151.png','static/uploads/b84f081c-8a16-4623-9d1c-17334c6a71e0.png','static/thumbnails/b84f081c-8a16-4623-9d1c-17334c6a71e0.png',57587,731,654,'2025-12-31 19:10:13',NULL,'其他',1,2,'2025-12-31 19:10:13'),(45,'屏幕截图 2024-03-24 212151.png','static/uploads/fb34595b-3d5d-451f-96ee-d773f5938456.png','static/thumbnails/fb34595b-3d5d-451f-96ee-d773f5938456.png',93428,910,944,'2025-12-31 19:13:37',NULL,'其他',0,6,'2025-12-31 19:13:37'),(46,'屏幕截图 2024-03-25 142227.png','static/uploads/46efa7f5-1cf6-49aa-8e55-9267f264d11e.png','static/thumbnails/46efa7f5-1cf6-49aa-8e55-9267f264d11e.png',218435,1929,1193,'2025-12-31 19:13:37',NULL,'其他',0,6,'2025-12-31 19:13:37'),(47,'屏幕截图 2024-03-25 160227.png','static/uploads/b3d3d063-4fe4-40fb-bfcb-6d22ab8f6f48.png','static/thumbnails/b3d3d063-4fe4-40fb-bfcb-6d22ab8f6f48.png',128146,587,1059,'2025-12-31 19:13:37',NULL,'其他',0,6,'2025-12-31 19:13:37');
/*!40000 ALTER TABLE `images` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tags`
--

DROP TABLE IF EXISTS `tags`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tags` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_tags_name` (`name`),
  KEY `ix_tags_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=114 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tags`
--

LOCK TABLES `tags` WRITE;
/*!40000 ALTER TABLE `tags` DISABLE KEYS */;
INSERT INTO `tags` VALUES (41,'aaa'),(1,'arcaea'),(49,'c'),(11,'c++'),(34,'c++代码'),(104,'c语言'),(24,'c语言代码'),(2,'data'),(13,'dfs'),(40,'kkk'),(73,'二分查找'),(5,'二叉搜索树'),(95,'二叉树'),(12,'二叉树构建'),(69,'代码'),(10,'代码片段'),(21,'伪代码'),(54,'列表'),(83,'动物'),(88,'动物角色'),(82,'动画风格'),(78,'卡通'),(81,'可爱'),(55,'哲学'),(50,'唉唉'),(51,'啦啦啦'),(48,'喔喔喔'),(64,'在线教学'),(56,'在线讲座'),(60,'在线课堂'),(90,'多选题'),(106,'大凶'),(57,'学习'),(65,'学习平台'),(61,'学习材料'),(97,'寿司'),(28,'循环结构'),(108,'情绪对线'),(87,'插画'),(77,'搜索'),(62,'政治理论'),(68,'教学内容'),(63,'教材展示'),(59,'教育'),(66,'教育工具'),(45,'数据'),(105,'数据处理'),(16,'数据对比'),(14,'数据结构'),(4,'文本'),(47,'文本信息'),(53,'文本内容'),(29,'文本比较'),(100,'日式料理'),(101,'木桌'),(71,'树'),(25,'树结构'),(96,'树节点定义'),(8,'样例输入'),(30,'样本分析'),(17,'样本验证'),(99,'橘子'),(102,'橙子'),(19,'正确与错误'),(107,'水讨论区'),(36,'深度优先搜索'),(58,'演示文稿'),(109,'熬夜'),(52,'版本信息'),(31,'版本对比'),(18,'版本测试'),(46,'版本管理'),(42,'版本验证'),(3,'猫猫虫'),(89,'甜美'),(111,'程序设计'),(74,'空间复杂度'),(23,'章节标题'),(85,'简单'),(84,'简约'),(76,'算法'),(72,'算法分析'),(103,'算法示例'),(20,'算法规范'),(38,'算法设计'),(44,'粉色'),(70,'编程'),(113,'编程题'),(94,'考试题'),(86,'胖胖的'),(26,'节点定义'),(79,'蓝色'),(91,'蛋白质来源'),(15,'表格'),(32,'表格数据'),(67,'视频会议'),(110,'警告'),(9,'计算机'),(6,'输入规范'),(27,'输入输出'),(112,'输入输出格式'),(39,'输入输出规范'),(7,'输出规范'),(75,'迭代'),(35,'递归'),(93,'问答形式'),(22,'问题解决'),(43,'颜色'),(92,'食物分类'),(98,'餐盘'),(80,'鱼');
/*!40000 ALTER TABLE `tags` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `created_at` timestamp NULL DEFAULT (now()),
  `is_active` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_users_username` (`username`),
  UNIQUE KEY `ix_users_email` (`email`),
  KEY `ix_users_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'admin','admin@test.com','$2b$12$9wwxBJbUJR31chSPk4BMeu3jz6dgPOSOIOkC2L8mMuzoXtlrC0O2K','2025-12-25 13:50:25',1),(2,'Keer','321600175@qq.com','$2b$12$K7hTmWkPIAwMeZlSTMNUU.NVOr0wAzDN4bj0uW6S6fd0MovI.yJr.','2025-12-25 14:00:42',1),(3,'test','333@zju.com','$2b$12$SJrmgT3EIKaLJ/J0qQo9VeCQCtFgo52QDRjil6dmnSq2aUm0Uxkky','2025-12-25 15:29:13',1),(4,'jinke','aaa@qq.com','$2b$12$wBbBc7SbZs6yB2V8Eqhuou3ilncDAJ.TTl9bsVSuhJQkYB0TUOwNO','2025-12-29 03:57:49',1),(5,'Keeee','3216175@qq.com','$2b$12$LUKRX1rqXXhC8un0jpaP5uC9AmgrJ7bhHj7H7wSTfaToQZ14hq9Li','2025-12-29 15:13:36',1),(6,'admin123','11111@qq.com','$2b$12$fWkPa1ivLiarIlPiUUtL0OZMSnv1WkMZa8xc5lXKTwuq0x896o5My','2025-12-31 19:13:22',1);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-01-01  7:15:48
