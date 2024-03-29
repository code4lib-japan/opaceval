from rich import print
import requests
import unicodedata
import isbnlib

# https://docs.google.com/spreadsheets/d/1KgIK9Yioy-uoup0nCjHDNQ8uGN-o5N2HIzr3KvcyAII/edit#gid=0

query_sets = """QID-2020-01	i	西加奈子の小説「i」を読みたい
QID-2020-02	こころ	夏目漱石の小説「こころ」（原著「こゝろ」）を読みたい
QID-2020-03	メンターと出会う法	本田健著の実用書「人生を変えるメンターと出会う法」を読みたい
QID-2020-04	骨を彩る	彩瀬まる著の小説「骨を彩る」を読みたい
QID-2020-05	若者よマルクスを読もう	内田樹・石川康宏著による書簡「若者よ、マルクスを読もう」を読みたい
QID-2020-06	it	スティーブン・キングによる小説「it」を読みたい
QID-2020-07	1984	ジョージ・オーウェルの小説「1984」を読みたい
QID-2020-08	チーズはどこへ消えた?   	ベストセラー「チーズはどこに消えた？」を読みたい
QID-2020-09	広辞苑 第七版	国語辞書「広辞苑」第7版を読みたい
QID-2020-10	ぐりとぐら	絵本「ぐりとぐら」を読みたい
QID-2020-11	思考の整理学	外山滋比古著の書籍「思考の整理学」を読みたい
QID-2020-12	少年と犬	馳星周著の直木賞受賞作「少年と犬」を読みたい
QID-2020-13	絵本の名作200	Casa BRUTUS特別編集「読み継ぐべき絵本の名作200」を読みたい
QID-2020-14	ヒマつぶしの作法	東海林さだお著「ヒマつぶしの作法」を読みたい
QID-2020-15	感染症は実在しない	岩田健太郎著「感染症は実在しない」を読みたい
QID-2020-16	社会とは何か	竹沢尚一郎著「社会とは何か」を読みたい
QID-2020-17	村上ラヂオ	村上春樹によるエッセイ「村上ラヂオ」を読みたい
QID-2020-18	算数脳パズル空間なぞぺ～	『考える力がつく算数脳パズルなぞぺー』を読みたい
QID-2020-19	後悔しない死の迎え方	後閑愛実著「後悔しない死の迎え方」を読みたい
QID-2020-20	唐代の国際関係	石見清裕著「唐代の国際関係」を読みたい
QID-2020-21	夜9時からの、癒しのスープ 	高山かづえ著「癒しのスープ」を読みたい
QID-2020-22	鉄輪	夢枕獏著「陰陽師 鉄輪」を読みたい
"""

correct_sets = """QID-2020-01	9784591164457
QID-2020-02	9784041001202
QID-2020-02	9784101010137
QID-2020-02	9784000269735
QID-2020-02	9784872578119
QID-2020-02	9784003101117
QID-2020-02	9784087520095
QID-2020-02	9784167158026
QID-2020-03	9784479794738
QID-2020-04	9784344024908
QID-2020-04	9784344425699
QID-2020-05	9784044086121
QID-2020-05	9784780303605
QID-2020-05	9784780307146
QID-2020-06	9784167148072
QID-2020-06	9784167148089
QID-2020-06	9784167148096
QID-2020-06	9784167148102
QID-2020-07	9784151200533
QID-2020-10	9784834014778
QID-2020-10	9784834000825
QID-2020-11	9784480017017
QID-2020-11	9784480020475
QID-2020-13	9784838789801
QID-2020-14	9784815603847
QID-2020-15	9784762826962
QID-2020-16	9784121020376
QID-2020-17	9784101001524
QID-2020-17	9784838722501
QID-2020-17	9784838724505
QID-2020-17	9784101001654
QID-2020-17	9784101001685
QID-2020-18	9784794217448
QID-2020-19	9784478106372
QID-2020-20	9784634349353
QID-2020-21	9784415327587
QID-2020-22	9784163240404
QID-2020-22	9784167528225
"""


def normalize_isbn(isbn: (str, None)) -> (str, None):
    """
    ISBNを集約用に正規化する
    :param isbn: 文字列
    :return: isbn 文字列 / None
    """
    if not isbn:
        return None
    _isbn = unicodedata.normalize('NFKC', isbn).strip()
    _isbn = isbnlib.canonical(_isbn)
    if isbnlib.is_isbn13(_isbn) and _isbn[0:3] == '978':
        return isbnlib.to_isbn10(_isbn)
    if isbnlib.is_isbn13('978' + _isbn):
        return isbnlib.to_isbn10('978' + _isbn)
    if len(_isbn) == 13 and isbnlib.is_isbn10(_isbn[3:]):
        return _isbn[3:]
    return _isbn if isbnlib.is_isbn10(_isbn) or isbnlib.is_isbn13(_isbn) else None


def call_unitrad(query):
    r = requests.get('https://unitrad-tokyo-1.calil.jp/v1/search', params={
        'free': query,
        'region': 'gk-2002005-w6j41'
    })
    data = r.json()
    while data['running']:
        r = requests.get('https://unitrad-tokyo-1.calil.jp/v1/polling', params={
            'uuid': data['uuid'],
            'timeout': str(10),
            'version': str(data['version']),
        })
        data = r.json()

    results = set()
    results_list = []
    for item in data['books']:
        results.add(normalize_isbn(item['isbn']))
        results_list.append(normalize_isbn(item['isbn']))
    return results, results_list


def call_enju(query):
    r = requests.get('https://dev.next-l.jp/manifestations.json', params={
        'utf8': '✓',
        'query': query,
        'per_page': '1000'
    })
    data = r.json()
    results = set()
    results_list = []
    for item in data['results']:
        # print(item)
        for identifier in item['identifiers']:
            if identifier['identifier_type'] == 'isbn':
                results.add(normalize_isbn(identifier['body']))
                results_list.append(normalize_isbn(identifier['body']))
    return results, results_list


def reciprocal_rank(ranking, corrects):
    hits = corrects.intersection(ranking)
    if len(hits) == 0:
        return 0.0
    for idx, e in enumerate(ranking):
        if e in c:
            return (1.0 / (idx + 1))


# 答えのテーブルをつくる
correct = {}
for line in correct_sets.splitlines():
    cols = line.split('\t')
    if cols[0] not in correct:
        correct[cols[0]] = []
    correct[cols[0]].append(normalize_isbn(cols[1]))

metrics_calil = {"recall": [], "mrr": []}
metrics_enju = {"recall": [], "mrr": []}
for line in query_sets.splitlines():
    print('------------------')
    cols = line.split('\t')
    print(f"[{cols[0]}]{cols[1]}")
    r_calil, list_calil = call_unitrad(cols[1])
    print(f"カーリル: {len(r_calil)}件")
    r_enju, list_enju = call_enju(cols[1])
    print(f"Enju: {len(r_enju)}件")
    intersection = r_calil.intersection(r_enju)
    print(f"共通:{len(intersection)}件")
    calil_difference = r_calil.difference(r_enju)
    print(f"カーリルのみ:{len(calil_difference)}件")
    enju_difference = r_enju.difference(r_calil)
    print(f"Enjuのみ:{len(enju_difference)}件")
    if cols[0] in correct:
        print(f"正解:{len(correct[cols[0]])}件")
        c = set(correct[cols[0]])
        invlid_calil = c.difference(r_calil)
        print(f"カーリル不足:{len(invlid_calil)}件")
        invlid_enju = c.difference(r_enju)
        print(f"Enju不足:{len(invlid_enju)}件")
        print(invlid_enju)
        print("Recall:")
        recall = float(len(c.intersection(r_calil))) / len(c)
        metrics_calil["recall"].append(recall)
        print("\tカーリル: {0:.3f}".format(recall))
        recall_calil = recall
        recall = float(len(c.intersection(r_enju))) / len(c)
        recall_enju = recall
        metrics_enju["recall"].append(recall)
        print("\tEnju: {0:.3f}".format(recall))
        print("MRR:")
        score = reciprocal_rank(list_calil, c)
        print("\tカーリル: {0:.3f}".format(score))
        metrics_calil["mrr"].append(score)
        mrr_calil = score

        score = reciprocal_rank(list_enju, c)
        print("\tEnju: {0:.3f}".format(score))
        metrics_enju["mrr"].append(score)
        mrr_enju = score

    print(",".join(['tsv', cols[0], cols[1], "{0:.3f}".format(recall_calil), "{0:.3f}".format(mrr_calil), "{0:.3f}".format(recall_enju), "{0:.3f}".format(mrr_enju)]))

print('==================')
print("[Recall]カーリル: {0:.3f}".format(float(sum(metrics_calil["recall"])) / len(metrics_calil["recall"])))
print("[Recall]Enju: {0:.3f}".format(float(sum(metrics_enju["recall"])) / len(metrics_enju["recall"])))
print("[MRR]カーリル: {0:.3f}".format(float(sum(metrics_calil["mrr"])) / len(metrics_calil["mrr"])))
print("[MRR]Enju: {0:.3f}".format(float(sum(metrics_enju["mrr"])) / len(metrics_enju["mrr"])))
