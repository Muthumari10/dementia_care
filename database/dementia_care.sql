

--
-- Database: `dementia_care`
--

-- --------------------------------------------------------

--
-- Table structure for table `admin`
--

CREATE TABLE `admin` (
  `id` int(11) NOT NULL auto_increment,
  `username` varchar(50) default NULL,
  `password` varchar(255) default NULL,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

--
-- Dumping data for table `admin`
--


-- --------------------------------------------------------

--
-- Table structure for table `caregivers`
--

CREATE TABLE `caregivers` (
  `id` int(11) NOT NULL auto_increment,
  `name` varchar(100) default NULL,
  `mobile` varchar(15) default NULL,
  `email` varchar(100) default NULL,
  `username` varchar(50) default NULL,
  `password` varchar(255) default NULL,
  PRIMARY KEY  (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=3 ;

--
-- Dumping data for table `caregivers`
--

-- --------------------------------------------------------

--
-- Table structure for table `chatbot_logs`
--

CREATE TABLE `chatbot_logs` (
  `id` int(11) NOT NULL auto_increment,
  `patient_id` int(11) NOT NULL,
  `question` text,
  `answer` text,
  `timestamp` timestamp NOT NULL default CURRENT_TIMESTAMP,
  PRIMARY KEY  (`id`),
  KEY `patient_id` (`patient_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=11 ;

--
-- Dumping data for table `chatbot_logs`
--


-- --------------------------------------------------------

--
-- Table structure for table `dementia_tests`
--

CREATE TABLE `dementia_tests` (
  `id` int(11) NOT NULL auto_increment,
  `patient_id` int(11) default NULL,
  `age` int(11) default NULL,
  `blood_pressure` int(11) default NULL,
  `cholesterol` int(11) default NULL,
  `memory_test_1` int(11) default NULL,
  `memory_test_2` int(11) default NULL,
  `attention_test` int(11) default NULL,
  `language_test` int(11) default NULL,
  `orientation_test` int(11) default NULL,
  `problem_solving_test` int(11) default NULL,
  `daily_activity_score` int(11) default NULL,
  `visual_spatial_score` int(11) default NULL,
  `social_interaction_score` int(11) default NULL,
  `result` varchar(10) default NULL,
  `timestamp` timestamp NOT NULL default CURRENT_TIMESTAMP,
  PRIMARY KEY  (`id`),
  KEY `patient_id` (`patient_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=18 ;




-- --------------------------------------------------------

--
-- Table structure for table `games_scores`
--

CREATE TABLE `games_scores` (
  `id` int(11) NOT NULL auto_increment,
  `patient_id` int(11) NOT NULL,
  `game_name` varchar(100) NOT NULL,
  `score` int(11) default '0',
  `played_at` timestamp NOT NULL default CURRENT_TIMESTAMP,
  PRIMARY KEY  (`id`),
  KEY `patient_id` (`patient_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=10 ;



-- --------------------------------------------------------

--
-- Table structure for table `login_activity`
--

CREATE TABLE `login_activity` (
  `id` int(11) NOT NULL auto_increment,
  `user_id` int(11) NOT NULL,
  `role` enum('patient','caregiver','admin') NOT NULL,
  `login_time` timestamp NOT NULL default CURRENT_TIMESTAMP,
  `ip_address` varchar(50) default NULL,
  `status` enum('success','failed') default 'success',
  PRIMARY KEY  (`id`),
  KEY `user_id` (`user_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=51 ;



-- --------------------------------------------------------

--
-- Table structure for table `patients`
--

CREATE TABLE `patients` (
  `id` int(11) NOT NULL auto_increment,
  `name` varchar(100) default NULL,
  `mobile` varchar(15) default NULL,
  `email` varchar(100) default NULL,
  `location` varchar(100) default NULL,
  `username` varchar(50) default NULL,
  `password` varchar(255) default NULL,
  PRIMARY KEY  (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=2 ;



-- --------------------------------------------------------

--
-- Table structure for table `patient_caregivers`
--

CREATE TABLE `patient_caregivers` (
  `id` int(11) NOT NULL auto_increment,
  `patient_id` int(11) NOT NULL,
  `caregiver_id` int(11) NOT NULL,
  PRIMARY KEY  (`id`),
  KEY `patient_id` (`patient_id`),
  KEY `caregiver_id` (`caregiver_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=2 ;



-- --------------------------------------------------------

--
-- Table structure for table `patient_relatives`
--

CREATE TABLE `patient_relatives` (
  `id` int(11) NOT NULL auto_increment,
  `patient_id` int(11) NOT NULL,
  `relative_name` varchar(100) default NULL,
  `relation` varchar(50) default NULL,
  `face_encoding` longblob,
  `created_at` timestamp NOT NULL default CURRENT_TIMESTAMP,
  PRIMARY KEY  (`id`),
  KEY `patient_id` (`patient_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=7 ;



-- --------------------------------------------------------

--
-- Table structure for table `relatives`
--

CREATE TABLE `relatives` (
  `id` int(11) NOT NULL auto_increment,
  `patient_id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `relative_type` varchar(50) default NULL,
  `photo_path` varchar(255) default NULL,
  `face_encoding` longblob,
  PRIMARY KEY  (`id`),
  KEY `patient_id` (`patient_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=4 ;



-- --------------------------------------------------------

--
-- Table structure for table `relative_faces`
--

CREATE TABLE `relative_faces` (
  `id` int(11) NOT NULL auto_increment,
  `relative_id` int(11) default NULL,
  `face_encoding` longblob,
  `created_at` timestamp NOT NULL default CURRENT_TIMESTAMP,
  PRIMARY KEY  (`id`),
  KEY `relative_id` (`relative_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;



--
-- Table structure for table `reminders`
--

CREATE TABLE `reminders` (
  `id` int(11) NOT NULL auto_increment,
  `patient_id` int(11) default NULL,
  `title` varchar(255) default NULL,
  `description` text,
  `datetime` datetime default NULL,
  `sent_count` int(11) default '0',
  PRIMARY KEY  (`id`),
  KEY `patient_id` (`patient_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=13 ;


--
-- Constraints for table `chatbot_logs`
--
ALTER TABLE `chatbot_logs`
  ADD CONSTRAINT `chatbot_logs_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`id`);

--
-- Constraints for table `dementia_tests`
--
ALTER TABLE `dementia_tests`
  ADD CONSTRAINT `dementia_tests_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`id`);

--
-- Constraints for table `games_scores`
--
ALTER TABLE `games_scores`
  ADD CONSTRAINT `games_scores_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`id`);

--
-- Constraints for table `patient_caregivers`
--
ALTER TABLE `patient_caregivers`
  ADD CONSTRAINT `patient_caregivers_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `patient_caregivers_ibfk_2` FOREIGN KEY (`caregiver_id`) REFERENCES `caregivers` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `patient_relatives`
--
ALTER TABLE `patient_relatives`
  ADD CONSTRAINT `patient_relatives_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`id`);

--
-- Constraints for table `relatives`
--
ALTER TABLE `relatives`
  ADD CONSTRAINT `fk_patient` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`id`),
  ADD CONSTRAINT `relatives_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`id`);

--
-- Constraints for table `relative_faces`
--
ALTER TABLE `relative_faces`
  ADD CONSTRAINT `relative_faces_ibfk_1` FOREIGN KEY (`relative_id`) REFERENCES `patient_relatives` (`id`);

--
-- Constraints for table `reminders`
--
ALTER TABLE `reminders`
  ADD CONSTRAINT `reminders_ibfk_1` FOREIGN KEY (`patient_id`) REFERENCES `patients` (`id`);
