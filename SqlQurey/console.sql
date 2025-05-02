create schema news_project;

create table news_project.search_information(
    user_id bigint unsigned primary key auto_increment,
    title varchar(50)NOT NULL ,
    summary MEDIUMTEXT,
    date DATE,
    href TEXT
);