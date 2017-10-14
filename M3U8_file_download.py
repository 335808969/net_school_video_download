import requests
import urllib
import json
from bs4 import BeautifulSoup
import os
import re

#-------------------------
f = -1
def open_log(url):
    f = open(url.replace("\/", "_"), "w")

def write_log(log):
    try:
        f.write(log)
    except:
        print("write log:%s failed" %(log))

def close_log_file():
    f.close()
#-------------------------

#使用SuperDownloader软件分析的解析对象，软件下载地址http://103.39.79.26/
parse_actual_url_head = "http://103.39.79.26//jiexi/net/yingsheng.php?url="
parse_m3u8_actual_url_head = "http://103.39.79.26//jiexi/net/bokecc.php?bokecc=yingsheng%7C"
yingsheng_main_page = "http://www.yingsheng.com"

def GetM3U8Data(url):
    list = []
    i = 3
    while i != 0:
        list.clear()
        try:
            print("aaaa")
            response = urllib.request.urlopen(url)
            print("bbb")
            if response.status == 200:
                print("ccc")
                data = response.read().decode("utf-8")
                print("dddd")
                ls = data.split("\n")
                for l in ls:
                    try:
                        if l[0] != '#':
                            list.append(l)
                    except:
                        pass
            break
        except:
            i = i -1
            print("open %s failed\n" %(url))
            continue
    return list

def WriteTsData(url, lis, filePath):
    print("create file:%s" %(filePath))
    with open(filePath, "wb") as f:
        for l in lis:
            index1 = url.find(".m3u8")
            index2 = l.find(".ts")
            new_url = url[:index1] + l[index2:]
            print(new_url)
            try:
                response = urllib.request.urlopen(new_url)
                if response.status == 200:
                    data = response.read(4096)
                    while len(data) != 0:
                        f.write(data)
                        f.flush()
                        data = response.read(4096)
            except:
                print("get %s failed" %(url))
                pass
    f.close()

def parse_m3u8_info_key(url):
    list = []
    i = 3
    while i != 0:
        list.clear()
        try:
            res = urllib.request.urlopen(parse_actual_url_head+url)
            if res.status == 200:
                data = res.read().decode("utf-8")
                json_info = json.loads(data.replace('\r\n', ''))
                return json_info["data"]
        except:
            i = i-1
            print("get %s failed, aaa" %(parse_actual_url_head+url))
            continue

    return list

def get_m3u8_url(key):
    str = ''
    i = 3
    while i != 0:
        url = parse_m3u8_actual_url_head + key
        try:
            res = urllib.request.urlopen(url)
            if res.status == 200:
                data = res.read().decode("utf-8")
                json_info = json.loads(data.replace('\r\n', ''))  # , encoding="utf-8",ensure_ascii=True)
                return json_info["response"]['qualities'][0]["copies"][0]["playurl"]
        except:
            i = i-1
            print("except occur %s" %(url))
            continue
    return str

def get_dir_path_name(url):
    str = ""
    i = 3
    while i != 0:
        try:
            res = urllib.request.urlopen(url)
            bs = BeautifulSoup(res.read().decode("utf-8"), "html.parser")
            str =  bs.title.string
            break
        except:
            i = i-1
            print("get title failed url:%s" %(url))
            continue
    return str

def get_actual_course_list(url):
    list = []
    i = 3
    while i != 0:
        list.clear()
        if url.find("course") != -1:
            list.append(url)
        elif url.find("performance") != -1:
            try:
                res = urllib.request.urlopen(url)
                bs = BeautifulSoup(res.read().decode("utf-8", "html.parser"))
                div_tag = bs.find("div", "detail_class")
                div_tag_list = div_tag.find_all("li")
                for dl in div_tag_list:
                    list.append(yingsheng_main_page+dl.find('a')['href'])
                return list
            except:
                i = i-1
                print("get performance data failed url:%s" %(url))
                continue
        elif url.find("special"):
            try:
                print(url)
                res = urllib.request.urlopen(url)
                bs = BeautifulSoup(res.read().decode("utf-8", "html.parser"))
                div_tag = bs.find_all("div", style=re.compile("background"))
                for div in div_tag:
                    if div.find("a"):
                        list.append(div.find("a")["href"])
                return list
            except:
                i=i-1
                print("get special data failed url:%s" %(url))
                continue
    return list

if __name__ == "__main__":
#支持岗位系统课，热销系统班，普通课程，添加对应url到url_list中
    url_list =['http://www.yingsheng.com/performance/list-181','http://www.yingsheng.com/performance/list-38','http://www.yingsheng.com/performance/list-37','http://www.yingsheng.com/performance/list-161','http://www.yingsheng.com/performance/list-162','http://www.yingsheng.com/performance/list-36','http://www.yingsheng.com/performance/list-35']
   # url_list = ["http://www.yingsheng.com/course-2429.html", "http://www.yingsheng.com/performance/list-12"]
    #url_list=["http://www.yingsheng.com/special/150810"]
    for url in url_list:
        #open_log(url)

        download_path=get_dir_path_name(url)
        new_url_list = get_actual_course_list(url)
        for l in new_url_list:
            print(l)
        for url in new_url_list:
            download_path_new = './' + download_path
            if len(new_url_list) != 1:
                download_path_new = download_path_new+'/'+get_dir_path_name(url)
            if len(download_path_new) == 0:
                print("get dir path failed<%s>" %(url))
                continue
            if os.path.exists(download_path_new) == False:
                os.makedirs(download_path_new)
                print(download_path_new)

            list = parse_m3u8_info_key(url)

            for l in list:
               l["m3u8_url"] = get_m3u8_url(l["videoid"])
               print(l)

            for l in list:
                list_m3u8_ts_info = GetM3U8Data(l["m3u8_url"])
                print(download_path_new)
                WriteTsData(l["m3u8_url"], list_m3u8_ts_info, download_path_new+"/"+l["title"] + ".ts")

        #close_log_file()
    #下面为使用SuperDownloader保存的m3u8文件作为解析对象，
    #url = "http://cm14-ccm1-1.play.bokecc.com/flvs/1546A7B7FB895F49/2016-07-23/36D2A47B8FEF951A9C33DC5901307461-20.m3u8?t=1507827167&key=4E0AB7C5B2E4AAAA121998A9D3BF85AB"
    #file = "英盛网-1631.txt"
  #  with open(file, "r", encoding='UTF-8') as f:
  #      lines = f.readlines()
  #      for i in range(0, len(lines), 2):
  #          filePath='./'+ lines[i][:len(lines[i])-1] + ".ts"
 #           url = lines[i+1]
  #          list=[]
  #          list = GetM3U8Data(url)
  #          WriteTsData(url, list, filePath)