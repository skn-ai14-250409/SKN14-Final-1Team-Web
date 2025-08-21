-- Active: 1753716315111@@127.0.0.1@3306@codenovadb
-- pip install mysqlclient

-- # root 계정으로 접속
-- # 사용자 codenovadb/django 생성

-- create user 'django'@'%' identified by 'django';

-- # 데이터베이스 생성
-- # - 인코딩 utf8mb4 (다국어/이모지 텍스트 지원 ver)
-- # - 정렬방식 utf8mb4_unicode_ci (대소문자 구분없음)
-- create database codenovadb character set utf8mb4 collate utf8mb4_unicode_ci;

-- # django 계정 권한 부여
-- grant all privileges on codenovadb.* to 'django'@'%';


-- flush privileges;

-- app > models.py 작업 후
-- python manage.py makemigrations
-- python manage.py migrate