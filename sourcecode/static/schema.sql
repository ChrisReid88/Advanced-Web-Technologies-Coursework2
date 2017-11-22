DROP TABLE IF EXISTS `comments`;
DROP TABLE IF EXISTS `users`;
DROP TABLE IF EXISTS `followers`;

CREATE TABLE `comments` (
  `comment_id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  `user_id` INTEGER NOT NULL,
  `comment` TEXT NOT NULL,
  FOREIGN KEY(`user_id`) REFERENCES `users`(`user_id`)
  ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE `users` (
  `user_id` INTEGER NOT NULL,
  `username` TEXT NOT NULL,
  `password` TEXT NOT NULL,
  `profile_picture` TEXT,
  `first_name` TEXT,
  `last_name` TEXT,
  `bio` TEXT,
  PRIMARY KEY (`user_id`)
);

CREATE TABLE `followers` (
  `id_user` INTEGER NOT NULL REFERENCES `users`(user_id),
  `id_following` INTEGER NOT NULL REFERENCES `users`(`user_id`),
  PRIMARY KEY (id_user, id_following)
);
INSERT INTO `users` (`username`, `password`, `profile_picture`,`first_name`, `last_name`,`bio`) VALUES ('TheCapn', '$2b$12$b8uFb3vOmHmjYtvHh.33u.cyWfv82s5zVUFUnoPiiJi/YHZX50ppW','prof.jpg','Captain', 'Spaulding','What''s the matter, kid? Don''t ya like clowns? ');
INSERT INTO `users` (`username`, `password`, `profile_picture`,`first_name`, `last_name`,`bio`) VALUES ('DVader', '$2b$12$b8uFb3vOmHmjYtvHh.33u.cyWfv82s5zVUFUnoPiiJi/YHZX50ppW','prof2.jpeg','Darth', 'Vader','I find your blah blah disturbing');
INSERT INTO `users` (`username`, `password`, `profile_picture`,`first_name`, `last_name`,`bio`) VALUES ('Batman', '$2b$12$b8uFb3vOmHmjYtvHh.33u.cyWfv82s5zVUFUnoPiiJi/YHZX50ppW','prof3.jpeg','Bat', 'Man','I''m Batman');
INSERT INTO `users` (`username`, `password`, `profile_picture`,`first_name`, `last_name`,`bio`) VALUES ('FGump12', '$2b$12$b8uFb3vOmHmjYtvHh.33u.cyWfv82s5zVUFUnoPiiJi/YHZX50ppW','prof4.jpeg','Forest', 'Gump','Mama always said life was like a box of chocolates. You never know what you''re gonna get.
') ;
INSERT INTO `users` (`username`, `password`, `profile_picture`,`first_name`, `last_name`,`bio`) VALUES ('TheDude', '$2b$12$b8uFb3vOmHmjYtvHh.33u.cyWfv82s5zVUFUnoPiiJi/YHZX50ppW','prof5.jpeg','Geoffrey', 'Lebowski','Sometimes you eat the bear, and sometimes, well, he eats you.');
