-- schema.sql

-- 创建 users 表，用于存储用户信息
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    phone TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
);

-- 创建 info 表，用于存储 信息
CREATE TABLE IF NOT EXISTS info (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    title TEXT NOT NULL,
    address TEXT NOT NULL,
    image BLOB
);

-- 创建 deleted_info 表，用于存储已删除的 信息
CREATE TABLE IF NOT EXISTS deleted_info (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    title TEXT NOT NULL,
    address TEXT NOT NULL,
    image BLOB,
    deleted_at TEXT NOT NULL
);


CREATE INDEX IF NOT EXISTS idx_info_name ON info(name);
CREATE INDEX IF NOT EXISTS idx_info_phone ON info(phone);