-- 创建 users 表，用于登录/注册
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL,
  phone TEXT NOT NULL UNIQUE,
  password TEXT NOT NULL
);

-- 创建 info 表，用于存储人员信息
CREATE TABLE IF NOT EXISTS info (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  phone TEXT NOT NULL,
  title TEXT NOT NULL,
  address TEXT NOT NULL,
  image BLOB,
  UNIQUE(name, phone)
);
