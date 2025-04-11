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
    #접속을 위한 쿠키, 헤더, 그리고 요청 URL
    NID_AUT="Your NID_AUT"
    NID_SES="Yout NID_SES"
    cookies = {'NID_AUT': NID_AUT, 'NID_SES': NID_SES}
    

    #치즈 구매 내역
    myAccount = CheeseAccount(NID_AUT, NID_SES)
    print(str(myAccount.getTotalPrice()) + "원")
    myAccount.exportAsFile()
    
if __name__ == "__main__":
    main()
    print('yay')

