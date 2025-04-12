import time
import requests
import json
import os
import argparse
import sys

class purchaseList:

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
            apiResponse.raise_for_status()
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
        totalCheese = 0
        totalPrice = 0
        for purchase in self.__purchaseList:
            totalPrice += int(purchase["purchasePrice"])
            totalCheese += int(purchase["chargeAmount"])
        return [totalCheese,totalPrice]
    

class usedList:
    def __init__(self, NID_AUT, NID_SES):
        self.__cookies = {'NID_AUT': NID_AUT, 'NID_SES': NID_SES}
        self.__lastRefreshTime = 0     #검색 시간을 초기화
        self.__purchaseList = []        # 구매 리스트를 초기화
        self.refreshList()
    
    def refreshList(self):
        newPurchaseList = []

        #헤더와 기본 Url
        headers={"user-agent":"Mozilla/5.0 (compatible; exhentai-extractor;)", "referer":"https://game.naver.com/profile"}
        currentTime = time.strftime("%Y %m").split(" ")
        index = (int(currentTime[0]) - 2023)*12 + int(currentTime[1]) 

        for yearMonth in range(0,index):
            
            monthlyList = []
            requestURL = f"https://api.chzzk.naver.com/commercial/v1/product/purchase/history?page={0}&size=10&searchYear={yearMonth // 12 + 2023}&searchMonth={yearMonth % 12 + 1}"
            apiResponse = requests.get(requestURL, headers=headers, cookies=self.__cookies)
            if apiResponse.status_code != 200:
                continue
            apiJson = json.loads(apiResponse.content)
            totalPageCount = apiJson["content"]["totalPages"]
            print(f"{yearMonth // 12 + 2023}년 {yearMonth % 12 + 1:2}월 작업중...")
            time.sleep(2)
            for i in range (0, totalPageCount):                                                                  
                requestURL = f"https://api.chzzk.naver.com/commercial/v1/product/purchase/history?page={i}&size=10&searchYear={yearMonth // 12 + 2023}&searchMonth={yearMonth % 12 + 1}"
                apiResponse = requests.get(requestURL, headers=headers, cookies=self.__cookies)    
                apiJson = json.loads(apiResponse.content)                                        # apiResponse를를 딕셔너리화
                tempList = apiJson["content"]["data"]                                            # i번째 페이지의 치즈 리스트 
                for j in range(0, len(tempList)):                                                # i번째 페이지의 구매별 데이터
                    tempDict = dict(tempList[j])                                                 # 데이터를 dict화                
                    monthlyList.append(tempDict)
            if len(monthlyList) == 0:
                continue
            monthlyList.reverse()
            newPurchaseList += monthlyList                                    
        self.__purchaseList = newPurchaseList                          
        self.__lastRefreshTime = time.time()

    def getlistOfSent(self):
        streamerTuple = {}
        for lineData in self.__purchaseList:
            if not(lineData["channelName"] in streamerTuple):
                streamerTuple[lineData["channelName"]] = [lineData["payAmount"],1]
                continue
            streamerTuple[lineData["channelName"]][0] += lineData["payAmount"]
            streamerTuple[lineData["channelName"]][1] += 1
        return streamerTuple

    def getEntireList(self):
        return self.__purchaseList





def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--NID_AUT", type=str, nargs=1, help="NID_AUT 수동입력", required=False)
    parser.add_argument("--NID_SES", type=str, nargs=1, help="NID_SES 수동입력", required=False)
    parser.add_argument("-f", "--file", action="store_true")
    parser.add_argument("-s", "--skip", action="store_true")
    args = parser.parse_args()
    os.system('cls')
    print("ChzzkCheeseChaser는 치즈를 구매/사용용 총액을 구하는 프로그램 입니다.")
    print("치지직의 로그인이 필수이기 때문에 사용자의 쿠키가 필요합니다.")
    print("입력한 쿠키는 cookie.txt에만 저장되며 이 프로그램 실행시 자동로그인 외의 용도로 쓰이지 않습니다.")
    print("쿠키를 얻는 방법은 https://hajoung56.tistory.com/108 을 참고하세요\n")
    
    basePath = ""

    if getattr(sys, 'frozen', False):
        basePath = os.path.dirname(os.path.abspath(sys.executable))
    else:
        basePath = os.path.dirname(os.path.abspath(__file__))
    basePath += "\\"
    cookies = dict()

    fileStore = False

    if args.skip:
        if (args.NID_AUT!=None and args.NID_SES!=None):
            cookies = { "NID_AUT":str(args.NID_AUT)[2:-2], "NID_SES":str(args.NID_SES)[2:-2]}
       
        if len(cookies) == 0:
            try:
                cookiePath = basePath + "cookie.txt"
                cookieFile = open(cookiePath, 'r')
                cookies = json.load(cookieFile)
                cookieFile.close()
            except:
                print("쿠키 파일 읽기 실패")
                return
    else:
        try:
            cookiePath = basePath + "cookie.txt"
            cookieFile = open(cookiePath, 'r')
            cookies = json.load(cookieFile)
            cookieFile.close()
            print("cookie.txt에서 쿠키 기록을 읽었습니다.")
        except:
            print("쿠키 파일 읽기 실패")
        
        if len(cookies) == 0:
            NID_AUT = input("NID_AUT의 값을 입력하세요 : ")
            NID_SES = input("NID_SES의 값을 입력하세요 : ")
            cookies = {"NID_AUT":NID_AUT, "NID_SES":NID_SES}
        fileStore = (True if input("전체 목록을 파일로 만드시겠습니까? (y/n) : ") == 'y' else False)
        

    if len(cookies) == 0:
        print("쿠키가 없습니다")
        return
    
    try:
        os.system("cls")
        print("작업중입니다...")
        myAccount = purchaseList(NID_AUT=cookies["NID_AUT"], NID_SES=cookies["NID_SES"])
        purchase = myAccount.getTotalPrice()

        myDonation = usedList(NID_AUT=cookies["NID_AUT"], NID_SES=cookies["NID_SES"])
        donation = myDonation.getlistOfSent()
        cheeseSum = 0

        os.system('cls')
        print("치즈 구매 종합")
        print(f"총 구매 치즈 : {purchase[0]:10} 치즈")
        print(f"총 구매 금액 : {purchase[1]:10} 원\n")

        print("스트리머 도네 금액 리스트")
        maxLength = 0
        for name in donation.keys():
            if maxLength < len(name):
                maxLength = len(name)
        for name in donation.keys():
            print(f"{name + ' '*(maxLength-len(name))}\t: {donation[name][0]:9} 치즈 ({donation[name][1]:6} 회)")
            cheeseSum += donation[name][0]
        print(f"총 도네 치즈 \t: {cheeseSum:10} 치즈 ")
        print(f"남은 치즈   \t: {purchase[0]-cheeseSum:10} 치즈 \n")
    except:
        print("문제가 발생했습니다.")
        print("쿠키의 문제일 수 있으니 cookie.txt를 지우고 다시 한 번 시도해보세요")
        print("문제가 지속될 경우 https://github.com/wksksson1/ChzzkCheeseChaser/issues로 올려주세요")
    
    try:
        cookiePath = basePath + "cookie.txt"
        cookieFile = open(cookiePath, 'w')
        json.dump(cookies,cookieFile)
        print("쿠키 파일 저장에 성공했습니다.")
    except:
        print("쿠키 파일 작성 실패")


    finally:
        cookieFile.close()

    if args.file or fileStore:
        try:
            outputPath = basePath + 'purchaseList.txt'
            outputFile = open(outputPath, 'w', encoding="utf-8")
            outputFile.write('"{ list" : ' + str(myAccount.getEntireList()).replace('},','},\n ').replace('[', '[\n  ') + "}")
            outputFile.close()

            donationPath = basePath + 'donationList.txt'
            donationFile = open(donationPath, 'w', encoding="utf-8")
            donationFile.write('"{ list" : ' + str(myDonation.getEntireList()).replace('},','},\n ').replace('[', '[\n  ') + "}")
            donationFile.close()
            print("목록 파일 저장에 성공했습니다.")
        except:
            print("목록 파일 작성 실패")
        finally:
            outputFile.close()
    os.system("pause")
        
    
        
    
if __name__ == "__main__":
    main()

