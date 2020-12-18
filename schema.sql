create database IF NOT EXISTS python_article 
DEFAULT CHARACTER SET utf8mb4  COLLATE   utf8mb4_unicode_ci


-- 要一个个执行
create table `users`(
    `id` varchar(50) NOT NULL COMMENT '主键', 
    `email` varchar(50) NOT NULL COMMENT '用户邮箱', 
    `password` varchar(50) NOT NULL COMMENT '用户密码', 
    `admin` Bool NOT NULL COMMENT '是否为管理员', 
    `name` varchar(50) not null COMMENT '用户名', 
    `avatar` varchar(500) DEFAULT NULL COMMENT '用户头像', 
    `created_at` real NOT NULL COMMENT '创建时间', 
    unique key `idx_email`(`email`), 
    key `idx_created_at`(`created_at`), 
    primary key(`id`)) engine= innodb DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
create table `blogs`(
    `id` int(11) not null AUTO_INCREMENT COMMENT '主键', 
    `user_id` varchar(50) not null COMMENT '创建者id', 
    `user_name` varchar(50) not null COMMENT '创建者名字', 
    `user_avatar` varchar(500) DEFAULT NULL COMMENT '创建者头像', 
    `name` varchar(50)  not null COMMENT '文章名字', 
    `summary` varchar(200) not null COMMENT '文章简介', 
    `content` mediumtext not null COMMENT '文章内容', 
    `created_at` real not null COMMENT '创建时间', 
    key `idx_created_at`(`created_at`), 
    primary key(`id`)) engine= innodb DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
create table `comments`(
    `id` varchar(50) not null COMMENT '主键', 
    `blog_id` int(11) not null COMMENT '评论所属文章id', 
    `user_id` varchar(50) not null COMMENT '评论者', 
    `user_name` varchar(50) not null COMMENT '评论者名字',
    `user_avatar` varchar(500) DEFAULT NULL COMMENT '评论者头像', 
    `content` mediumtext not null COMMENT '评论内容', 
    `created_at` real not null COMMENT '创建时间', 
    key `idx_created_at`(`created_at`), primary key(`id`)) engine= innodb DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci