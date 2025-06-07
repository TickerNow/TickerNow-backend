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
    joined_at  DATE NOT NULL,
    is_admin BOOLEAN NOT NULL DEFAULT FALSE
);

drop table news_project.user_info;

DELETE FROM news_project.user_info
WHERE id = 'test' and is_admin = FALSE;

UPDATE news_project.user_info set is_admin=TRUE where id='dndjeh';

CREATE TABLE conversation_history (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    role ENUM('user', 'assistant') NOT NULL,
    content TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

# drop table conversation_history;
