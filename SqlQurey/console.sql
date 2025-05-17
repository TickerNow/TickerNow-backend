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

select *
from news_project.daum_financial_stock_table
where name LIKE '%SK%'
ORDER BY date DESC ;