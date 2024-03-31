-- Active: 1682823504090@@localhost@3306@bmarket
create view miku as
select * from all_fig where
name like '%初音未来%' and
not name like '%景品%' and
not name like '%初音未来%MTV%' and
not name like '%棕色相框%' and
not name like '%科技魔法%' and
not name like '%新东京和服%' and
not name like '%FUTURE EVE%' and
not name like '%GSC 初音未来 V3 Q版手办%' and
not name like '%回首美人图%' and
not name like '%小红帽%' and
not name like '%Max Factory 初音未来 手办%' and
not name like '%Art by lack%' and
not name like '%S-FIRE 初音未来 Q版手办%' and
not name like '%Stronger%' and
not name like '%矢吹健太朗%' and
not name like '%擎苍%' and
not name like '%艺华境%' and
not name like '%招财未来%';
