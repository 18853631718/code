-- AI Code Review System MySQL Database Schema
-- Database Name: ai_code_review

CREATE DATABASE IF NOT EXISTS ai_code_review CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE ai_code_review;

-- 代码文件表
CREATE TABLE IF NOT EXISTS code_files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(255) NOT NULL COMMENT '文件名',
    language VARCHAR(50) NOT NULL COMMENT '编程语言',
    content TEXT NOT NULL COMMENT '代码内容',
    created_at DATETIME DEFAULT (NOW()) COMMENT '创建时间',
    updated_at DATETIME DEFAULT (NOW()) ON UPDATE NOW() COMMENT '更新时间',
    INDEX idx_language (language),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='代码文件表';

-- 分析结果表
CREATE TABLE IF NOT EXISTS analysis_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    file_id INT NOT NULL COMMENT '代码文件ID',
    defect_type VARCHAR(100) COMMENT '缺陷类型',
    confidence FLOAT COMMENT '置信度',
    line_number INT COMMENT '缺陷行号',
    suggestion TEXT COMMENT '修复建议',
    severity VARCHAR(20) DEFAULT 'medium' COMMENT '严重程度: high/medium/low/none',
    created_at DATETIME DEFAULT (NOW()) COMMENT '创建时间',
    INDEX idx_file_id (file_id),
    INDEX idx_defect_type (defect_type),
    INDEX idx_severity (severity),
    FOREIGN KEY (file_id) REFERENCES code_files(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='分析结果表';

-- 审查会话表
CREATE TABLE IF NOT EXISTS review_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL COMMENT '会话名称',
    owner VARCHAR(100) NOT NULL COMMENT '创建者',
    status VARCHAR(20) DEFAULT 'active' COMMENT '状态: active/closed',
    participants TEXT COMMENT '参与者列表，逗号分隔',
    code_content TEXT COMMENT '会话中的代码内容',
    created_at DATETIME DEFAULT (NOW()) COMMENT '创建时间',
    updated_at DATETIME DEFAULT (NOW()) ON UPDATE NOW() COMMENT '更新时间',
    INDEX idx_owner (owner),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='审查会话表';

-- 审查评论表
CREATE TABLE IF NOT EXISTS review_comments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT NOT NULL COMMENT '会话ID',
    author VARCHAR(100) NOT NULL COMMENT '评论作者',
    content TEXT NOT NULL COMMENT '评论内容',
    line_number INT COMMENT '评论对应的行号',
    created_at DATETIME DEFAULT (NOW()) COMMENT '创建时间',
    INDEX idx_session_id (session_id),
    INDEX idx_author (author),
    FOREIGN KEY (session_id) REFERENCES review_sessions(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='审查评论表';

-- 用户表（可选，用于扩展）
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE COMMENT '用户名',
    email VARCHAR(255) UNIQUE COMMENT '邮箱',
    password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
    role VARCHAR(20) DEFAULT 'user' COMMENT '角色: admin/user',
    created_at DATETIME DEFAULT (NOW()) COMMENT '创建时间',
    updated_at DATETIME DEFAULT (NOW()) ON UPDATE NOW() COMMENT '更新时间',
    INDEX idx_username (username)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- 项目表（可选，存储多个代码项目）
CREATE TABLE IF NOT EXISTS projects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL COMMENT '项目名称',
    description TEXT COMMENT '项目描述',
    owner_id INT COMMENT '项目所有者',
    language VARCHAR(50) COMMENT '主要编程语言',
    created_at DATETIME DEFAULT (NOW()) COMMENT '创建时间',
    updated_at DATETIME DEFAULT (NOW()) ON UPDATE NOW() COMMENT '更新时间',
    INDEX idx_owner_id (owner_id),
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='项目表';

-- 缺陷类型统计表（用于统计分析）
CREATE TABLE IF NOT EXISTS defect_statistics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL COMMENT '统计日期',
    defect_type VARCHAR(100) NOT NULL COMMENT '缺陷类型',
    count INT DEFAULT 0 COMMENT '数量',
    UNIQUE KEY uk_date_type (date, defect_type),
    INDEX idx_date (date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='缺陷统计表';
