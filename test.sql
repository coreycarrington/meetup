USE meetup;

INSERT INTO `member` (`username`, `password`, `firstname`, `lastname`, `zipcode`)
VALUES
    ('ben','81dc9bdb52d04dc20036dbd8313ed055','Ben','Miller',11418),
    ('clare','ea416ed0759d46a8de58f63a59077499','Clare','Smith',21248),
    ('david','81dc9bdb52d04dc20036dbd8313ed055','david','miller',12209),
    ('eve','ea416ed0759d46a8de58f63a59077499','Eve','Andorson',1234),
    ('john','81dc9bdb52d04dc20036dbd8313ed055','john','smith',1122),
    ('sophia','ea416ed0759d46a8de58f63a59077499','Sophia','Miller',12004),
    ('user','81dc9bdb52d04dc20036dbd8313ed055','First','Last',21247);

INSERT INTO `interest` (`interest_name`)
VALUES
    ('Chess'),
    ('Computer Games'),
    ('computers'),
    ('Cycling'),
    ('Food'),
    ('physics'),
    ('Snowboarding'),
    ('Swimming');

INSERT INTO `groups` (`group_id`, `group_name`, `description`, `username`)
VALUES
    (1,'Database','INtroduction to database undergraduate course at NYU','eve'),
    (2,'Geeks-NYC','group for geeks of NYC','sophia'),
    (3,'Photographer','Bend your mind with amazing world of photographers\n','eve'),
    (4,'Food Lovers','Food lovers around the world','ben');

INSERT INTO `location` (`lname`, `zipcode`, `street`, `city`, `description`, `latitude`, `longitude`)
VALUES
    ('Beach town ',10012,'Main St','NYC','Beach town ',41,-74),
    ('DallasBBQ',10124,'261 8th Ave','NYC','Bustling local chain serving big plates of saucy meats & other classic fare plus jumbo margaritas.\r\n',41,-74),
    ('Joes Diner',10002,'Hawthorn St','NYC','Joes Diner',41,-74),
    ('NYU CSE Department',12201,'Jay St','Brooklyn','NYU Computer Science Department',43,-89),
    ('SAP Center',11489,'Hacker Way','San Jose','SAP Center, San Jose, CA',33,-50);

INSERT INTO `events` (`event_id`, `title`, `description`, `start_time`, `end_time`, `group_id`, `lname`, `zipcode`)
VALUES
    (1,'Holiday Pary','Group created on this day','2015-12-16 00:00:00','2015-12-16 00:00:00',1,'Beach town',10012),
    (2,'First Meet','Fisrt Meet of our group','2015-10-11 00:00:00','2015-10-12 00:00:00',3,'DallasBBQ',10124),
    (3,'Let\'s Meet','let\'s meet and talk','2016-01-14 00:00:00','2016-01-14 00:00:00',2,'Joes Diner',10002),
    (4,'Group Picnic','Group picnic','2015-12-15 00:00:00','2015-12-15 10:00:00',3,'Joes Diner',10002);

INSERT INTO `about` (`interest_name`, `group_id`)
VALUES
    ('Computer Games',1),
    ('Computer Games',2),
    ('computers',1),
    ('computers',3),
    ('Cycling',3),
    ('physics',3),
    ('Snowboarding',2);

INSERT INTO `interested_in` (`username`, `interest_name`)
VALUES
    ('eve','Chess'),
    ('david','computers'),
    ('sophia','computers'),
    ('ben','physics'),
    ('ben','Swimming');

INSERT INTO `attend` (`event_id`, `username`, `rsvp`, `rating`)
VALUES
    (1,'ben',1,0),
    (1,'eve',1,0),
    (2,'eve',1,3),
    (2,'sophia',0,0),
    (3,'ben',0,0),
    (3,'sophia',1,2);

INSERT INTO `belongs_to` (`group_id`, `username`, `authorized`)
VALUES
    (1,'ben',1),
    (1,'eve',0),
    (1,'sophia',0),
    (2,'ben',1),
    (2,'eve',0),
    (3,'eve',1),
    (3,'john',1);

