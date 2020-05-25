import sqlalchemy as sa
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from everyclass.server.utils.db.postgres import Base, db_session


class CourseMeta(Base):
    __tablename__ = 'course_meta'

    course_id = Column(String(30), primary_key=True)  # 课程ID
    name = Column(String)  # 课程名称
    description = Column(String, nullable=True)  # 课程简介
    main_category = Column(String, nullable=False)  # 课程类型
    unit = Column(String, nullable=True)  # 开课单位

    classes = relationship("KlassMeta", back_populates="course")

    __table_args__ = (sa.Index('idx_main_category', 'main_category'),
                      )

    @classmethod
    def get_categories(cls):
        """获得所有类别和对应的课程ID"""
        from .klass import KlassMeta

        results = db_session.query(KlassMeta).all()

        categories = {}

        for klass in results:
            if klass.course.main_category not in categories:
                categories[klass.course.main_category] = [klass]
            else:
                categories[klass.course.main_category].append(klass)

        for _, classes in categories.items():
            classes.sort(key=lambda x: x.score, reverse=True)

        return {'categories': [{'name': k, 'classes': v[:3]} for k, v in categories.items()],
                'total_classes': len(results)}  # 每个类别只取前3门评分最高的课程

    @classmethod
    def import_demo_content(cls):
        data = {'创新与创业': """1-10	创业概论	普通课	公共管理学院(教学)
1-12	创业基础（创业学）	普通课	商学院(教学)
1-01	创新型大学生的培养	普通课	化学化工学院(教学)
1-02	传统文化与管理智慧	普通课	商学院(教学)
1-06	大学科研创意原理与方法	普通课	法学院(教学)
1-13	人力资源管理	普通课	商学院(教学)
1-14	公司战略管理	普通课	商学院(教学)
1-15	建设项目管理基础	普通课	土木工程学院(教学)
1-16	孙子兵法与现代管理	普通课	公共管理学院(教学)
1-17	现代管理基础	普通课	交通运输工程学院(教学)
1-18	博弈论解说	普通课	商学院(教学)
1-19	税收筹划实务	普通课	商学院(教学)
1-20	创新创业管理的素质与技能	普通课	商学院(教学)
1-21	运输市场营销学	普通课	交通运输工程学院(教学)
1-22	创业基础（创新创业与专利法）	普通课	法学院(教学)
1-23	创业基础（创办你的企业）	普通课	本科生院(行政)
1-24	创业基础（大学生创业实训课）	普通课	本科生院(行政)
1-29	中国文化视域下的组织与人力管理	普通课	商学院(教学)
1-60	企业管理	普通课	商学院(教学)
1-61	项目管理	普通课	商学院(教学)
1-62	领导科学与领导力	普通课	公共管理学院(教学)
1-64	管理素质与能力的五项修炼-跟我学管理	普通课	商学院(教学)
1-65	战略推演：企业致胜七步法	普通课	商学院(教学)
2-04	西方创造学	普通课	公共管理学院(教学)
5-04	互联网创新思维与品牌设计	普通课	建筑与艺术学院(教学)
2-12	管理心理学	普通课	公共管理学院(教学)
5-01	“互联网+”背景下的创新理论与实践	普通课	计算机学院（教学）
2-30	创造学	普通课	公共管理学院(教学)""",
                "经济": """1-03	西方经济学概论	普通课	商学院(教学)
1-04	宏观经济学	普通课	商学院(教学)
1-05	微观经济学	普通课	商学院(教学)
1-07	基础会计学	普通课	商学院(教学)
1-09	金融学	普通课	商学院(教学)
1-11	经贸谈判	普通课	商学院(教学)
1-28	用经济学智慧解读中国	普通课	本科生院(行政)
1-63	经济法	普通课	法学院(教学)""",
                "政治与政务": """1-08	电子政务与政府管理创新	普通课	公共管理学院(教学)
2-02	思想的奥秘与思想工作的艺术	普通课	马克思主义学院(教学)
2-120	公共政策学	普通课	公共管理学院(教学)
2-121	公共关系学	普通课	公共管理学院(教学)
4-67	卫生事业管理	普通课	公共卫生学院院办公室
2-73	入党基本知识	普通课	党校
2-41	当代世界经济与政治热点	普通课	马克思主义学院(教学)
4-31	公共安全管理概论	普通课	资源与安全工程学院(教学)""",
                "法律": """2-62	生活中的法律常识	普通课	法学院(教学)
2-64	影视中的法律世界	普通课	法学院(教学)
2-74	国际经济法	普通课	法学院(教学)
2-76	知识产权审判实务	普通课	法学院(教学)
2-122	知识产权法	普通课	法学院(教学)
2-125	经济法	普通课	法学院(教学)
2-60	生物医药知识产权	普通课	生命科学学院""",
                "职业生涯规划": """1-25	职业生涯规划实训	普通课	学工部
1-26	职业生涯规划与求职就业指导	普通课	学工部
1-27	大学生职业选择能力训练	普通课	学工部""",
                "人际与心理": """2-05	大学心理学	普通课	公共管理学院(教学)
2-07	社会心理学	普通课	公共管理学院(教学)
2-10	健康心理学	普通课	公共管理学院(教学)
2-13	心理学与生活	普通课	学工部
2-23	朋辈心理辅导基础	普通课	学工部
2-26	影响力心理学	普通课	公共管理学院(教学)
2-43	心理学	普通课	马克思主义学院(教学)
4-63	情商（EQ）与人生成就	普通课	公共卫生学院院办公室
2-124	人际传播与沟通	普通课	文学院(教学)
2-20	现代礼仪	普通课	公共管理学院(教学)
2-21	管理沟通艺术与技巧	普通课	公共管理学院(教学)
2-24	潜意识分析与人际交往艺术	普通课	公共管理学院(教学)""",
                "中国传统文化": """2-42	中国传统文化	普通课	马克思主义学院(教学)
2-06	儒家文化	普通课	公共管理学院(教学)
2-08	中国传统文化经典导读	普通课	马克思主义学院(教学)
h2-01	中国民俗文化	普通课	本科生院(行政)
h3-01	戏剧台词鉴赏	普通课	本科生院(行政)
2-82	《周易》（双语）	普通课	外国语学院(教学)
2-83	《周易》与人生	普通课	公共管理学院(教学)
2-86	道家思想与心理保健	普通课	公共管理学院(教学)
2-91	漫谈大学文化	普通课	自动化学院(教学)
2-92	发现唐诗宋词	普通课	文学院(教学)
2-93	中华诗词之美	普通课	本科生院(行政)
2-94	创新中国	普通课	本科生院(行政)
2-95	走近中华优秀传统文化	普通课	本科生院(行政)
2-96	中国文学经典与中国精神	普通课	文学院(教学)
2-25	国学精粹	普通课	公共管理学院(教学)""",
                "自然与社会": """2-03	人类社会与生态环境	普通课	公共管理学院(教学)
2-27	社会性别与婚姻家庭	普通课	公共管理学院(教学)
2-22	伦理学	普通课	公共管理学院(教学)
2-18	公共关系学	普通课	公共管理学院(教学)
2-80	生命伦理学	普通课	公共管理学院(教学)
2-81	女性与发展	普通课	马克思主义学院(教学)
2-89	当代中国经济变迁与社会转型	普通课	公共管理学院(教学)""",
                "军事与体育": """12-5	形体训练	普通课	土木工程学院(教学)
2-01	大学生健康教育	普通课	职工医院
2-09	现代武器装备及运用	普通课	学工部
2-100	革命军人思想品德修养	普通课	学工部
2-101	军人心理学	普通课	学工部
2-102	国家安全环境及国防和军队建设	普通课	学工部
2-103	人民军队导论	普通课	学工部
2-104-1	军事体育（一）	普通课	学工部
2-104-2	军事体育（二）	普通课	学工部
2-104-3	军事体育（三）	普通课	学工部
2-104-4	军事体育（四）	普通课	学工部
2-104-5	军事体育（五）	普通课	学工部
2-104-6	军事体育（六）	普通课	学工部
2-104-7	军事体育测试	普通课	学工部
2-105	军事思想	普通课	学工部
2-106	军事领导科学与方法	普通课	学工部
3-05	足球	普通课	体育教研部
3-06	篮球	普通课	体育教研部
3-07	排球	普通课	体育教研部
3-08	乒乓球	普通课	体育教研部
3-09	合唱艺术	普通课	校团委
3-10	羽毛球	普通课	体育教研部
3-11	体育舞蹈概论	普通课	体育教研部
3-12	体育舞蹈实践	普通课	体育教研部
3-16	奥林匹克文化	普通课	体育教研部
3-04	身心瑜伽	普通课	体育教研部
3-22	体育美学	普通课	体育教研部
3-23	体育欣赏	普通课	体育教研部
3-24	体育旅游文化	普通课	体育教研部
3-45	花样跳绳	普通课	体育教研部
3-38	户外自行车	普通课	体育教研部""",
                "文学与外语": """2-47	英美诗选	普通课	外国语学院(教学)
2-48	英汉语言对比与对外汉语教学	普通课	外国语学院(教学)
2-49	英美文学欣赏	普通课	外国语学院(教学)
2-50	英汉翻译技巧	普通课	外国语学院(教学)
2-51	生物医学论文英文编辑与写作初步	普通课	外国语学院(教学)
2-52	中西文化对比	普通课	外国语学院(教学)
2-53	西班牙语入门	普通课	外国语学院(教学)
2-54	实用英语写作	普通课	外国语学院(教学)
2-55	医学英语学术写作	普通课	外国语学院(教学)
2-56	英文电影欣赏与翻译	普通课	外国语学院(教学)
2-57	商务英语交流	普通课	外国语学院(教学)
2-58	实用新闻英语	普通课	外国语学院(教学)
2-59	新闻英语	普通课	外国语学院(教学)
2-69	高级英语视、听、说	普通课	外国语学院(教学)
2-70	翻译理论与实践	普通课	外国语学院(教学)
2-71	英语写作进阶	普通课	外国语学院(教学)
2-79	《圣经》文学选读	普通课	外国语学院(教学)
2-77	日语入门	普通课	外国语学院(教学)
2-78	法语入门	普通课	外国语学院(教学)
2-34	新闻学八讲	普通课	文学院(教学)
2-35	传媒通论	普通课	文学院(教学)
2-36	中国现代文学八讲	普通课	文学院(教学)
2-37	经典鉴赏与文艺思潮	普通课	文学院(教学)
2-38	汉字与文化学	普通课	文学院(教学)
2-29	大学语文	普通课	文学院(教学)
2-40	学术英语	普通课	外国语学院(教学)
2-39	优秀电视节目赏析	普通课	文学院(教学)
2-123	文学与创意	普通课	文学院(教学)""",
                "思维与哲学": """2-14	思维与论辩	普通课	公共管理学院(教学)
2-15	西方哲学与趣味人生	普通课	公共管理学院(教学)
2-16	哲学思想与人文关怀	普通课	公共管理学院(教学)
2-17	中西大学理念与大学生活	普通课	公共管理学院(教学)
2-19	趣味哲学	普通课	公共管理学院(教学)""",
                "音乐与艺术": """3-01	管弦乐演奏实践	普通课	校团委
3-02	舞蹈艺术	普通课	校团委
3-03	设计思维	普通课	建筑与艺术学院(教学)
3-13	表演艺术	普通课	校团委
3-26	应用美学	普通课	文学院(教学)
3-27	音乐欣赏	普通课	自动化学院(教学)
3-28	美术欣赏	普通课	建筑与艺术学院(教学)
3-29	大学生音乐修养	普通课	建筑与艺术学院(教学)
3-30	舞蹈艺术欣赏	普通课	建筑与艺术学院(教学)
3-31	毛笔书法	普通课	建筑与艺术学院(教学)
3-33	通俗音乐赏析与创作	普通课	建筑与艺术学院(教学)
3-35	走进世界艺术博物馆------艾尔米塔什	普通课	外国语学院(教学)
3-36	电影音乐赏析	普通课	建筑与艺术学院(教学)
3-37	瑶族长鼓舞欣赏	普通课	校团委
3-39	诗词格律与写作	普通课	建筑与艺术学院(教学)
3-40	经典音乐欣赏	普通课	建筑与艺术学院(教学)
3-41	数码摄影	普通课	建筑与艺术学院(教学)
3-42	艺术导论	普通课	本科生院(行政)
3-43	水彩画赏析与体验	普通课	建筑与艺术学院(教学)
3-44	白描花鸟画赏析与临摹	普通课	建筑与艺术学院(教学
2-31	写作	普通课	文学院(教学)""",
                "医学与健康": """5-05	生理学问题探究	普通课	基础医学院教务办
4-80	临床科研实验技能	其他	湘雅三医院教学部
4-81	疫战到底--瘟疫的历史和控制	普通课	公共卫生学院院办公室
4-82	饮食与健康	普通课	药学院(教学)
4-33	生命与健康	普通课	生命科学学院
4-24	现代生物技术概论	普通课	资源加工与生物工程学院(教学)
4-25	生命科学导论	普通课	资源加工与生物工程学院(教学)
4-26	分子生物学实验技术	普通课	生命科学学院
4-46	食品营养与健康	普通课	化学化工学院(教学)
4-47	生活方式与常见疾病预防	普通课	公共卫生学院院办公室
4-39	运动、营养与游龙拳的实践	普通课	公共卫生学院院办公室
4-40	饮食、文化与健康	普通课	公共卫生学院院办公室
4-41	医学大数据与虚拟生理人	普通课	公共卫生学院院办公室
4-42	食之有道：饮食的科学与智慧	普通课	公共卫生学院院办公室
4-43	食物、营养、身体活动和癌症预防	普通课	公共卫生学院院办公室
4-44	营养365，安全面面观	普通课	公共卫生学院院办公室
4-34	医学遗传学讲座	普通课	生命科学学院
4-17	生物技术与生命	普通课	化学化工学院(教学)
4-07	药与健康	普通课	化学化工学院(教学)
4-79	生物医药创新创业技术推广示范	其他	人体解剖学与神经生物学系
4-83	生物与安全	普通课	基础医学院教务办
5-03	基础医学创新思维与训练	普通课	基础医学院教务办
4-68	现代膳食与人体健康	普通课	公共卫生学院院办公室
4-74	食物营养与食品安全	普通课	公共卫生学院院办公室
4-48	重金属污染、防治与健康	普通课	冶金与环境学院公共教学中心
4-71	矿物质与人体健康	普通课	冶金与环境学院公共教学中心
4-51	生活中的毒理学	普通课	公共卫生学院院办公室
4-59	《爱丽丝漫游仙境》与重金属中毒	普通课	公共卫生学院院办公室
4-66	食品安全与人体健康	普通课	公共卫生学院院办公室
4-55	现代生物技术与人类生活	普通课	本科生院(行政)
4-56	全球卫生简介	普通课	公共卫生学院院办公室
4-57	全球卫生简介：他山之“识”	普通课	公共卫生学院院办公室
4-58	病原生物与人类健康	普通课	基础医学院教务办
4-60	出入境检验检疫	普通课	公共卫生学院院办公室
4-61	环境污染与人类疾病	普通课	公共卫生学院院办公室
4-62	环境与健康	普通课	公共卫生学院院办公室
4-64	日常化学物与人体健康	普通课	公共卫生学院院办公室
4-65	社会文化与健康	普通课	公共卫生学院院办公室
4-53	职业与健康	普通课	公共卫生学院院办公室
2-33	临床心灵关怀	普通课	湘雅医学院(教学)
2-87	事故急救与安全教育	普通课	护理学院教学办
2-90	向生而死：关于生和死	普通课	湘雅护理学院""",
                "科学与工程技术": """2-88	世界之谜	普通课	本科生院(行政)
2-11	科学通史	普通课	公共管理学院(教学)
4-01	材料与人类文明	普通课	材料科学与工程学院(教学)
4-02	氢能源与未来生活	普通课	冶金与环境学院公共教学中心
4-03	有色金属世界	普通课	材料科学与工程学院(教学)
4-04	新能源概论	普通课	化学化工学院(教学)
4-05	感恩教育与生态环境	普通课	化学化工学院(教学)
4-06	化学史	普通课	化学化工学院(教学)
4-08	名侦探柯南与化学探秘	普通课	化学化工学院(教学)
4-09	科学计算与虚拟现实	普通课	冶金与环境学院公共教学中心
4-10	资源循环工程学	普通课	冶金与环境学院公共教学中心
4-11	储能技术与电动汽车	普通课	冶金与环境学院公共教学中心
4-12	金属与人类文明	普通课	冶金与环境学院公共教学中心
4-13	环境保护与可持续发展	普通课	冶金与环境学院公共教学中心
4-14	计算机图形学	普通课	交通运输工程学院(教学)
4-15	计算机辅助应用技术基础	普通课	交通运输工程学院(教学)
4-16	高速列车概论	普通课	交通运输工程学院(教学)
4-18	能源革命与环境保护	普通课	能源科学与工程学院(教学)
4-19	数学建模方法引论	普通课	数学与统计学院(教学)
4-20	电磁波与现代生活	普通课	航空航天学院(教学)
4-21	数学实验与建模	普通课	数学与统计学院(教学)
4-22	体验科学－大学物理演示实验	普通课	物理与电子学院(教学)
4-23	先进复合材料	普通课	航空航天学院(教学)
4-27	现代物流概论	普通课	交通运输工程学院(教学)
4-28	车辆工程导论	普通课	交通运输工程学院(教学)
4-29	科技信息检索	普通课	生命科学学院
4-30	资源评估学	普通课	资源与安全工程学院(教学)
4-36	热之密码	普通课	能源科学与工程学院(教学)
4-37	工程伦理	普通课	土木工程学院(教学)
4-38	塑性力学	普通课	土木工程学院(教学)
4-69	放射性测量与辐射防护基础	普通课	地球科学与信息物理学院(教学)
4-70	道路交通环境的安全、生态与美	普通课	资源与安全工程学院(教学)
4-72	医院信息管理	普通课	生命科学学院
4-73	观赏植物学	普通课	生命科学学院
4-75	物理与高新技术	普通课	物理与电子学院
4-76	透过卫星看地球	普通课	地球科学与信息物理学院(教学)
4-77	宝玉石鉴赏	普通课	地球科学与信息物理学院(教学)
4-78	消防安全	普通课	土木工程学院(教学)
4-32	水利水电工程概论	普通课	土木工程学院(教学)
4-35	地理信息系统概论	普通课	地球科学与信息物理学院(教学)
4-45	大学生安全文化	普通课	资源与安全工程学院(教学)
4-49	环境保护与生态文明	普通课	冶金与环境学院公共教学中心
4-50	环境污染与现代生活	普通课	冶金与环境学院公共教学中心
4-52	3D打印技术的基础与应用	普通课	冶金与环境学院公共教学中心
5-02	电子科技制作理论和实践	普通课	电子信息工程系""",
                "学术": """2-32	学术诚信与学术规范	普通课	生命科学学院"""}
        for category_name, lines in data.items():
            for line in lines.splitlines():
                print(line.split())
                splitted = line.split()
                unit = splitted[3]
                if '(' in unit:
                    unit = unit[:unit.index('(')]
                if '（' in unit:
                    unit = unit[:unit.index('（')]
                course = CourseMeta(course_id=splitted[0], name=splitted[1], main_category=category_name, unit=unit)
                db_session.add(course)
        db_session.commit()
