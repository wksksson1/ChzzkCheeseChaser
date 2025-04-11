import time
import requests
import json
import os
import argparse


class CheeseAccount:

    def __init__(self, NID_AUT, NID_SES):
        self.__cookies = {'NID_AUT': NID_AUT, 'NID_SES': NID_SES}
        self.__lastRefreshTime = 0     #검색 시간을 초기화
        self.__purchaseList = []        # 구매 리스트를 초기화
        self.refreshList()          #구매 리스트 최초 갱신

    def setCookies(self, NID_AUT, NID_SES):
        self.__cookies = {'NID_AUT': NID_AUT, 'NID_SES': NID_SES}

    def getCookies(self):
        return self.__cookies
    

    def refreshList(self):
        newPurchaseList = []

        #헤더와 기본 Url
        headers={"user-agent":"Mozilla/5.0 (compatible; exhentai-extractor;)", "referer":"https://game.naver.com/profile"}
        urlBase="https://api.chzzk.naver.com/commercial/v1/coin/history/purchase?"

        #처음에 Json 요청을 보낸 후 첫 페이지 치즈 내역과 총 치즈 페이지 갯수를 구한다.
        requestURL = urlBase + "page=0&pageSize=10"
        apiResponse = requests.get(requestURL, headers=headers, cookies=self.__cookies)
        apiJson = json.loads(apiResponse.content)
        totalPageCount = apiJson["content"]["totalPages"]

        for i in range (0, totalPageCount):
            flag = False                                                                     # 반복 중단을 결정하는 flag
            requestURL = urlBase + "page={}&pageSize=10".format(i)                           # i번째 페이지 요청 URL
            apiResponse = requests.get(requestURL, headers=headers, cookies=self.__cookies)    # 요청해 데이터를 얻어옴
            apiJson = json.loads(apiResponse.content)                                        # apiResponse를를 딕셔너리화
            tempList = apiJson["content"]["data"]                                            # i번째 페이지의 치즈 리스트 
            for j in range(0, len(tempList)):                                                # i번째 페이지의 구매별 데이터
                tempDict = dict(tempList[j])                                                 # 데이터를 dict화                
                purchaseTime = time.mktime(time.strptime(tempDict["purchaseDate"], '%Y-%m-%d %H:%M:%S')) # 텍스트 형태의 시간을 time의 float로 만든다
                if purchaseTime < self.__lastRefreshTime: # 구매시간이 마지막 갱신시간보다 과거면 중단함
                    flag = True
                    break
                newPurchaseList.append(tempDict) #구매 기록을 신규 구매리스트에 추가
            if flag: # 검색 중단용
                break                                                # 전체 리스트에 append 
        newPurchaseList.reverse                                     # 순서 거꾸로 된 것 뒤집기
        self.__purchaseList += newPurchaseList                          #기존 구매리스트에 신규 구매스리스트 추가
        self.__lastRefreshTime = time.time()                          #마지막 검색 시간을 갱신


    def getEntireList(self):
        return self.__purchaseList
        

    def getTotalPrice(self):
        totalPrice = 0
        for purchase in self.__purchaseList:
            totalPrice += int(purchase["purchasePrice"])
        return totalPrice
    
    def exportAsFile(self,filePath=(os.getcwd() + "\\output.txt")):
        file = open(filePath, 'w')
        file.write(str(self.getEntireList()))
        file.close()

    





def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--NID_AUT", type=str, nargs=1, help="NID_AUT 수동입력", required=False)
    parser.add_argument("--NID_SES", type=str, nargs=1, help="NID_SES 수동입력", required=False)
    parser.add_argument("-f", "--file", nargs='?', default="", const="purchaseList.txt", type=str)
    parser.add_argument("-s", "--skip", action="store_true")
    args = parser.parse_args()

    cookies = dict()

    fileStore = False

    if args.skip:
        if (args.NID_AUT!=None and args.NID_SES!=None):
            cookies = { "NID_AUT":str(args.NID_AUT)[2:-2], "NID_SES":str(args.NID_SES)[2:-2]}
       
        if len(cookies) == 0:
            try:
                cookiePath = os.path.abspath(__file__)[:-20] + "cookie.txt"
                cookieFile = open(cookiePath, 'r')
                cookies = json.load(cookieFile)
                cookieFile.close()
            except:
                print("쿠키 파일 읽기 실패")
                return
    else:
        NID_AUT = input("NID_AUT의 값을 입력하세요 : ")
        NID_SES = input("NID_SES의 값을 입력하세요 : ")
        cookies = {"NID_AUT":NID_AUT, "NID_SES":NID_SES}
        fileStore = (True if input("전체 목록을 파일로 만드시겠습니까? (y/n) : ") == 'y' else False)
        

    if len(cookies) == 0:
        print("쿠기가 없습니다")
        return
    
    myAccount = CheeseAccount(NID_AUT=cookies["NID_AUT"], NID_SES=cookies["NID_SES"])
    print(str(myAccount.getTotalPrice()) + "원")

    try:
        cookiePath = os.path.abspath(__file__)[:-20] + "cookie.txt"
        cookieFile = open(cookiePath, 'w')
        json.dump(cookies,cookieFile)
    except:
        print("쿠키 파일 작성 실패")

    finally:
        cookieFile.close()

    if args.file != "" or fileStore:
        try:
            outputPath = os.path.abspath(__file__)[:-20] + (args.file if args.file != "" else 'purchaseList.txt')
            outputFile = open(outputPath, 'w', encoding="utf-8")
            outputFile.write('"{ list" : ' + str(myAccount.getEntireList()).replace('},','},\n ').replace('[', '[\n  ') + "}")
            outputFile.close()
        except:
            print("목록 파일 작성 실패")
        finally:
            outputFile.close()
        
    
        
    
if __name__ == "__main__":
    main()

