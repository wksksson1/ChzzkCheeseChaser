import time
import requests
import json
import os
import argparse
import sys
from wcwidth import wcswidth

class ChzzkUser:
    def __init__(self, NID_AUT, NID_SES):
        self.__cookies = {'NID_AUT': NID_AUT, 'NID_SES': NID_SES}
        self.__donationLastRefreshTime = 0
        self.__purchaseLastRefreshTime = 0
        self.__donationList = []        # 후원 리스트를 초기화
        self.__purchaseList = []
        self.refreshDonationList()
        self.refreshPurchaseList()

    def refreshDonationList(self):
        #현재 시간과 로드해야 할 년/월 구하기
        currentTime = time.strftime("%Y %m").split(" ")
        index = (int(currentTime[0]) - 2023)*12 + int(currentTime[1]) 

        #헤더, 기본 URL
        headers={"user-agent":"Mozilla/5.0 (compatible; exhentai-extractor;)", "referer":"https://game.naver.com/profile"}
        urlBase="https://api.chzzk.naver.com/commercial/v1/product/purchase/history?"

        #임시 데이터 저장용
        tempDonationList = []

        #각 월마다의 치즈 리스트 구하기
        for loadTime in range(0,index):
            
            year = 2023 + loadTime // 12
            month = 1 + loadTime % 12

            #해당 달의 totalCount를 구하기 위해 1회 요청
            requestURL = urlBase + f"searchYear={year}&searchMonth={month}"
            apiResponse = requests.get(requestURL, headers=headers, cookies=self.__cookies)
            if apiResponse.status_code != 200: continue
            totalCount = json.loads(apiResponse.content)["content"]["totalCount"]
            
            print(f"{year:4}년 {month:2}월 : {totalCount:5}개")

            #실제로 도네된 경우가 없는 경우 건너뜀
            if totalCount == 0 : continue

            #실제 도네 리스트를 구함
            requestURL = urlBase + f"searchYear={year}&searchMonth={month}&size={totalCount}"
            apiResponse = requests.get(requestURL, headers=headers, cookies=self.__cookies)
            apiJson = json.loads(apiResponse.content)
            tempMonthList = reversed(list(apiJson["content"]["data"]))
            tempDonationList += tempMonthList
            time.sleep(1)



        #도네 리스트와 최종 갱신 시간을 수정
        self.__donationList = tempDonationList
        self.__donationLastRefreshTime = time.time()

    def getDonationList(self):
        return self.__donationList
    
    def refreshPurchaseList(self):
        #기본 URL, 헤더
        headers={"user-agent":"Mozilla/5.0 (compatible; exhentai-extractor;)", "referer":"https://game.naver.com/profile"}
        urlBase="https://api.chzzk.naver.com/commercial/v1/coin/history/purchase?"

        #totalCount를 구하기 위해 1회 요청
        requestURL = urlBase + f"page=0&pageSize=1"
        apiResponse = requests.get(requestURL, headers=headers, cookies=self.__cookies)
        totalCount = json.loads(apiResponse.content)["content"]["totalCount"]

        #실제 구매 리스트 
        requestURL = urlBase + f"page=0&pageSize={totalCount}"
        apiResponse = requests.get(requestURL, headers=headers, cookies=self.__cookies)
        apiJson = json.loads(apiResponse.content)
        tempPurchaseList = reversed(list(apiJson["content"]["data"]))
        
        #구매 리스트와 최종 갱신 시간을 갱신
        self.__purchaseList = list(tempPurchaseList)
        self.__purchaseLastRefreshTime = time.time()

    def getPurchaseList(self):
        return self.__purchaseList
    
    #구매한 금액, 치즈의 총액과 남은 치즈를 알려줍니다.
    def getTotalAmount(self):
        balanceCheese = 0
        totalCheese = 0 
        totalPurchase = 0
        for index in range(0, len(self.__purchaseList)):
            tempDict = dict(self.__purchaseList[index])
            balanceCheese += tempDict["balance"]
            totalCheese += tempDict["chargeAmount"]
            totalPurchase += int(tempDict["purchasePrice"])
        return {"balanceCheese":balanceCheese, "totalCheese":totalCheese, "totalPurchase":totalPurchase}


    def setCookies(self, NID_AUT, NID_SES):
        self.__cookies = {'NID_AUT': NID_AUT, 'NID_SES': NID_SES}
    
    def getCookies(self):
        return self.__cookies
    
    #스트리머별 도네 리스트를 딕셔너리로 반환해줍니다.
    def getDonationPerStreamer(self):
        streamerDonationDict = dict()
        for donation in self.__donationList: 
            tempDict = dict(donation)
            if not(tempDict["channelName"] in streamerDonationDict): 
                streamerDonationDict[tempDict["channelName"]] = [0,0]
            streamerDonationDict[tempDict["channelName"]][0] += int(tempDict["payAmount"])
            streamerDonationDict[tempDict["channelName"]][1] += 1
        return streamerDonationDict

def nameFormatter(text, size):
    addLen = size - wcswidth(text)
    formattedText = text + ' '*addLen
    return formattedText

def main():
    #기본 안내
    os.system('cls')
    print("ChzzkCheeseChaser는 치즈를 구매/사용 총액을 구하는 프로그램 입니다.")
    print("치지직의 로그인이 필수이기 때문에 사용자의 쿠키가 필요합니다.")
    print("입력한 쿠키는 cookie.txt에만 저장되며 이 프로그램 실행시 자동로그인 외의 용도로 쓰이지 않습니다.")
    print("쿠키를 얻는 방법은 https://hajoung56.tistory.com/108 을 참고하세요\n")
    
    #쿠키 값 입력받기
    NID_AUT = input("NID_AUT의 값을 입력하세요 : ")
    NID_SES = input("NID_SES의 값을 입력하세요 : ")
    
    #인스턴스 만들기
    user = ChzzkUser(NID_AUT=NID_AUT, NID_SES=NID_SES)
    
    totals = user.getTotalAmount()
    streamerDonations = user.getDonationPerStreamer()
    
    #이쁘게 출력하기 위한 글 사이즈 구하기
    os.system('cls')
    maxNameLength = 0
    maxIntegerLength = len(str(totals["totalPurchase"]))
    for name in list(streamerDonations.keys()) + ["총 구매 치즈", "총 구매 금액", "총 도네 치즈"]:
        if maxNameLength < len(name): maxNameLength = wcswidth(name)

    #개요 출력
    print("개요\n\n")
    print("구매 종합")
    print(nameFormatter('총 구매 치즈',maxNameLength)+ "\t: " + str(totals["totalCheese"]).rjust(maxIntegerLength) + " 치즈")
    print(nameFormatter('총 구매 금액',maxNameLength) + "\t: " + str(totals["totalPurchase"]).rjust(maxIntegerLength) + " 원")
    print("")
    print("소비 종합")
    for streamerName in list(streamerDonations.keys()):
        print(nameFormatter(streamerName,maxNameLength) + "\t: " + str(streamerDonations[streamerName][0]).rjust(maxIntegerLength) + " 치즈" + f"({streamerDonations[streamerName][1]:6} 회)")
    print(nameFormatter('총 도네 치즈',maxNameLength) + "\t: " + str(totals["totalCheese"] - totals["balanceCheese"]).rjust(maxIntegerLength) + " 치즈")
    print(nameFormatter('남은 치즈',maxNameLength) + "\t: " + str(totals["balanceCheese"]).rjust(maxIntegerLength) + " 치즈")


    #파일 저장용 프롬프트
    flag = input("\n\n개요와 구매 내역과 도네 내역을 저장하시겠습니까? (y/N) : ")
    if flag == 'y':
        #제작 위치를 실행 파일의 위치로 지정
        basePath = os.path.dirname(os.path.abspath(__file__)) + "\\"
        try:
            #구매파일 작성
            purchaseFile = open(basePath + 'purchaseList.txt', 'w', encoding="utf-8")
            purchaseFile.write('"{ list" : ' + str(user.getPurchaseList()).replace('},','},\n ').replace('[', '[\n  ') + "}")
            
            #도네파일 작성
            donationFile = open(basePath + 'donationList.txt', 'w', encoding="utf-8")
            donationFile.write('"{ list" : [\n')
            donationList = user.getDonationList()
            for index in range(0, len(donationList)-1):
                donationFile.write(str(donationList[index]) + ",\n")
            donationFile.write(str(donationList[-1]) + "]}")

            #인포 파일 작성
            infoFile = open(basePath + 'info.txt', 'w', encoding="utf-8")
            infoFile.write("실행시간 : " + str(time.strftime("%Y-%m-%d %H:%M:%S(%z)", time.localtime(time.time()))) + "\n")
            infoFile.write(nameFormatter('총 구매 치즈',maxNameLength)+ "\t: " + str(totals["totalCheese"]).rjust(maxIntegerLength) + " 치즈" + "\n")
            infoFile.write(nameFormatter('총 구매 금액',maxNameLength) + "\t: " + str(totals["totalPurchase"]).rjust(maxIntegerLength) + " 원" + "\n")
            infoFile.write("" + "\n")
            infoFile.write("소비 종합" + "\n")
            for streamerName in list(streamerDonations.keys()): 
                infoFile.write(nameFormatter(streamerName,maxNameLength) + "\t: " + str(streamerDonations[streamerName][0]).rjust(maxIntegerLength) + " 치즈" + f"({streamerDonations[streamerName][1]:6} 회)" + "\n")
            infoFile.write(nameFormatter('총 도네 치즈',maxNameLength) + "\t: " + str(totals["totalCheese"] - totals["balanceCheese"]).rjust(maxIntegerLength) + " 치즈" + "\n")
            infoFile.write(nameFormatter('남은 치즈',maxNameLength) + "\t: " + str(totals["balanceCheese"]).rjust(maxIntegerLength) + " 치즈" + "\n")
            print("파일 저장됨")
        except:
            pass
        finally:
            purchaseFile.close()
            donationFile.close()
            infoFile.close()
    print("종료하려면 아무 키나 누르세요")
    os.system("pause")


    





if __name__ == "__main__":
    main()