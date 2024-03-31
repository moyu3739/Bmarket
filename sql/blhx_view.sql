-- Active: 1682823504090@@localhost@3306@bmarket
create view blhx as
select * from all_fig where
name like '%碧蓝航线%' and
not name like '%AniMester大漫匠 碧蓝航线 鳐%' and
not name like '%EMONTOYS 碧蓝航线 贝尔法斯特%' and
not name like '%FREEing B-style 碧蓝航线 树城%' and
not name like '%FREEing B-style 碧蓝航线 里诺%' and
not name like '%FREEing 碧蓝航线 曼彻斯特 白衣“恶魔”的狂欢夜%' and
not name like '%企业 誓约的星光%' and
not name like '%纯白的守护者%' and
not name like '%期待的便当时间%' and
not name like '%WANDERER 碧蓝航线 独角兽%' and
not name like '%鸣子小夏%' and
not name like '%永不落幕的茶会%';
