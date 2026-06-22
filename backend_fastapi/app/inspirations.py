"""
HabitFlow 内容推荐系统
按目标类型分类的精选内容库，包含名人名言、学习方法、好词好句、技巧建议等
"""

import random

INSPIRATIONS = {
    "英语": [
        {"type": "quote", "content": "\"The only limit to our realization of tomorrow is our doubts of today.\" — Franklin D. Roosevelt",
         "cn": "实现明天理想的唯一障碍是今天的疑虑。"},
        {"type": "quote", "content": "\"Success is not final, failure is not fatal: it is the courage to continue that counts.\" — Winston Churchill",
         "cn": "成功不是终点，失败也非末日，最重要的是继续前进的勇气。"},
        {"type": "quote", "content": "\"The beautiful thing about learning is that nobody can take it away from you.\" — B.B. King",
         "cn": "学习的美妙之处在于没有人能把它从你身边夺走。"},
        {"type": "quote", "content": "\"Language is the road map of a culture. It tells you where its people come from and where they are going.\" — Rita Mae Brown",
         "cn": "语言是文化的地图，它告诉你人们来自哪里，将去往何方。"},
        {"type": "quote", "content": "\"To have another language is to possess a second soul.\" — Charlemagne",
         "cn": "掌握另一门语言，等于拥有了第二个灵魂。"},
        {"type": "quote", "content": "\"Learning is a treasure that will follow its owner everywhere.\" — Chinese Proverb",
         "cn": "学习是随身携带的宝藏。"},
        {"type": "word", "content": "今日词汇：perseverance /ˌpɜːrsəˈvɪrəns/ n. 毅力，坚持",
         "example": "Learning a language takes patience and perseverance."},
        {"type": "word", "content": "今日词汇：resilience /rɪˈzɪliəns/ n. 韧性，恢复力",
         "example": "She showed great resilience in overcoming difficulties."},
        {"type": "word", "content": "今日词组：step out of one's comfort zone 走出舒适区",
         "example": "To improve your English, you need to step out of your comfort zone."},
        {"type": "word", "content": "今日词组：break the ice 打破沉默/破冰",
         "example": "The game helped everyone break the ice at the party."},
        {"type": "sentence", "content": "今日高频句型：It occurred to me that...（我突然想到……）",
         "example": "It occurred to me that I had left the book at home."},
        {"type": "sentence", "content": "今日高频句型：It's no use doing...（做……是没有用的）",
         "example": "It's no use worrying about the exam without studying."},
        {"type": "sentence", "content": "今日高频句型：The more..., the more...（越……就越……）",
         "example": "The more you practice, the better your English will become."},
        {"type": "sentence", "content": "今日高频句型：There's no denying that...（不可否认的是……）",
         "example": "There's no denying that English is important for your career."},
        {"type": "tip", "content": "英语学习方法：每天用英语写3句话总结当天发生的事情，坚持一个月，写作能力会明显提升。"},
        {"type": "tip", "content": "英语听力技巧：先听一遍不看字幕，再听一遍看英文字幕，最后看中文字幕对照。每天坚持15分钟。"},
        {"type": "tip", "content": "英语口语秘诀：自言自语法——每天挑一个话题（如介绍你的房间），用英语说3分钟，录下来自己听。"},
        {"type": "tip", "content": "背单词技巧：不要单独背单词，要背短语和句子。把单词放在语境中记忆，效率提高3倍。"},
        {"type": "tip", "content": "英语阅读建议：选择比你当前水平略高一点的英文文章，先读大意，再查生词，最后精读。"},
        {"type": "tip", "content": "看美剧学英语：第一遍看剧情，第二遍看英文字幕，第三遍模仿跟读。推荐《老友记》《生活大爆炸》。"},
        {"type": "tip", "content": "英语学习APP推荐：每日英语听力（听力训练）、多邻国（闯关式学习）、Grammarly（写作纠错）。"},
        {"type": "tip", "content": "英语语法小技巧：学语法不如用语法。多读多写自然就能掌握语感，不用死记硬背规则。"},
        {"type": "tip", "content": "晨读建议：每天早上朗读英语15分钟，注意语音语调，坚持21天会有质的飞跃。"},
        {"type": "tip", "content": "英语学习资源推荐：BBC Learning English（免费）、VOA慢速英语、TED演讲（英文字幕）。"},
    ],
    "运动": [
        {"type": "quote", "content": "\"Take care of your body. It's the only place you have to live.\" — Jim Rohn",
         "cn": "照顾好你的身体，这是你唯一要居住的地方。"},
        {"type": "quote", "content": "\"The pain you feel today will be the strength you feel tomorrow.\" — Arnold Schwarzenegger",
         "cn": "今天感受到的酸痛，明天会成为你的力量。"},
        {"type": "quote", "content": "\"Exercise is a celebration of what your body can do, not a punishment for what you ate.\" — Unknown",
         "cn": "运动是庆祝你身体的能力，不是对你吃的东西的惩罚。"},
        {"type": "quote", "content": "\"A one-hour workout is 4% of your day. No excuses.\" — Unknown",
         "cn": "一小时的锻炼只占你一天的4%，没有借口。"},
        {"type": "quote", "content": "\"The best project you'll ever work on is you.\" — Unknown",
         "cn": "你一生最好的项目，就是投资你自己。"},
        {"type": "quote", "content": "\"Don't count the days, make the days count.\" — Mike Tyson",
         "cn": "不要数日子，让每一天都有意义。"},
        {"type": "tip", "content": "运动后记得做5-10分钟的拉伸，可以减少肌肉酸痛，帮助身体恢复。"},
        {"type": "tip", "content": "健身小知识：每组动作之间休息30-60秒效果最佳，过长会影响训练效率。"},
        {"type": "tip", "content": "跑步建议：采用“跑一休一”的方式，给身体足够的恢复时间，反而进步更快。"},
        {"type": "tip", "content": "早晨锻炼比晚上锻炼更能提高全天的新陈代谢率，试试早起运动30分钟。"},
        {"type": "tip", "content": "运动补水技巧：运动前喝200ml水，运动中每15分钟喝100ml，运动后称体重，每减轻0.5kg补充500ml水。"},
        {"type": "tip", "content": "力量训练入门：从自重训练开始——俯卧撑、深蹲、平板支撑，每个动作3组，每组8-12次。"},
        {"type": "tip", "content": "有氧运动推荐：快走（每天30分钟）、跳绳（10分钟=跑步30分钟）、游泳（全身运动）。"},
        {"type": "tip", "content": "运动时听音乐的节奏建议：热身期120-140BPM，训练期140-160BPM，整理期100-120BPM。"},
        {"type": "tip", "content": "如果你想减脂，力量训练+有氧运动的组合效果是最好的。先力量30分钟，再有氧20分钟。"},
    ],
    "阅读": [
        {"type": "quote", "content": "\"A reader lives a thousand lives before he dies. The man who never reads lives only one.\" — George R.R. Martin",
         "cn": "读书的人在死前活过一千次。从不读书的人只活了一次。"},
        {"type": "quote", "content": "\"Books are a uniquely portable magic.\" — Stephen King",
         "cn": "书籍是一种独一无二的可随身携带的魔法。"},
        {"type": "quote", "content": "\"The more that you read, the more things you will know. The more that you learn, the more places you'll go.\" — Dr. Seuss",
         "cn": "你读得越多，知道得就越多；你学得越多，能去的地方就越多。"},
        {"type": "quote", "content": "\"Reading is to the mind what exercise is to the body.\" — Joseph Addison",
         "cn": "阅读之于心灵，犹如运动之于身体。"},
        {"type": "quote", "content": "\"A room without books is like a body without a soul.\" — Cicero",
         "cn": "没有书的房间，如同没有灵魂的躯体。"},
        {"type": "quote", "content": "\"I have never known any distress that an hour's reading did not relieve.\" — Montesquieu",
         "cn": "我从未遇到过一小时的阅读无法缓解的痛苦。"},
        {"type": "tip", "content": "阅读技巧：试试番茄阅读法——专注阅读25分钟，休息5分钟，每4个循环休息15分钟。"},
        {"type": "tip", "content": "如何选书：先看豆瓣评分（7.5分以上），再看目录和前言，最后试读前20页。"},
        {"type": "tip", "content": "读书笔记方法：康奈尔笔记法——左栏记关键词，右栏记要点，底部写总结。"},
        {"type": "tip", "content": "速读技巧：不要逐字阅读，要以意群为单位扫读，用笔或手指引导视线，速度可以提升50%。"},
        {"type": "tip", "content": "阅读后复习：读完一本书后，第二天用自己的话复述一遍核心内容，记忆留存率从30%提升到80%。"},
        {"type": "tip", "content": "推荐阅读顺序：先读经典（经过了时间考验），再读畅销书，最后读专业书籍。"},
        {"type": "tip", "content": "电子书 vs 纸质书：电子书适合碎片时间阅读，纸质书适合深度阅读。建议两者结合使用。"},
        {"type": "tip", "content": "每周读一本书的秘诀：每天早起读30分钟+午休读20分钟+睡前读30分钟=80分钟，一周560分钟≈一本书。"},
    ],
    "学习": [
        {"type": "quote", "content": "\"The mind is not a vessel to be filled, but a fire to be kindled.\" — Plutarch",
         "cn": "大脑不是等待被填满的容器，而是需要被点燃的火把。"},
        {"type": "quote", "content": "\"Education is not the learning of facts, but the training of the mind to think.\" — Albert Einstein",
         "cn": "教育不是学习事实，而是训练思维去思考。"},
        {"type": "quote", "content": "\"Live as if you were to die tomorrow. Learn as if you were to live forever.\" — Mahatma Gandhi",
         "cn": "像明天就要死去一样地活着，像永远不死一样地学习。"},
        {"type": "quote", "content": "\"In learning you will teach, and in teaching you will learn.\" — Phil Collins",
         "cn": "在学习中你会教，在教的过程中你又会学。"},
        {"type": "quote", "content": "\"Study hard what interests you the most in the most undisciplined, irreverent and original manner possible.\" — Richard Feynman",
         "cn": "以最不守规矩、最不敬、最原创的方式，去努力学习你最感兴趣的东西。"},
        {"type": "tip", "content": "学习方法：费曼技巧——尝试用最简单的话把学到的知识讲给一个完全不懂的人听。"},
        {"type": "tip", "content": "记忆技巧：学完新知识后，在1小时、1天、1周、1个月后分别复习，记忆效果最好（艾宾浩斯遗忘曲线）。"},
        {"type": "tip", "content": "专注力训练：使用番茄工作法——25分钟专注学习+5分钟休息，每4个循环休息15-30分钟。"},
        {"type": "tip", "content": "学习环境优化：保持桌面整洁，手机放在视线之外，背景白噪音（如雨声、咖啡馆声）有助于专注。"},
        {"type": "tip", "content": "高效笔记法：不要逐字记录。用思维导图或关键词记录，课后立即整理笔记，理解比记录更重要。"},
        {"type": "tip", "content": "主动回忆法：看完一页书后，合上书本在脑中复述一遍。这比反复阅读有效得多。"},
        {"type": "tip", "content": "学习时间分配：成年人一次深度专注的极限是90分钟，超过后效率急剧下降，记得多休息。"},
        {"type": "tip", "content": "交叉学习法：不要长时间学习同一科目，每1小时切换一次学习内容，大脑保持新鲜感。"},
        {"type": "tip", "content": "睡前学习法：睡前学习的内容，大脑会在睡眠中自动整理和巩固。睡前30分钟是学习的黄金时间。"},
        {"type": "tip", "content": "目标拆解法：把大目标拆成每天可执行的小任务。比如“学好Python”→“今天学完函数这一章”。"},
        {"type": "tip", "content": "考试复习策略：先复习自己不熟悉的内容，再做模拟题，最后复习自己擅长的部分。不要从头到尾平均用力。"},
    ],
    "健身": [
        {"type": "quote", "content": "\"Strength does not come from the body. It comes from the will.\" — Unknown",
         "cn": "力量来自意志，而非身体。"},
        {"type": "quote", "content": "\"The hardest lift of all is lifting your butt off the couch.\" — Unknown",
         "cn": "最难的举重，是把你的屁股从沙发上举起来。"},
        {"type": "tip", "content": "新手健身建议：先掌握动作标准，再追求重量。动作不对，练了反而伤身。"},
        {"type": "tip", "content": "饮食建议：健身三分练七分吃。增肌期适当增加蛋白质摄入，减脂期控制总热量但不要过度节食。"},
    ],
    "早睡": [
        {"type": "quote", "content": "\"Early to bed and early to rise makes a man healthy, wealthy and wise.\" — Benjamin Franklin",
         "cn": "早睡早起使人健康、富有且智慧。"},
        {"type": "tip", "content": "早睡技巧：睡前一小时放下手机，手机蓝光会抑制褪黑素分泌，影响睡眠质量。"},
        {"type": "tip", "content": "睡眠建议：每天固定时间睡觉和起床，包括周末。规律的生物钟比睡眠时长更重要。"},
        {"type": "tip", "content": "助眠方法：睡前喝一杯温牛奶、听白噪音或ASMR、做5分钟深呼吸。"},
        {"type": "tip", "content": "卧室环境：保持黑暗、安静、凉爽（18-22℃），这些条件最有利于深度睡眠。"},
        {"type": "tip", "content": "如果你晚上难以入睡，试试“4-7-8呼吸法”：吸气4秒→屏息7秒→呼气8秒，重复4次。"},
    ],
    "default": [
        {"type": "tip", "content": "坚持本身就是一种天赋。今天的每一分努力，都在为未来的自己铺路。"},
        {"type": "quote", "content": "\"The secret of getting ahead is getting started.\" — Mark Twain",
         "cn": "领先的秘诀就是开始行动。"},
        {"type": "tip", "content": "每完成一个目标，给自己一个小奖励，这会让大脑形成正向反馈循环。"},
        {"type": "quote", "content": "\"It does not matter how slowly you go as long as you do not stop.\" — Confucius",
         "cn": "不怕慢，就怕站。"},
        {"type": "tip", "content": "如果你想放弃，告诉自己：先做5分钟，5分钟后不想继续再放弃。大多数情况下你会继续做下去。"},
        {"type": "quote", "content": "\"The best time to plant a tree was 20 years ago. The second best time is now.\" — Chinese Proverb",
         "cn": "种一棵树最好的时间是十年前，其次是现在。"},
        {"type": "tip", "content": "习惯养成的关键是：降低门槛。想每天运动？先从“换上运动服”开始。"},
        {"type": "quote", "content": "\"We are what we repeatedly do. Excellence, then, is not an act, but a habit.\" — Aristotle",
         "cn": "我们重复做的事情塑造了我们。优秀不是一种行为，而是一种习惯。"},
        {"type": "tip", "content": "当打卡变成肌肉记忆，自律就不再需要意志力了。前21天最难，熬过去就好了。"},
        {"type": "tip", "content": "如果你今天错过了打卡，不要自责，明天补上就好。完美的坚持不存在，长期的坚持才是目标。"},
        {"type": "tip", "content": "自律不是自我惩罚，而是对自己未来的投资。你现在的每一次打卡，都是给未来的自己送礼物。"},
    ],
}


def get_inspiration(goal_type: str) -> dict:
    """根据目标类型随机返回一条精选内容"""
    items = INSPIRATIONS.get(goal_type, INSPIRATIONS["default"])
    item = random.choice(items)
    return {
        "goalType": goal_type,
        "content": item["content"],
        "type": item.get("type", "tip"),
        "cn": item.get("cn", ""),
        "example": item.get("example", ""),
    }


def get_peer_tips(db, goal_type: str, limit: int = 3) -> list:
    """获取同类型目标中，打卡备注写得比较认真的前N条"""
    from .models import CheckIn, Goal
    rows = (
        db.query(CheckIn.remark, Goal.name)
        .join(Goal, CheckIn.goal_id == Goal.id)
        .filter(Goal.type == goal_type, CheckIn.remark.isnot(None), CheckIn.remark != "")
        .order_by(CheckIn.id.desc())
        .limit(limit)
        .all()
    )
    return [{"remark": r[0], "goalName": r[1]} for r in rows if r[0] and len(r[0]) > 5]
