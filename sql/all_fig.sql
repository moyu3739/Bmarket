-- Active: 1682823504090@@localhost@3306@bmarket
create view all_fig as
(select * from fig)
UNION ALL
(select * from peri where name like '%手办%');
