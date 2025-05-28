# create schema news_project;
# drop schema news_project;
# drop table news_project.search_information;
# drop table news_project.daum_financial_stock_table;

create table news_project.search_information(
    id bigint unsigned primary key auto_increment,
    title varchar(200)NOT NULL ,
    content MEDIUMTEXT,
    date DATE,
    url TEXT
);

create table news_project.daum_financial_stock_table(
    id bigint unsigned primary key auto_increment,
    name varchar(50)NOT NULL ,
    open_price INT NOT NULL,
    high_price  INT NOT NULL,
    low_price  INT NOT NULL,
    close_price INT NOT NULL,
    price_change text NOT NULL,
    change_rate text NOT NULL,
    trading_volume INT NOT NULL,
    date DATE NOT NULL
);

select distinct (name)
from news_project.daum_financial_stock_table;

create table news_project.user_info(
    user_id bigint unsigned primary key auto_increment,
    name text NOT NULL,
    sex char(2) NOT NULL,
    age INT NOT NULL,
    birth_date date NOT NULL,
    nickname text NOT NULL,
    id text NOT NULL,
    password text NOT NULL,
    joined_at  DATE NOT NULL
);

INSERT INTO news_project.user_info (name, sex, age, birth_date, nickname, id, password, joined_at)
VALUES
  ('park', '남자', 20, '2000-05-02', '뭐야', 'dndjeh', '1111', '2024-05-02'),
  ('So', '여자', 21, '2003-07-14','아무거나', 'soso123', '2222', '2024-05-18'),
  ('Kim','남자', 21,'2000-02-14', '이건아님','dign','3333','2025-04-12');

drop table news_project.user_info;
DELETE FROM news_project.user_info
WHERE id = 'dndjeh';

