-- phpMyAdmin SQL Dump
-- version 2.11.6
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Apr 25, 2025 at 03:45 PM
-- Server version: 5.0.51
-- PHP Version: 5.2.6

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `railway_booking`
--

-- --------------------------------------------------------

--
-- Table structure for table `admin`
--

CREATE TABLE `admin` (
  `username` varchar(30) NOT NULL,
  `password` varchar(30) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `admin`
--

INSERT INTO `admin` (`username`, `password`) VALUES
('admin', 'admin');

-- --------------------------------------------------------

--
-- Table structure for table `bookings`
--

CREATE TABLE `bookings` (
  `id` int(11) NOT NULL auto_increment,
  `booking_id` varchar(20) default NULL,
  `transport_id` int(11) default NULL,
  `travel_date` date default NULL,
  `passengers` int(11) default NULL,
  `status` varchar(20) default NULL,
  `transport_number` varchar(255) default NULL,
  `user_email` varchar(255) default NULL,
  `total_fare` decimal(10,2) default NULL,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=16 ;

--
-- Dumping data for table `bookings`
--

INSERT INTO `bookings` (`id`, `booking_id`, `transport_id`, `travel_date`, `passengers`, `status`, `transport_number`, `user_email`, `total_fare`) VALUES
(1, 'BOOK-3248', 0, '2025-04-28', 2, 'Confirmed', NULL, NULL, NULL),
(2, 'BOOK-2386', 0, '2025-05-12', 3, 'Cancelled', 'TN 72 as 4270', NULL, NULL),
(3, 'BOOK-7954', 0, '2025-05-12', 3, 'Confirmed', 'TN 72 as 4270', NULL, NULL),
(4, 'BOOK-4974', 0, '2025-05-12', 3, 'Confirmed', 'TN 72 as 4270', NULL, NULL),
(5, 'BOOK-4692', 0, '2025-05-12', 3, 'Confirmed', 'TN 72 as 4270', NULL, NULL),
(6, 'BOOK-3769', 0, '2025-05-12', 3, 'Confirmed', 'TN 72 as 4270', NULL, NULL),
(7, 'BOOK-4237', 0, '2025-05-12', 3, 'Confirmed', 'TN 72 as 4270', NULL, NULL),
(8, 'BOOK-7899', 0, '2025-05-12', 3, 'Confirmed', 'TN 72 as 4270', NULL, NULL),
(9, 'BOOK-9835', 0, '2025-05-12', 3, 'Confirmed', 'TN 72 as 4270', NULL, NULL),
(10, 'BOOK-4329', 0, '2025-05-12', 3, 'Cancelled', 'TN 72 as 4270', 'kalirajan3079@gmail.com', '1650.00'),
(11, 'BOOK-3292', 0, '2025-05-12', 3, 'Confirmed', 'TN 72 as 4270', 'kalirajan3079@gmail.com', '1650.00'),
(12, 'BOOK-2001', 0, '2025-05-12', 3, 'Confirmed', 'TN 72 as 4270', 'kalirajan3079@gmail.com', '1650.00'),
(13, 'BOOK-6397', 0, '2025-05-12', 3, 'Confirmed', 'TN 72 as 4270', 'kalirajan3079@gmail.com', '1650.00'),
(14, 'BOOK-6868', 0, '2025-05-12', 3, 'Cancelled', 'TN 72 as 4270', 'kalirajan3079@gmail.com', '1650.00'),
(15, 'BOOK-4755', 0, '2025-05-12', 3, 'Confirmed', 'TN 72 as 4270', 'kalirajan3079@gmail.com', '1650.00');

-- --------------------------------------------------------

--
-- Table structure for table `train_details`
--

CREATE TABLE `train_details` (
  `id` int(11) NOT NULL,
  `train_name` varchar(30) NOT NULL,
  `train_number` varchar(30) NOT NULL,
  `source` varchar(30) NOT NULL,
  `destination` varchar(30) NOT NULL,
  `departure_time` varchar(30) NOT NULL,
  `arrival_time` varchar(30) NOT NULL,
  `running_days` varchar(30) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `train_details`
--

INSERT INTO `train_details` (`id`, `train_name`, `train_number`, `source`, `destination`, `departure_time`, `arrival_time`, `running_days`) VALUES
(0, 'Nellai express', '12345', 'Maduurai', 'Trichy', '12:00', '12:40', 'Mon, Wed'),
(0, 'Okha Express', '34636', 'Maduurai', 'Trichy', '13:00', '13:30', 'Fri');

-- --------------------------------------------------------

--
-- Table structure for table `transport`
--

CREATE TABLE `transport` (
  `id` int(11) NOT NULL,
  `transport_type` varchar(10) default NULL,
  `transport_name` varchar(100) default NULL,
  `source` varchar(100) default NULL,
  `destination` varchar(100) default NULL,
  `departure_time` time default NULL,
  `arrival_time` time default NULL,
  `fare` decimal(10,2) default NULL,
  `transport_number` varchar(255) default NULL,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `transport`
--

INSERT INTO `transport` (`id`, `transport_type`, `transport_name`, `source`, `destination`, `departure_time`, `arrival_time`, `fare`, `transport_number`) VALUES
(0, 'bus', 'SC8908', 'Maduurai', 'Trichy', '12:00:00', '06:00:00', '550.00', 'TN 72 as 4270');

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

CREATE TABLE `user` (
  `id` int(11) NOT NULL,
  `name` varchar(30) NOT NULL,
  `email` varchar(30) NOT NULL,
  `mobile` varchar(30) NOT NULL,
  `username` varchar(30) NOT NULL,
  `password` varchar(30) NOT NULL,
  `date_join` varchar(30) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `user`
--

INSERT INTO `user` (`id`, `name`, `email`, `mobile`, `username`, `password`, `date_join`) VALUES
(1, 'Sankaar', 'kalirajan3079@gmail.com', '8838468320', 'raja', '1234', '2025-04-25');
