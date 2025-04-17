drop database secondsale_shopping;
create database secondsale_shopping;

use secondsale_shopping;


create table category(
category_id int auto_increment primary key,
category_name varchar(255) not null
);

create table sub_category(
sub_category_id int auto_increment primary key,
sub_category_name varchar(255) not null,
category_id int,
FOREIGN KEY (category_id) REFERENCES category(category_id)
);

create table user(
 user_id int auto_increment primary key,
 name varchar(255) not null,
 phone varchar(255) not null,
 email varchar(255) not null,
 password varchar(255) not null,
 about varchar(255) not null,
 address varchar(255) not null,
 status varchar(255) not null
 );
 
 create table product(
 product_id int auto_increment primary key,
 product_name varchar(255) not null,
 price varchar(255) not null,
 picture varchar(255) not null,
 description varchar(255) not null,
 posted_date varchar(255) not null,
 status varchar(255) not null,
 sub_category_id int,
 seller_id int,
 FOREIGN KEY (sub_category_id) REFERENCES sub_category(sub_category_id),
 FOREIGN KEY (seller_id) REFERENCES user(user_id)
 );
 
 
create table transaction(
 transaction_id int auto_increment primary key,
 requested_amount varchar(255) not null,
 seller_amount varchar(255) not null,
 admin_amount varchar(255) not null,
 status varchar(255) not null,
 date datetime,
 settlement_date date,
 product_id int,
 buyer_id int,
 seller_id int,
 FOREIGN KEY (product_id) REFERENCES product(product_id),
 FOREIGN KEY (buyer_id) REFERENCES user(user_id),
 FOREIGN KEY (seller_id) REFERENCES user(user_id)
 );
 
 
 
 create table chat(
 chat_id  int auto_increment primary key,
 message varchar(255) not null,
 isSenderRead varchar(255) not null,
 isReceiverRead varchar(255) not null,
 date datetime not null,
 sender_id int,
 receiver_id int,
 FOREIGN KEY (sender_id) REFERENCES user(user_id),
 FOREIGN KEY (receiver_id) REFERENCES user(user_id)
 );
