from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.chrome.options import Options as ChromeOptions

import time
import requests, json
import os

STEP_LIST = ["download", "transform", "format", "all"]

def getCharacterAudio(targetUrl: str, driver: webdriver.Remote, outputDir: str):

    # 清空outputDir
    if not os.path.exists(outputDir):
        os.makedirs(outputDir)
    else:
        for file in os.listdir(outputDir):
            os.remove(f"{outputDir}/{file}")

    driver.get(targetUrl)
    time.sleep(2)
    contents = getAudioText(driver)
    return contents
    
def getCharacterAudioDownloadPart(contents: list[list], outputDir: str):
    res = {}
    mp3Path = f"{outputDir}/mp3"
    if not os.path.exists(mp3Path):
        os.makedirs(mp3Path)
    for content in contents:
        outputFile = downloadAudioFiles(content, mp3Path)
        res[outputFile] = content[0]

    with open(f"{outputDir}/character_audio.txt", "w") as f:
        json.dump(res, f, indent=4, ensure_ascii=False)

    print(res)

def formatDataset(dirPath: str):
    # vocal_path|speaker_name|language|text
    absPath = os.getcwd() + "/" + dirPath + "/mp3"
    # 讀取json
    data = {}
    with open(f"{dirPath}/character_audio.txt", "r") as f:
        data = json.load(f)

    if data == {}:
        print("No data")
        return
    
    with open(f"{dirPath}/dataset.txt", "w") as f:
        for file in os.listdir(absPath):
            key = f"{dirPath}/mp3/{file}"
            if key not in data:
                continue
            f.write(f"{absPath}/{file}|furina|zh|{data[key]}\n")
    
    print("Dataset format done")
        

    
def getAudioText(driver: webdriver.Remote) -> list[list]:
    
    
    elements = driver.execute_script('return document.getElementsByClassName("resp-tabs-container")[0].getElementsByClassName("visible-md visible-sm visible-lg")')
    audioList = []
    for i in range(len(elements)):
        # content
        # document.getElementsByClassName("resp-tabs-container")[0].getElementsByClassName("visible-md visible-sm visible-lg")[0].getElementsByClassName("voice_text_chs vt_active")[0].textContent
        content = driver.execute_script(f'return document.getElementsByClassName("resp-tabs-container")[0].getElementsByClassName("visible-md visible-sm visible-lg")[{i}].getElementsByClassName("voice_text_chs vt_active")[0].textContent')
        audioUrl = driver.execute_script(f'return document.getElementsByClassName("resp-tabs-container")[0].getElementsByClassName("visible-md visible-sm visible-lg")[{i}].getElementsByTagName("audio")[0].getAttribute("src")')
        audioList.append([content, audioUrl])


    print(len(audioList))
    print(audioList[0])
    return audioList

def downloadAudioFiles(content: list, outputDir: str) -> str:

    contentText = content[0][:3]+ "OO" + content[0][-3:]
    audioUrl = content[1]
    outputFile = f"{outputDir}/{contentText}.mp3"
    downloadAudioFile(audioUrl, outputFile)
    return outputFile

def downloadAudioFile(url: str, outputFile: str):
    # 下載url 檔案並存闈 outputFile
    # 發送 HTTP 請求並下載檔案
    response = requests.get(url)

    # 將下載的內容保存到指定的檔案中
    with open(outputFile, 'wb') as file:
        file.write(response.content)

    print(f"檔案已下載至 {outputFile}")


def transformeMp3ToWav(inputFile: str):
    outputDir = "/".join(inputFile.split("/")[:-2]) + "/wav"
    if not os.path.exists(outputDir):
        os.makedirs(outputDir)
    outputFile = f"{outputDir}/{inputFile.split('/')[-1]}"
    outputFile = outputFile.replace(".mp3", ".wav")

    os.system(f"ffmpeg -i {inputFile} {outputFile}")


def downloadAudio(step: list = []):
    url = "https://wiki.biligame.com/ys/%E8%8A%99%E5%AE%81%E5%A8%9C%E8%AF%AD%E9%9F%B3"
    filePath = "tmpfile/audio/furina"

    if "download" in step or "all" in step:
        chromeOptions = ChromeOptions()
        browser = webdriver.Remote(
            command_executor='http://localhost:4444/wd/hub',
            options=chromeOptions
        )
        contents = []
        try :
            contents = getCharacterAudio(url, 
                            browser, filePath)
        except Exception as e:
            print(e)
        finally:
            browser.quit()

        getCharacterAudioDownloadPart(contents, filePath)

    if "transform" in step or "all" in step:
        wavPath = f"{filePath}/wav"
        if os.path.exists(wavPath):
            for file in os.listdir(wavPath):
                os.remove(f"{wavPath}/{file}")
        # list 
        for file in os.listdir(filePath + "/mp3"):
            transformeMp3ToWav(f"{filePath}/mp3/{file}")

    if "format" in step or "all" in step:
        formatDataset(filePath)

if __name__ == "__main__":
    # main()
    downloadAudio("transform")