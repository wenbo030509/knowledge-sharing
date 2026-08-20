核心结论：把目标表格 39 个 sheet 的 E 列按“前 3 个非空单元格”做了原始提取，再把其中真正可学习的自然语言评分细则做了清洗归类。整体看，这批评分细则不是简单的“答案对错说明”，而是一套把任务目标、取证边界、输出格式、容错阈值和负例排除写死的 可执行评测规范。
一、任务与提取口径
任务：读取任务2中全部 sheet，逐个提取 E 列前 3 个非空内容；在此基础上，区分“原始非空项”和“有效评分细则”，再做归类分层，总结这些评分细则在评测设计中的作用。
提取口径：原始层面严格按“E 列前 3 个非空单元格”收集，所以会同时看到正文规则、模板占位符和判定标签；例如 [RUBRIC]、[extra_rubric]、def grade(**kwargs) -> dict:、以及个别 sheet 中的 不正确。这说明该表不是纯自然语言 rubric 汇编，而是把“评分说明 + 程序模板 + 中间标记”混在了一起。
总体观察：39 个 sheet 里，内容最完整、最适合学习的是两类：一类是 OCR/字幕抽取与视频问答类，它们把时间窗、画面对象、输出顺序、去重规则和错误排除写得非常细；另一类是体育赛事与计数读数类，它们把“接受答案形式”“顺序是否敏感”“容差范围”“干扰数字不算”写得非常明确。相对而言，部分检索/流程类 sheet 的前几项更多是代码骨架或占位符，说明这些 sheet 更偏 judge 模板而不是成型 rubric 文本。
二、归类分层
2.1 按规则结构分层
第一层是任务定义层，先把要识别的对象说清楚，例如识别哪一句字幕、哪个时间段、哪个比分、哪个国家、哪一个 segment。第二层是证据边界层，明确证据只能来自哪里，比如“只看底部 narrator 字幕”“只取某段时间窗”“只看大字 headword”“只统计全屏分类图段落”。第三层是输出约束层，要求答案按出现顺序、一行一个、去重、只输出整数、或必须给出起止时间。第四层是判分容错层，给出 accepted forms、大小写忽略、标点忽略、数值容差、部分分权重等规则。第五层是负例排除层，专门写明哪些看起来像答案但其实不能算，例如前后 topic 的字幕、干扰性的 overlay 数字、倒序比分、错误单位、与当前问题无关的画面元素。
2.2 按业务类型分层
第一组是OCR / 字幕抽取类，典型是 M015、M016，这类 rubric 最强调“时间窗 + 取字范围 + 去重 + 排除中英夹杂/解释文字”；第二组是视频分段 / 事件定位类，如 M046、部分监控与片段判断任务，核心是先定义 segment，再要求给出每段的数量与起止时间；第三组是体育视频读数 / 问答类，如 M034、M035、M053-M071，这类规则尤其重视记分板顺序、整数抽取、接受表达式和干扰数字排除；第四组是视觉识别 / 场景判断类，如 M029、M041-M051、M099、M101，常见写法是先限定场景，再判断目标实体、类别或结果是否命中；第五组是文献核验 / 检索流程类，如 M021 以及若干 Productivity / Search Retrieval sheet，这类内容更像“把 judge 逻辑脚手架写在表里”，强调字段、匹配模式和程序化评估接口。
三、可直接学习的写法
这批 rubric 有几个非常值得学。其一，不只说“识别字幕”，而是写成“在哪个时间窗、哪种字幕轨、包含哪个关键词、按什么顺序输出”；其二，不只说“回答比分”，而是把“谁在前谁在后、倒序算错、哪些相近数字是干扰项”一并写进去；其三，不只给标准答案，还说明容错方式，例如大小写忽略、标点忽略、相似度阈值、整数容差、部分分权重；其四，会主动写出排除项，避免模型抓到视觉上更显眼但语义上不属于答案的内容。
四、这些评分细则的作用
这些评分细则至少有五个作用。第一，把任务目标压实，避免一句模糊题目引出多种互相冲突的理解。第二，把证据路径限定住，告诉评测对象到底该看哪里、忽略哪里，减少“答得像对、但证据取错”的情况。第三，把输出格式标准化，让自动 judge 可以稳定比较。第四，把容错机制显式化，把“允许的合理偏差”和“必须判错的情况”分开。第五，把主观判断转成程序化判断，从而提升评测的一致性、复现性和后续可扩展性。
五、对后续工作的启发
以后如果要写数据质检或评测 rubric，不能只写“看是否答对”，而应该至少补齐这 5 个部件：任务对象、证据边界、输出格式、容错规则、排除项。如果能再往前走一步，把常见错误答案、顺序敏感性、单位敏感性、跨段混淆点也提前写进 rubric，评测稳定性会明显更高。
六、结论
这批评分细则的核心价值，不在于“写得长”，而在于它们把一个原本依赖人脑理解的开放题，逐步收缩成了一个可验证、可复现、可自动化的 judge 规范。对做质检、做 CoT 压缩后的结果验收、以及后续 agent 化评测设计，都很有参考意义。
七、具体评分标准示例
前面的分析偏方法论，这里补上更具体的评分标准示例，方便直接感受这些 rubric 是怎么写的。下面选了几类最有代表性的 sheet，分别展示其 E 列中的实际评分标准片段，并说明它们各自强调的判分重点。
1. M015_video_subtitle_ocr_english
示例记录：
1. Row 4：The single English sentence shown on screen between 0:52 and 0:54 of the video, transcribed verbatim to /workspace/output.txt (English only, no Chinese gloss). GT: 'Difficult roads often lead to beautiful destinations.' Normalization lowercases and strips all whitespace/punctuation, so case and the trailing period are ignored; similarity ratio >= 0.9 scores 1.0 (accepts minor OCR noise), else the rounded ratio. Appending the Chinese translation lowers the ratio below the threshold.
2. Row 5：Frame-verified from Bilibili BV1oc41137gf 《磨耳朵单词词——Vehicles交通工具》 (UP 程子与橙子, 272.3 s, 1280x720). The clip flashes ONE large English vehicle word on-screen per scene, held for several seconds, then a coloured swipe transition wipes to the next word. List EVERY large flashing English word that appears between 1:08 and 1:38 of the video, in the order it appears, de-duplicated (a lingering word counts once), ignoring the small Chinese gloss and any caption text. Verified big-word timeline (s): plane ~55-64.5, ship ~65.5-71.5, yacht ~72-78.5, sailboat ~79.2-86.5, jeep ~87-95, tank ~96-105.5, truck ~106.5+. Window [1:08,1:38] = [68 s, 98 s]: 68 s is ~2.5 s into 'ship' and 98 s is ~2 s into 'tank', both well clear of any swipe transition, so boundary words are unambiguous; 'plane' (before) and 'truck' (after) are excluded. Ordered GT = exactly these 5 lines: ship / yacht / sailboat / jeep / tank. Case- and punctuation-insensitive. Scored by mean best-position line similarity; the exact 5-line ordered answer = 1.0, and missing/extra/reordered words lower the score.
3. Row 6：Frame-verified from Bilibili BV1xP4y1R7uh 《儿童英语启蒙学习动画--Weather（天气）英语单词识记》 (UP 趣味英语动画, 227.5 s, 640x360). The clip flashes ONE large English weather word on-screen per scene, held for several seconds, then the scene changes and the next word appears. List EVERY large flashing English word that appears between 1:12 and 1:48 of the video, in the order it appears, de-duplicated (a lingering word counts once), ignoring the small 'It's X' caption and any Chinese text. Verified big-word timeline (s): cold ~34-39, foggy ~46-53, hot ~58-64, raining ~70.5-77, snowing ~81.5-88, stormy ~93-99, sunny ~106-112.5, windy ~116-124. Window [1:12,1:48] = [72 s, 108 s]: 72 s is ~1.5 s into 'raining' and 108 s is ~2 s into 'sunny', both >=1.5 s from any transition, so boundary words are unambiguous; 'hot' (before) and 'windy' (after) are excluded. Ordered GT = exactly these 4 lines: raining / snowing / stormy / sunny. Case- and punctuation-insensitive. Scored by mean best-position line similarity; the exact 4-line ordered answer = 1.0, and missing/extra/reordered words lower the score.
这一类规则在强调什么：这类规则强调时间窗、屏幕上真正要抄录的文本对象、去重规则，以及大小写/标点是否忽略，典型目标是把 OCR 任务写成可稳定自动判分的字符串匹配问题。
2. M016_video_subtitle_ocr_chinese_filter
示例记录：
1. Row 4：Frame-verified from Bilibili BV15U4y1E7kG 《彩虹是如何形成的？为什么有两圈？》 (UP 萌萌战队, 268s, 640x360, hardcoded white bottom narrator subtitles). The video opens by posing two questions (彩虹的成因 and 外圈为什么还有一道较暗的彩虹). List EVERY narrator bottom-subtitle sentence containing the two characters '彩虹' in the SECONDARY-RAINBOW (副虹 / 双彩虹) explanation segment (~3:06-3:42, t≈186-222) that answers the second question, in on-screen order, one per line, no punctuation. GT = exactly these 4 lines in order. EXCLUDE the primary-bow conclusion line '中间七彩色的彩虹' (~3:04, t=184, belongs to the preceding 主虹 topic) and all later arc/circular-rainbow lines that also contain 彩虹 (e.g. '由于彩虹里的小水滴发出的色散光线' at ~3:43 t=223, '所以我们在地面上看到彩虹', '会和飞机上一样看到圆环形彩虹', '而自己的投影有时恰好在圆环彩虹的中心' — a following topic). Also exclude 副虹-segment narrator lines without 彩虹 (e.g. '然后色散光偏折离开', '这种情况下入射光与红光夹角50度', '与紫光夹角53度', '色散光线最强', '此时紫光向地面偏折的角度比红光更大', '所以色带里的颜色顺序颠倒了过来') and the orange on-screen '副虹' keyword caption (not a commentary sentence). Note '也叫做双彩虹' counts because '双彩虹' contains '彩虹'. Scored by mean best-match line similarity (punctuation/whitespace stripped) to the 4 GT lines; missing/wrong/extra sentences lower the score, exact 4-line answer = 1.0.
2. Row 5：Frame-verified from Bilibili BV12f421v7oN 《闪电到底是向下劈还是向上劈？从闪电原理到大气电平衡》 (UP 萌萌战队). List EVERY narrator bottom-of-screen commentary subtitle sentence containing the two characters '冰粒' in the thundercloud charge-separation segment that answers the on-screen question '那么到底是谁在给地球这个电容器充电呢' (~1:22-1:49, storm cloud drifts in at '说话间一朵雷雨云飘来' t≈82, ends at '因此雷雨云出现电荷分离' t≈109-110), in on-screen order, one per line, no punctuation. GT = exactly these 6 lines in order. Only the bottom narrator commentary track counts; the segment's graphics are green particle blobs and arrows with no on-screen '冰粒' text label, so '冰粒' appears only in the narrator subtitle track. Narrator lines without '冰粒' in the same segment are excluded (e.g. '说话间一朵雷雨云飘来', '最终向下坠落', '都向底部集中', '而负电荷则向顶部集中', '因此相撞瞬间二者电荷中和并弹开', '因此雷雨云出现电荷分离'). Scored by mean best-match line similarity to the GT lines; missing/wrong/extra sentences lower the score, exact 6-line answer = 1.0.
3. Row 6：Frame-verified from Bilibili BV1Dn7j6yEyG 《为什么微波炉可以快速加热食物？》 (UP 原理视界). List EVERY narrator bottom-of-screen commentary subtitle sentence containing the three characters '水分子' in the microwave heating-mechanism segment that answers the opening on-screen question '为什么微波炉没有火却能快速加热食物' (~0:31-1:08, high-energy microwaves enter the food at '当这些高能微波进入食物后' t≈31, and the polar water molecules follow the alternating field and rub against neighbours until '所以呀最终就产生了热量' t≈68), in on-screen order, one per line, no punctuation. GT = exactly these 4 lines in order. Only the bottom narrator commentary track counts; the segment's graphics are 3-D water-molecule models labelled with letters/symbols (O, H, H+, δ+, 2δ-, 电场方向, 2450000000 Hz) with no on-screen '水分子' text label, so '水分子' appears only in the narrator subtitle track. Narrator lines without '水分子' in the same segment are excluded (e.g. '当这些高能微波进入食物后', '这种特殊结构更像是一块迷你磁铁', '如果对其施加外部电场', '而微波的电场方向刚好是来回变化的', '由于微波的频率是2.45G赫兹', '还不断地与周围分子产生摩擦碰撞' (contains 分子 but not 水分子), '所以呀最终就产生了热量'); the later danger line '因为鸡蛋里的水分在加热后会迅速变为蒸汽' (contains 水分 but not 水分子) is also excluded. Scored by mean best-match line similarity to the GT lines; missing/wrong/extra sentences lower the score, exact 4-line answer = 1.0.
这一类规则在强调什么：这类规则最强的地方在于“排除项”写得非常细：不仅说明要保留哪些字幕，还明确哪些相邻段落、哪些同主题但不属于当前问题的句子必须剔除。
3. M021_doc_reference_verification
示例记录：
1. Row 4：You are grading a CSV that lists, for the Tree of Thoughts paper's (Yao et al., arXiv:2305.10601) reference section, which citations that appear ONLY as a bare arXiv preprint (an entry whose venue is written as "arXiv preprint arXiv:XXXX.XXXXX", i.e. entries that do NOT already name a conference or journal) have SINCE been formally published at a peer-reviewed venue, together with that venue. CSV columns: Paper Title, Formal Venue.
2. Row 5：You are grading a CSV that lists, for the Self-Instruct paper's (Wang et al., arXiv:2212.10560) reference section, which citations that appear ONLY as a bare arXiv preprint (an entry whose venue is written as "arXiv preprint arXiv:XXXX.XXXXX", i.e. entries that do NOT already name a conference or journal) have SINCE been formally published at a peer-reviewed venue, together with that venue. CSV columns: Paper Title, Formal Venue.
3. Row 6：You are grading a CSV that lists, for the SimCSE paper's (Gao et al.,
这一类规则在强调什么：这类规则强调字段定义和任务边界，例如只统计原本是 bare arXiv preprint 的引用，已经明确写出 conference/journal 的条目不算，适合做结构化核验。
4. M034_video_tennis_shotlog_qa
示例记录：
1. Row 14：shots count; accept '71','71 shots','71拍'; distractor 84 (Chinese 84拍 overlay) NOT accepted
2. Row 15：ordered games pair, top row DJOKOVIC=2 then bottom FEDERER=5; '2-5'/'2:5'. Not sets (2,1) or points (40,30)
3. Row 16：fastest return speed 126 MPH (final title card). 186 KPH is NOT accepted
这一类规则在强调什么：这类体育问答规则重视“接受答案形式”和“干扰数字排除”。它不是只写标准答案，而是提前写明哪些表达算对、哪些相近数字或倒序写法必须判错。
5. M035_video_tennis_exhibition_qa
示例记录：
1. Row 17：Final result as three completed sets. Winner scoreline 7-6, 4-6, 7-6 (equivalently the loser's perspective 6-7, 6-4, 6-7). Deterministic: 1.0 iff the three set score pairs equal [(7,6),(4,6),(7,6)] or [(6,7),(6,4),(6,7)], else 0.0.
2. Row 18：Number of prior meetings the semifinal winner (Ostapenko) had already won vs opponent (Swiatek): 5 (H2H was 5-0). Accepted: 5 / 5-0 / 5:0 / 0-5 / '5 times' / '5 wins' / 5次 / five / 五. Deterministic: 1.0 iff extracted count == 5, else 0.0.
3. Row 19：Single surname on the scoreboard. Accepted: sinner / jannik sinner / j. sinner / j sinner / 辛纳 (case-insensitive substring match).
这一类规则在强调什么：这类体育问答规则重视“接受答案形式”和“干扰数字排除”。它不是只写标准答案，而是提前写明哪些表达算对、哪些相近数字或倒序写法必须判错。
6. M046_video_mme_news_segments
示例记录：
1. Row 4：Question: Count the total number of distinct segments that appear in the video. For each segment, identify its start and end timestamp.
2. Row 5：Question: The video interleaves talking-head / daylight ship b-roll with a small number of full-screen ANIMATED CLASSIFICATION-DIAGRAM segments — a distinctive dark-navy background covered with glowing blue hexagons that name ship categories (e.g. "船舶分类 / 运输船 / 货船 / 液货船"). Count how many such distinct full-screen classification-diagram segments appear, and give each segment's start and end timestamp.
3. Row 6：Question: Count the total number of distinct country chapters that appear in the video. For each chapter, identify the country it covers and its start and end timestamp.
这一类规则在强调什么：这类视频分段规则会先定义 segment 的视觉特征，再要求计数和起止时间，核心是避免不同人对“什么算一个段落”理解不一致。
7. M053_video_badminton_rally_count
示例记录：
1. Row 7：The current-game point total of the player representing China (CHN, Shi Yu Qi) on the on-screen broadcast scoreboard. Frame-verified from Bilibili BV19YdAYVEtQ (2025 Ningbo Asia Badminton Championships men's singles): the deciding-game match-point stretch shows CHN 20 : Macau 10 (games 1:0), so the CHN player has 20 points in the current game. Accept 20 in any form: '20', '20 points', 'twenty', '二十'. A lone integer is trusted; if several appear prefer the one near 'points'/'分', else the max. NOT '1' (games won), NOT '10' (opponent's points), NOT any other number.
2. Row 14：Points the losing pair (Fruergaard/Thygesen DEN) scored in game 2 (JPN won 21-15). Accept '15','15 points', or '21-15'/'21:15'/'21 to 15' (loser's 15 extracted). Others (19,21,8,20) score 0.
3. Row 15：Final game score (winner 21, loser 16). Unordered {21,16}; accept '21:16','21-16','21：16','16:21','21 to 16','21比16'. Others (e.g. 21:19, lone number) score 0.
这一类规则在强调什么：这类体育问答规则重视“接受答案形式”和“干扰数字排除”。它不是只写标准答案，而是提前写明哪些表达算对、哪些相近数字或倒序写法必须判错。
8. M065_video_tennis_net_error
示例记录：
1. Row 8：Sets Cobolli won (sets 2 & 4). Accept '2','2 sets','two','两'/'二'. Other counts score 0.
2. Row 15：km/h (Sam Groth ITF record). Tolerance +-0.5, accepts '263'..'263.4', '263.4 km/h','263.4kmh'. Other shown speeds 253/210.8 score 0.
3. Row 16：Server points=4 (0.4), opponent points=0/'love' (0.3), end time within +-3s of 0:52 (0.3). Accept '4-0','held to love','0:52'/'0:51'.
这一类规则在强调什么：这类体育问答规则重视“接受答案形式”和“干扰数字排除”。它不是只写标准答案，而是提前写明哪些表达算对、哪些相近数字或倒序写法必须判错。
八、原始提取记录（按 sheet 汇总）
下面保留本次提取的原始记录摘要。口径是：对每个 sheet，读取 E 列，抓取前 3 个非空单元格；若单元格内容很长，这里保留原文开头片段，便于快速回看。这个部分更像“抽样记录台账”，后续如果你要继续学习某一类任务，可以直接顺着 sheet 名回到源表细看。
Sheet
示例 1
示例 2
示例 3
M015_video_subtitle_ocr_english
Row 4: The single English sentence shown on screen between 0:52 and 0:54 of the video, transcribed verbatim to /workspace/outp…
Row 5: Frame-verified from Bilibili BV1oc41137gf 《磨耳朵单词词——Vehicles交通工具》 (UP 程子与橙子, 272.3 s, 1280x720). The clip flashes ONE la…
Row 6: Frame-verified from Bilibili BV1xP4y1R7uh 《儿童英语启蒙学习动画--Weather（天气）英语单词识记》 (UP 趣味英语动画, 227.5 s, 640x360). The clip flash…
M016_video_subtitle_ocr_chinese_filter
Row 4: Frame-verified from Bilibili BV15U4y1E7kG 《彩虹是如何形成的？为什么有两圈？》 (UP 萌萌战队, 268s, 640x360, hardcoded white bottom narrator s…
Row 5: Frame-verified from Bilibili BV12f421v7oN 《闪电到底是向下劈还是向上劈？从闪电原理到大气电平衡》 (UP 萌萌战队). List EVERY narrator bottom-of-screen c…
Row 6: Frame-verified from Bilibili BV1Dn7j6yEyG 《为什么微波炉可以快速加热食物？》 (UP 原理视界). List EVERY narrator bottom-of-screen commentary …
M021_doc_reference_verification
Row 4: You are grading a CSV that lists, for the Tree of Thoughts paper's (Yao et al., arXiv:2305.10601) reference section, wh…
Row 5: You are grading a CSV that lists, for the Self-Instruct paper's (Wang et al., arXiv:2212.10560) reference section, whic…
Row 6: You are grading a CSV that lists, for the SimCSE paper's (Gao et al.,
M022_video_movie_recognition
—
—
—
M029_video_surveillance_clip
Row 14: You are shown frames sampled from a short video clip.
Row 15: You are shown frames sampled from a short video clip taken from a live musical-gala
Row 16: You are shown frames sampled from a short clip taken from a dance tutorial video.
M032_video_tennis_rally_qa
—
—
—
M034_video_tennis_shotlog_qa
Row 14: shots count; accept '71','71 shots','71拍'; distractor 84 (Chinese 84拍 overlay) NOT accepted
Row 15: ordered games pair, top row DJOKOVIC=2 then bottom FEDERER=5; '2-5'/'2:5'. Not sets (2,1) or points (40,30)
Row 16: fastest return speed 126 MPH (final title card). 186 KPH is NOT accepted
M035_video_tennis_exhibition_qa
Row 17: Final result as three completed sets. Winner scoreline 7-6, 4-6, 7-6 (equivalently the loser's perspective 6-7, 6-4, 6-…
Row 18: Number of prior meetings the semifinal winner (Ostapenko) had already won vs opponent (Swiatek): 5 (H2H was 5-0). Accep…
Row 19: Single surname on the scoreboard. Accepted: sinner / jannik sinner / j. sinner / j sinner / 辛纳 (case-insensitive substr…
M043_video_mme_device_identification
—
—
—
M041_video_lvb_artwork_scene
Row 4: 不正确
Row 5: 不正确
Row 6: 不正确
M042_video_mme_multihop_reasoning
—
—
—
M044_video_mme_bugatti_identification
—
—
—
M045_video_mme_building_identification
—
—
—
M046_video_mme_news_segments
Row 4: Question: Count the total number of distinct segments that appear in the video. For each segment, identify its start an…
Row 5: Question: The video interleaves talking-head / daylight ship b-roll with a small number of full-screen ANIMATED CLASSIF…
Row 6: Question: Count the total number of distinct country chapters that appear in the video. For each chapter, identify the …
M048_video_fitness_pullup_frames
Row 18: 100 / 100个 / 100次 / 100 pull-ups / 一百
Row 19: 18 / 18个 / 18次 / 十八
Row 20: 5 / 5位 / 5人 / 5名 / five / 五
M051_video_surveillance_intrusion
—
—
—
M053_video_badminton_rally_count
Row 7: The current-game point total of the player representing China (CHN, Shi Yu Qi) on the on-screen broadcast scoreboard. F…
Row 14: Points the losing pair (Fruergaard/Thygesen DEN) scored in game 2 (JPN won 21-15). Accept '15','15 points', or '21-15'/…
Row 15: Final game score (winner 21, loser 16). Unordered {21,16}; accept '21:16','21-16','21：16','16:21','21 to 16','21比16'. O…
M055_video_badminton_baseline_out
Row 10: Under rally scoring every completed rally awards exactly one point; total = 30. Answer a single integer. Deterministic:…
Row 11: Second game's final score = 21-3 (winner 21, loser 3). Accepted forms: '21-3','21:3','21 to 3','21–3','MOMOTA 21 ANTONS…
Row 17: Longest rally length from the on-screen broadcast graphic = 61 shots. Answer a single integer. Accepts '61', '61 shots'…
M056_video_badminton_net_error
Row 9: Accepted forms: 22, twenty-two. Total points. Any other number scores 0.
Row 15: Accepted forms: 52, 52 shots, 52拍, fifty-two. The green on-screen shot counter's final value (freezes at 52). Any other…
Row 16: Accepted forms: 211, 211 shots, 211 strokes, 211拍. The longest rally is 211 shots. Any other number scores 0.
M057_video_pingpong_rally_count
—
—
—
M059_video_pingpong_smash_ace
—
—
—
M060_video_pingpong_let_serve
Row 14: winner's points first; accept 11-8 / 11:8 / 11 to 8 / 'Matsushima 11, Gerassimenko 8'. Reversed 8-11 is wrong.
Row 15: games Xinyu Wang won in set 1; accept '7', '7 games', 'seven', or a 7-5/7:5 pair (Wang first).
Row 16: last point score, Djokovic first Federer second (0/15/30/40). GT 30-40; reversed 40-30 wrong.
M062_video_snooker_brown_ball_time
—
—
—
M064_video_soccer_save_analysis
Row 15: First kick taken by Germany (德国/GER/Deutschland) AND the kick was NOT scored (no goal / saved / missed).
Row 18: Jersey number 10 (accept '10', '#10', '10号', 'number 10').
Row 19: Team Switzerland (瑞士/SUI/Suisse) whose GK made the first save; timestamp within [0:03, 0:10].
M065_video_tennis_net_error
Row 8: Sets Cobolli won (sets 2 & 4). Accept '2','2 sets','two','两'/'二'. Other counts score 0.
Row 15: km/h (Sam Groth ITF record). Tolerance +-0.5, accepts '263'..'263.4', '263.4 km/h','263.4kmh'. Other shown speeds 253/2…
Row 16: Server points=4 (0.4), opponent points=0/'love' (0.3), end time within +-3s of 0:52 (0.3). Accept '4-0','held to love',…
M066_video_tennis_lob_winner
Row 14: The integer 20 (on-screen POINTS 'Winners 20 | 19', left=Ruud). Accept '20', '20 winners', 'twenty'.
Row 15: On-screen TOTAL DISTANCE (IN METRES) for ALCARAZ = 75.73 m; accept within +/-0.05 (e.g. 75.73).
Row 16: First-set games as TOP-BOTTOM = '7-6' (top-row player 7, bottom-row player 6). Exact ordered pair (7,6).
M067_video_tennis_long_rally
Row 17: first-game winner=Federer/费德勒 (not Nadal); games score after game 1 = 1-0 in Federer's favor (0.5 each half).
Row 18: first-set games, unordered pair {7,5}; player order irrelevant (Siniakova 7 – Zheng 5).
Row 19: shots=21 (weight 0.6); start within 0:02-0:06 full / 0:00-0:08 partial (weight 0.4).
M070_video_tennis_serve_game_stats
—
—
—
M071_video_tennis_break_point_stats
Row 8: Games won by Rublev in the second set; a single integer.
Row 16: Total games won by runner-up Alexander Zverev across all sets combined; a single integer.
Row 17: Games won by Berdych in the first set; a single integer (digits only).
M099_su7_price_from_image_zh
Row 2: Evaluate whether the assistant correctly identified the car and provided a plausible price range.
—
—
M101_chinese_food_identification_zh
Row 2: This is an image-grounded identification task.
—
—
01_Productivity_Flow_task_2_table_tex_download
—
—
—
01_Productivity_Flow_task_7_openmmlab_contributors
—
—
—
04_Search_Retrieval_task_10_tomllib_trace
—
—
—
04_Search_Retrieval_task_2_conflicting_handling
—
—
—
04_Search_Retrieval_task_3_constraint_search
—
—
—
04_Search_Retrieval_task_4_efficient_search
—
—
—
04_Search_Retrieval_task_7_location_search
—
—
—
04_Search_Retrieval_task_9_artwork_search
—
—
—
补充说明：这个”原始提取记录”保留了最初抽取时看到的实际内容形态，因此会同时出现自然语言 rubric、占位标签、代码骨架、以及个别判定词。也正因为如此，前文的”归类分层”才有必要：它的作用就是把这些混杂信息里真正可学习、可复用的评分细则抽出来。

---

## 九、工程层解读：判分代码的模式拆解与生成实现（2026-08-20 追加）

> 说明：研发未提供评分代码样本，本文档基于评分标准中暴露的判分逻辑（`def grade(**kwargs) -> dict:` 接口形态 + Deterministic 规则 + accepted forms + 容差 + 部分分权重 + mean best-position similarity），**生成 5 个代表性判分模式的可运行实现**，逐条拆解工程实现要点。代码可直接复制运行验证，属”生成样本”，非研发原始代码。

### 9.0 公共层：统一接口 + 规范化

```python
import re
from difflib import SequenceMatcher

def normalize(text: str) -> str:
    “””幂等规范化：大小写 / 全角半角 / 中文标点 / 空白”””
    if text is None:
        return “”
    text = text.strip().lower()
    text = “”.join(chr(ord(c) - 0xFEE0) if “！” <= c <= “～” else c
                   for c in text)          # 全角 → 半角（数字标点）
    for ch in “，。！？：；、（）”:
        text = text.replace(ch, “ “)
    return re.sub(r”\s+”, “ “, text).strip()

def grade(answer: str, **kwargs) -> dict:
    “””统一判分接口（def grade(**kwargs) -> dict 的原型）：
    纯函数、无副作用、无随机 → 幂等可复现；返回分数 + 原因，可审计”””
    raise NotImplementedError
```

工程要点：

```text
├── 判分器统一签名 grade(answer) -> {“score”: 0~1, “reason”: ...}
│   = 批量跑（pandas apply / 多进程）、记录、归因的统一接口
├── normalize 就是”accepted forms 写死”的代码形态：
│   先归一化再判断等价，而不是字符串相等
├── 幂等性：纯函数 + 无随机 → 同输入必同输出（测试可断言）
└── 边界兜底：None / 空串 / 多空格 → normalize 全收口
```

### 9.1 模式一：计数类 + accepted forms + distractor 排除（M034 R14 / M053）

```python
def extract_integer_candidates(text: str) -> list[tuple[int, str]]:
    “””返回 (数字, 前后 6 字符上下文) 列表”””
    return [(int(m.group(1)), text[max(0, m.start() - 6):m.end() + 6])
            for m in re.finditer(r”(\d+)”, text)]

def pick_integer(text: str) -> int | None:
    “””文档原话转代码：'A lone integer is trusted; if several appear
    prefer the one near points/分, else the max'”””
    cands = extract_integer_candidates(text)
    if not cands:
        return None
    if len(cands) == 1:
        return cands[0][0]
    for num, ctx in cands:                      # 优先取带量词上下文的
        if any(k in ctx for k in (“points”, “shots”, “wins”, “分”, “拍”, “次”, “个”)):
            return num
    return max(num for num, _ in cands)         # 否则取最大

def grade_count(answer: str, gt: int, distractor: int | None = None) -> dict:
    norm = normalize(answer)
    num = pick_integer(norm)
    if num is None:
        return {“score”: 0.0, “reason”: “no integer found”}
    if num == gt:
        return {“score”: 1.0, “reason”: f”match {gt}”}
    if num == distractor:
        return {“score”: 0.0, “reason”: f”distractor {distractor} excluded”}
    return {“score”: 0.0, “reason”: f”{num} != {gt}”}
```

工程要点：

```text
├── 数字候选抽取：正则 \d+；全角数字已被 normalize 转半角
├── 启发式选择写死：单数字直接信；多数字优先”带量词上下文”，
│   否则取 max —— 这就是”干扰数字排除”在判定前的第一道闸
├── distractor 显式特判：命中干扰数字既不判对也不给部分分
│   （M034：84拍 overlay 是屏幕上更显眼的数字，模型极易抄错）
└── 为什么这样设计：记分板 / overlay 数字密集，模型会”答得像对
    但证据取错”；把干扰项写死 = 评测稳定性成本最低的杠杆
```

### 9.2 模式二：结构化比分 + Deterministic 0/1（M035 R17 / M053 R15）

```python
def parse_score_pairs(text: str) -> list[tuple[int, int]]:
    “””支持 - : ：to 比 全部分隔符（含全角冒号）”””
    return [(int(a), int(b))
            for a, b in re.findall(r”(\d+)\s*(?:-|:|：|to|比)\s*(\d+)”, text)]

def grade_best_of_three(text: str) -> dict:
    “””M035 R17：三盘比分，赢家或输家视角均可 → 结构化比对”””
    gt_winner = [(7, 6), (4, 6), (7, 6)]
    gt_loser = [(6, 7), (6, 4), (6, 7)]
    pairs = parse_score_pairs(normalize(text))
    ok = pairs in (gt_winner, gt_loser)
    return {“score”: 1.0 if ok else 0.0, “reason”: f”pairs={pairs}”}

def grade_unordered_pair(text: str) -> dict:
    “””M053 R15：无序对 {21,16} → set 比较”””
    pairs = parse_score_pairs(normalize(text))
    if not pairs:
        return {“score”: 0.0, “reason”: “no score pair”}
    a, b = pairs[0]
    ok = {a, b} == {21, 16}
    return {“score”: 1.0 if ok else 0.0, “reason”: f”pair=({a},{b})”}
```

工程要点：

```text
├── “Deterministic: 1.0 iff ... else 0.0” 的代码形态 = 结构化比对：
│   有序 → tuple 相等，无序 → set 相等，等价视角 → 白名单枚举
├── 这就是 Deterministic Floor：单一事实型问题全走规则，
│   不经过任何模型判断（LLM judge 的偏差在这里根本没有入场机会）
├── 分隔符白名单（- : ：to 比）必须显式列出并做全角归一
└── 边界：比分缺失 / 格式不符 → 0.0，不给部分分（严格 0/1）
```

### 9.3 模式三：数值 / 时间容差（M065 R15）

```python
def grade_numeric_tolerance(text: str, gt: float, tol: float = 0.5) -> dict:
    “””M065 R15：GT 263.4 km/h，容差 ±0.5，accept '263'..'263.4'”””
    m = re.search(r”\d+(?:\.\d+)?”, normalize(text).replace(“,”, “”))
    if not m:
        return {“score”: 0.0, “reason”: “no number”}
    val = float(m.group())
    ok = abs(val - gt) <= tol
    return {“score”: 1.0 if ok else 0.0,
            “reason”: f”val={val}, gt={gt}, tol={tol}”}

def parse_mmss(text: str) -> int | None:
    m = re.search(r”(\d+):(\d{2})”, text)
    return int(m.group(1)) * 60 + int(m.group(2)) if m else None

def grade_time_tolerance(text: str, gt_sec: int = 52, tol: int = 3) -> dict:
    “””M065 R16：结束时间在 0:52 ± 3s 内算对”””
    sec = parse_mmss(text)
    if sec is None:
        return {“score”: 0.0, “reason”: “no timestamp”}
    ok = abs(sec - gt_sec) <= tol
    return {“score”: 1.0 if ok else 0.0, “reason”: f”sec={sec}, gt={gt_sec}”}
```

工程要点：

```text
├── 容差的实现 = “归一化提取 → 数值距离 → 阈值”三步；
│   容差类型（文本相似 / 数值 / 时间）与问题类型配套
├── 时间统一转秒再比：0:52 vs 0:51 变成 52 vs 51 的整数距离
├── 千分位逗号要先剥（263.4 km/h vs 2,634 —— 防止量级误判）
└── 阈值的可配置性：±0.5 与 ±3s 是 per-sheet 参数，不进公共库
```

### 9.4 模式四：部分分权重（M065 R16：0.4 + 0.3 + 0.3）

```python
def grade_weighted(text: str) -> dict:
    “””M065 R16：发球方 4 分(0.4) + 接发方 0/love(0.3) + 结束时间 ±3s(0.3)”””
    t = normalize(text)
    score = 0.0
    detail = {}
    pairs = parse_score_pairs(t)
    server = pairs[0][0] if pairs else None
    opp = pairs[0][1] if pairs else None
    if server == 4:                        # 子项 1：'4-0' 左位
        score += 0.4; detail[“server”] = “ok”
    if opp == 0 or “love” in t:            # 子项 2：'love' 文字也算
        score += 0.3; detail[“opponent”] = “ok”
    sec = parse_mmss(t)                    # 子项 3
    if sec is not None and abs(sec - 52) <= 3:
        score += 0.3; detail[“end_time”] = “ok”
    return {“score”: round(score, 2), “detail”: detail}
```

工程要点：

```text
├── 部分分 = 把一道题拆成子问题清单，各自判分后加权求和；
│   权重和 = 1，分数可解释（detail 记录每个子项命中情况）
├── 这是”全有或全无 vs 部分得分”的评测设计选择：
│   多子项题用部分分，避免 0/1 把”答对一半”抹成 0
├── 子项之间解耦：一个子项缺失不影响其他子项得分
└── 审计友好：detail 字典 = 归因分析的最小单元
```

### 9.5 模式五：有序列表相似度（M015 / M016 字幕类）

```python
def grade_line_list(text: str, gt_lines: list[str]) -> dict:
    “””mean best-position line similarity：每行 GT 与答案行做
    best match，取平均；完整匹配 = 1.0，缺/多/乱序降分”””
    ans_lines = [normalize(l) for l in text.splitlines() if l.strip()]
    gt_norm = [normalize(l) for l in gt_lines]
    if not ans_lines:
        return {“score”: 0.0, “reason”: “empty answer”}
    per_line = [max((SequenceMatcher(None, g, a).ratio() for a in ans_lines),
                    default=0.0) for g in gt_norm]
    return {“score”: round(sum(per_line) / len(gt_norm), 4),
            “per_line”: per_line, “n_ans”: len(ans_lines)}
```

工程要点：

```text
├── 开放输出（字幕转录）不能精确比对 → 退到序列相似度；
│   相似度阈值（≥ 0.9）= 容忍 OCR 噪声的显式阈值
├── 简版实现是 one-to-many（一行答案可被多行 GT 重复匹配）：
│   不惩罚多余行；文档写 “extra/reordered lines lower the score”，
│   严格版需 bipartite matching（匈牙利算法）+ 位置偏差惩罚
│   —— 这就是”知道简化代价”的工程判断
├── 为什么字幕类也不用 LLM judge：GT 是逐字转录，可精确比对；
│   相似度计算是确定性的，LLM 判分反而引入位置/冗长偏差
│   （连接 papers/05 LLM Judge 可靠性）
└── 幂等无随机：SequenceMatcher 纯算法，可复现可测试
```

### 9.6 共性抽象：80% 模板 + 20% 配置

```python
GRADERS = {
    “M034_video_tennis_shotlog_qa”: lambda t: grade_count(t, gt=71, distractor=84),
    “M035_video_tennis_exhibition_qa”: grade_best_of_three,
    “M053_video_badminton_rally_count”: lambda t: grade_count(t, gt=20),
    “M065_video_tennis_net_error”: grade_weighted,
    “M015_video_subtitle_ocr_english”: lambda t: grade_line_list(t, GT_M015),
    # ... 39 个 sheet = 39 个注册项
}

def run_sheet(sheet: str, answer: str) -> dict:
    “””批量跑入口：pandas.apply(run_sheet) 即全量判分”””
    return GRADERS[sheet](answer)
```

工程要点：

```text
├── 验证了”大概率 80% 模板 + 20% 题目特定逻辑”的预期：
│   公共库（normalize / pick_integer / parse_score_pairs /
│   相似度）+ per-sheet 配置或自定义判分器
├── 新增一个 sheet = 注册一行，不侵入公共代码（开闭原则）
├── 规模化：规则判分纯 CPU 毫秒级，400+ 答案秒级跑完；
│   成本瓶颈在 LLM judge 层（证据类校验），不在规则层
└── 可批量 = 回答了”评分代码能否批量跑”（Q4）：能，且廉价
```

### 9.7 测试：把文档真例变成断言

```python
def test_distractor_excluded():
    assert grade_count(“84拍”, gt=71, distractor=84)[“score”] == 0.0   # M034 R14
    assert grade_count(“71拍”, gt=71, distractor=84)[“score”] == 1.0
    assert grade_count(“71 shots”, gt=71, distractor=84)[“score”] == 1.0

def test_deterministic_scoreline():
    assert grade_best_of_three(“7-6, 4-6, 7-6”)[“score”] == 1.0       # 赢家视角
    assert grade_best_of_three(“6-7, 6-4, 6-7”)[“score”] == 1.0       # 输家视角
    assert grade_best_of_three(“2-1”)[“score”] == 0.0

def test_tolerance_and_partial():
    assert grade_numeric_tolerance(“263.4 km/h”, gt=263.4)[“score”] == 1.0
    assert grade_numeric_tolerance(“264.0”, gt=263.4)[“score”] == 0.0  # 差 0.6 > 容差
    assert grade_weighted(“4-0, 0:52”)[“score”] == 1.0
    assert grade_weighted(“4-0”)[“score”] == 0.7                      # 缺时间子项
```

### 9.8 工程层总结（面试可讲）

```text
判分器五模式的本质：
├── 模式一/二 = 把”唯一答案”转成确定性匹配（Deterministic Floor）
├── 模式三/四 = 把”允许的偏差”显式化（容差 + 部分分）
├── 模式五 = 把”开放输出”退到可计算的距离（相似度）
└── 统一接口 + 注册表 = 39 个 sheet 可批量、可测试、可审计

工程视角四条追问的答案：
├── 幂等性？纯函数无副作用，同输入同输出
├── 可复现性？无随机；LLM judge 层才需要 seed 与固定 prompt
├── 边界处理？normalize 收口 + 候选启发式 + 显式 distractor
└── 规模翻 100 倍？规则层纯 CPU 秒级，瓶颈在 LLM 层 → 分层判分
```