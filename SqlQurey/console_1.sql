use news_project;


create table search_information(
    title bigint unsigned primary key auto_increment,
    summary MEDIUMTEXT,
    date DATE,
    href TEXT
);