import requests
import urllib
import json

#使用SuperDownloader软件分析的解析对象，软件下载地址http://103.39.79.26/
parse_actual_url_head = "http://103.39.79.26//jiexi/net/yingsheng.php?url="
parse_m3u8_actual_url_head = "http://103.39.79.26//jiexi/net/bokecc.php?bokecc=yingsheng%7C"

def GetM3U8Data(url):
    list = []
    try:
        response = urllib.request.urlopen(url)
        if response.status == 200:
            data = response.read().decode("utf-8")
            ls = data.split("\n")
            for l in ls:
                try:
                    if l[0] != '#':
                        list.append(l)
                except:
                    pass
    except:
        print("open %s failed\n" %(url))
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
                    data = response.read()#.decode("utf-8")
                    print(f.write(data))
            except:
                print("except occur")
                pass
    f.close()

def parse_m3u8_info_key(url):
    list = []
    try:
        res = urllib.request.urlopen(parse_actual_url_head+url)
       # print(res.status)
        if res.status == 200:
            data = res.read().decode("utf-8")
            #print(data)
            json_info = json.loads(data.replace('\r\n', ''))#, encoding="utf-8",ensure_ascii=True)
           # print(json_info)
            return json_info["data"]
    except:
        print("except occur")
        return list
        pass

def get_m3u8_url(key):
    url = parse_m3u8_actual_url_head + key
    str = ''
    try:
        res = urllib.request.urlopen(url)
        if res.status == 200:
            data = res.read().decode("utf-8")
            json_info = json.loads(data.replace('\r\n', ''))  # , encoding="utf-8",ensure_ascii=True)
            return json_info["response"]['qualities'][0]["copies"][0]["playurl"]
    except:
        print("except occur")
    return str

if __name__ == "__main__":

    url="http://www.yingsheng.com/course-2429.html"
    list = parse_m3u8_info_key(url)

    for l in list:
       l["m3u8_url"] = get_m3u8_url(l["videoid"])
       print(l)

    for l in list:
        list_m3u8_ts_info = GetM3U8Data(l["m3u8_url"])
        WriteTsData(l["m3u8_url"], list_m3u8_ts_info, l["title"] + ".ts")

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