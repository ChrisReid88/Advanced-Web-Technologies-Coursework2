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
  PRIMARY KEY (`user_id`)
);

CREATE TABLE `followers` (
  `id_user` INTEGER NOT NULL REFERENCES `users`(user_id),
  `id_following` INTEGER NOT NULL REFERENCES `users`(`user_id`),
  PRIMARY KEY (id_user, id_following)
);
INSERT INTO `users` (`username`, `password`, `profile_picture`,`first_name`, `last_name`) VALUES ('chrisrd', '$2b$12$b8uFb3vOmHmjYtvHh.33u.cyWfv82s5zVUFUnoPiiJi/YHZX50ppW','prof.jpg','Chris', 'Reid');
INSERT INTO `users` (`username`, `password`, `profile_picture`,`first_name`, `last_name`) VALUES ('dvader', '$2b$12$b8uFb3vOmHmjYtvHh.33u.cyWfv82s5zVUFUnoPiiJi/YHZX50ppW','prof2.jpeg','Darth', 'Vader');
INSERT INTO `users` (`username`, `password`, `profile_picture`,`first_name`, `last_name`) VALUES ('batman', '$2b$12$b8uFb3vOmHmjYtvHh.33u.cyWfv82s5zVUFUnoPiiJi/YHZX50ppW','prof3.jpeg','Bat', 'Man');
