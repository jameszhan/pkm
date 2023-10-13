# `Series`, `Anthology` 和 `Album`

"Series"、"anthology" 和 "album" 在英语中有不同的含义，分别对应不同类型的集合。让我们来看看每个词的具体用法：

- Series: 这个词通常指的是一组相关的作品 —— 如书籍、电视节目、文章等，它们是按一定的顺序发布的，通常共享共同的主题、角色或设置。"Series" 用于描述连续的作品集，每个作品都是独立的，但又与其他作品相关。例如，一部小说的系列，或者一个电视剧的多个季。
- Anthology: 这个词指的是一个集合作品，通常是短篇小说、诗歌、文章等，这些作品由不同的作者创作，但收录在同一本书中。"Anthology" 通常用于文学或音乐领域，指的是一个主题或风格下的不同作品的集合。
- Album: 在音乐领域，这个词指的是一组录音的集合，这些录音作为一个单一的作品发布。例如，一个音乐专辑包含了一个艺术家或乐队的多首歌曲。

总的来说，如果你是在谈论一系列相关的书籍或其他媒体，"series" 可能是最合适的词汇。如果你是在描述一个不同作品的集合，特别是文学或音乐作品，"anthology" 或 "album" 可能更适合，具体取决于上下文。每个词都有其特定的用途，所以选择哪个词取决于你想要表达的具体意思。


```bash
$ python3 manage.py shell
```

```python
import re
from webfs.models import ManagedFile

pattern = re.compile(r"series/([^/]+)")
files = ManagedFile.objects.filter(original_path__istartswith="shared/ebooks/series/")
series_map = {}
for file in files:
    match = pattern.search(file.original_path)
    if match:
        series_name = match.group(1)
        if series_name not in series_map:
            series_map[series_name] = 1
        else:
            series_map[series_name] += 1
            
print(series_map)
```

```json
{
  "一生的读书计划": 12,
  "世界数学名题欣赏丛书": 13,
  "世界科技全景百卷书": 14,
  "世界科普名着精选": 19,
  "世界经典机智与幽默其思妙答": 19,
  "中国历史大讲堂": 5,
  "中学数学丛书": 6,
  "中学数学奥林匹克丛书": 11,
  "中学数学思维方法丛书": 8,
  "中学数学拓展丛书": 4,
  "中学物理思维方法丛书": 13,
  "中学生探索学习丛书": 1,
  "中学生数学视野丛书": 9,
  "中学生文库": 33,
  "二十世纪中国民俗学经典": 8,
  "二十世纪西方哲学译丛": 9,
  "人类未解之谜新探索": 10,
  "从零开始学电子技术丛书": 11,
  "全美经典学习指导系列": 51,
  "初等数学小丛书": 28,
  "初等数学精品库": 2,
  "加德纳趣味数学系列": 17,
  "名人随笔精品": 7,
  "国外电子与通信教材系列": 44,
  "图灵新知": 4,
  "图灵电子与电气工程丛书": 30,
  "大众心理学丛书": 5,
  "好玩的数学": 10,
  "学习方法指导丛书": 4,
  "安徒生童话全集": 5,
  "应用数学丛书": 9,
  "当代心理科学名著译丛": 1,
  "当代西方刑侦经典系列": 4,
  "数学小丛书": 21,
  "数学教育前沿研究丛书": 6,
  "数学方法论丛书": 13,
  "数学方法论应用传播丛书": 2,
  "数学科学文化理念传播丛书": 1,
  "日本中学生数学丛书": 10,
  "汉译世界学术名著丛书": 110,
  "科学大师佳作系列": 5,
  "精彩人生100系列": 5,
  "精神分析经典译丛": 1,
  "经济学家茶座": 1,
  "自然珍藏图鉴丛书": 25,
  "英语词汇学习丛书": 6,
  "西方名著入门": 8,
  "西方数学文化理念传播译丛": 4,
  "计算数学丛书": 11,
  "走向数学丛书": 18,
  "走向科学的明天丛书": 5,
  "通俗数学名著译丛": 31,
  "飞碟探索丛书": 5,
  "马丁·加德纳趣味数学作品集": 15
}
```

```python
chinese_to_english = {
    "一生的读书计划": "Lifetime Reading Plan",
    "世界数学名题欣赏丛书": "World's Famous Math Problems Series",
    "世界科技全景百卷书": "World Technology Panorama: 100 Volumes",
    "世界科普名着精选": "World Science Popularization Classics Selection",
    "世界经典机智与幽默其思妙答": "World Classics of Wit and Humor",
    "中国历史大讲堂": "Chinese History Lecture Hall",
    "中学数学丛书": "Middle School Mathematics Series",
    "中学数学奥林匹克丛书": "Middle School Mathematics Olympiad Series",
    "中学数学思维方法丛书": "Middle School Mathematical Thinking Methods Series",
    "中学数学拓展丛书": "Middle School Mathematics Extension Series",
    "中学物理思维方法丛书": "Middle School Physics Thinking Methods Series",
    "中学生探索学习丛书": "Exploratory Learning Series for Middle School Students",
    "中学生数学视野丛书": "Mathematical Horizon Series for Middle School Students",
    "中学生文库": "Middle School Students' Library",
    "二十世纪中国民俗学经典": "Twentieth-Century Chinese Folklore Classics",
    "二十世纪西方哲学译丛": "Twentieth-Century Western Philosophy Series",
    "人类未解之谜新探索": "New Explorations into the Unsolved Mysteries of Humanity",
    "从零开始学电子技术丛书": "Learn Electronics from Scratch Series",
    "全美经典学习指导系列": "American Classic Study Guide Series",
    "初等数学小丛书": "Elementary Mathematics Mini Series",
    "初等数学精品库": "Elementary Mathematics Premium Library",
    "加德纳趣味数学系列": "Gardner's Fun Mathematics Series",
    "名人随笔精品": "Celebrities' Essays Boutique",
    "国外电子与通信教材系列": "Foreign Electronics and Communication Textbook Series",
    "图灵新知": "Turing New Knowledge",
    "图灵电子与电气工程丛书": "Turing Electronics and Electrical Engineering Series",
    "大众心理学丛书": "Popular Psychology Series",
    "好玩的数学": "Fun with Mathematics",
    "学习方法指导丛书": "Learning Methodology Guide Series",
    "安徒生童话全集": "Complete Collection of Andersen's Fairy Tales",
    "应用数学丛书": "Applied Mathematics Series",
    "当代心理科学名著译丛": "Contemporary Psychology Science Masterpieces Series",
    "当代西方刑侦经典系列": "Contemporary Western Detective Classics Series",
    "数学小丛书": "Mathematics Mini Series",
    "数学教育前沿研究丛书": "Frontline Research in Mathematics Education Series",
    "数学方法论丛书": "Mathematical Methodology Series",
    "数学方法论应用传播丛书": "Mathematical Methodology Application and Communication Series",
    "数学科学文化理念传播丛书": "Communication of Mathematical Science Cultural Concepts Series",
    "日本中学生数学丛书": "Japanese Middle School Mathematics Series",
    "汉译世界学术名著丛书": "Chinese Translations of World Academic Masterpieces Series",
    "科学大师佳作系列": "Science Masters' Excellent Works Series",
    "精彩人生100系列": "Wonderful Life 100 Series",
    "精神分析经典译丛": "Psychoanalysis Classics Translation Series",
    "自然珍藏图鉴丛书": "Nature Treasury Illustrated Series",
    "英语词汇学习丛书": "English Vocabulary Learning Series",
    "西方名著入门": "Introduction to Western Classics",
    "西方数学文化理念传播译丛": "Western Mathematical Cultural Concepts Translation Series",
    "计算数学丛书": "Computational Mathematics Series",
    "走向数学丛书": "Towards Mathematics Series",
    "走向科学的明天丛书": "Towards the Science of Tomorrow Series",
    "通俗数学名著译丛": "Popular Mathematics Masterpieces Translation Series",
    "飞碟探索丛书": "UFO Exploration Series",
    "马丁·加德纳趣味数学作品集": "Martin Gardner’s Mathematical Games"
}
```