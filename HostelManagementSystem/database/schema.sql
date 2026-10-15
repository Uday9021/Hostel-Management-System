-- Schema used by the Java Swing Hostel Management System.
-- Run this file against a MySQL server before launching the desktop app.

CREATE DATABASE IF NOT EXISTS nugasewana
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE nugasewana;

CREATE TABLE IF NOT EXISTS hostel (
    HID VARCHAR(20) NOT NULL,
    No_of_Rooms INT NOT NULL DEFAULT 0,
    Gender_of_residence VARCHAR(30) NOT NULL,
    phone_Number VARCHAR(30) NOT NULL,
    Address VARCHAR(255) NOT NULL,
    PRIMARY KEY (HID)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS type (
    TID VARCHAR(20) NOT NULL,
    Price DECIMAL(10, 2) NOT NULL DEFAULT 0,
    Name VARCHAR(80) NOT NULL,
    Description VARCHAR(255) NOT NULL DEFAULT '',
    PRIMARY KEY (TID),
    UNIQUE KEY uq_type_name (Name)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS facility (
    FID VARCHAR(20) NOT NULL,
    Name VARCHAR(100) NOT NULL,
    PRIMARY KEY (FID),
    UNIQUE KEY uq_facility_name (Name)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS facility_type (
    TID VARCHAR(20) NOT NULL,
    FID VARCHAR(20) NOT NULL,
    PRIMARY KEY (TID, FID),
    CONSTRAINT fk_facility_type_type FOREIGN KEY (TID)
        REFERENCES type (TID) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_facility_type_facility FOREIGN KEY (FID)
        REFERENCES facility (FID) ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS room (
    Room_no VARCHAR(20) NOT NULL,
    TID VARCHAR(20) NOT NULL,
    HID VARCHAR(20) NOT NULL,
    No_of_beds INT NOT NULL,
    Floor_number INT NOT NULL DEFAULT 0,
    Current_Borders_count INT NOT NULL DEFAULT 0,
    Width DECIMAL(8, 2) NOT NULL DEFAULT 0,
    Length DECIMAL(8, 2) NOT NULL DEFAULT 0,
    PRIMARY KEY (Room_no),
    KEY idx_room_hostel (HID),
    KEY idx_room_type (TID),
    CONSTRAINT fk_room_hostel FOREIGN KEY (HID)
        REFERENCES hostel (HID) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_room_type FOREIGN KEY (TID)
        REFERENCES type (TID) ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS guest (
    GID VARCHAR(20) NOT NULL,
    Full_name VARCHAR(120) NOT NULL,
    NIC VARCHAR(40) NOT NULL,
    Address VARCHAR(255) NOT NULL,
    Work_place VARCHAR(120) NOT NULL DEFAULT '',
    Phone_No VARCHAR(30) NOT NULL,
    E_mail VARCHAR(160) NOT NULL DEFAULT '',
    profession VARCHAR(100) NOT NULL DEFAULT '',
    gender VARCHAR(30) NOT NULL,
    PRIMARY KEY (GID),
    UNIQUE KEY uq_guest_nic (NIC)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS reservation (
    REID VARCHAR(20) NOT NULL,
    Room_no VARCHAR(20) NOT NULL,
    GID VARCHAR(20) NOT NULL,
    Payment_date VARCHAR(30) NOT NULL,
    Checking_date VARCHAR(30) NOT NULL,
    Checking_out VARCHAR(30) NOT NULL,
    Booking_date VARCHAR(30) NOT NULL,
    Key_money_amount DECIMAL(10, 2) NOT NULL DEFAULT 0,
    PRIMARY KEY (REID),
    KEY idx_reservation_room (Room_no),
    KEY idx_reservation_guest (GID),
    CONSTRAINT fk_reservation_room FOREIGN KEY (Room_no)
        REFERENCES room (Room_no) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_reservation_guest FOREIGN KEY (GID)
        REFERENCES guest (GID) ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS key_money (
    KID VARCHAR(20) NOT NULL,
    GID VARCHAR(20) NOT NULL,
    paidDate VARCHAR(30) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL DEFAULT 0,
    Pay_BackDate VARCHAR(30) NOT NULL DEFAULT '',
    PRIMARY KEY (KID),
    KEY idx_key_money_guest (GID),
    CONSTRAINT fk_key_money_guest FOREIGN KEY (GID)
        REFERENCES guest (GID) ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS monthly_payment (
    mpid VARCHAR(20) NOT NULL,
    GID VARCHAR(20) NOT NULL,
    Amount DECIMAL(10, 2) NOT NULL DEFAULT 0,
    payment_date VARCHAR(30) NOT NULL,
    nextPaymentDate VARCHAR(30) NOT NULL,
    PRIMARY KEY (mpid),
    KEY idx_monthly_payment_guest (GID),
    CONSTRAINT fk_monthly_payment_guest FOREIGN KEY (GID)
        REFERENCES guest (GID) ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS user_account (
    UserName VARCHAR(80) NOT NULL,
    password VARCHAR(255) NOT NULL,
    PRIMARY KEY (UserName)
) ENGINE=InnoDB;
