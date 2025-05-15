create schema news_project;
# drop schema news_project;
# drop table news_project.search_information;


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
    open_price INT,
    high_price  INT,
    low_price  INT,
    close_price INT,
    price_change INT,
    trading_volume INT,
    date DATE
);