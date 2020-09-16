import numpy

# import pytesseract
from PIL import ImageDraw, Image, ImageFont
from fontTools.ttLib import TTFont

# from 百度.百度文字识别 import get_word
from .baidu_ocr import get_word


def fontConvert(fontPath):  # 将web下载的字体文件解析，返回其编码和汉字的对应关系
    font = TTFont(fontPath)  # 打开字体文件
    # print(font)
    # print(font.getGlyphOrder()[1:])  # 列举出所有字体的uni码
    codeList = font.getGlyphOrder()[1:]
    # print(codeList)
    im = Image.new("RGB", (2000, 1500), (255, 255, 255))  # 创建一张画布   第二个参数为大小  第三个为颜色
    # im.show()
    dr = ImageDraw.Draw(im)  # 把im 上面的内容画上去
    # print(dr)
    font = ImageFont.truetype(fontPath, 50)  # 加载一个字体文件 并创建一个字体对象 并指定字体大小
    # print(font)
    count = 10
    arrayList = numpy.array_split(codeList, count)  # 将列表切分成15份，以便于在图片上分行显示
    # print(arrayList)
    unicode_list = ""
    for t in range(count):
        newList = [i.replace("uni", "\\u") for i in arrayList[t]]
        # print(newList)
        text = "".join(newList)
        # print(text)
        text = text.encode('utf-8').decode('unicode_escape')
        # print(text)
        unicode_list = unicode_list + text  # 这个是uncoide编码之后的字
        dr.text((50, 55 * t), text, font=font, fill="#000000")  # 用来画图的代码     t 才是真正画的图
        #  第一个参数  开始的位置 第二个参数 需要画的内容 第三个参数 字体    第四个 颜色
    # window
    im.save("./sss.jpg")
    # linux
    # im.save("/home/home/mywork/font/luntan/sss.jpg")
    unicode_list = list(unicode_list)
    # print(unicode_list)
    # window
    word_list = get_word("./sss.jpg")  # 百度
    # linux
    # word_list = get_word("/home/home/mywork/font/luntan/sss.jpg")  # 百度

    # im = Image.open("sss.jpg")  # 可以将图片保存到本地，以便于手动打开图片查看
    # im = im.convert('L')
    # 产生图片之后可以 百度文字识别来识别文字 提高准确率吧
    # result = pytesseract.image_to_string(im, lang="chi_sim")
    # print(result)
    # result = result.replace(" ", "").replace("\n", "")  # OCR识别出来的字符串有空格换行符
    # print(result)
    # codeList = [i.replace("uni", "&#x") + ";" for i in codeList]
    # return dict(zip(unicode_list, result))
    return dict(zip(unicode_list, word_list))


if __name__ == "__main__":
    # font=TTFont('./ccw.ttf')    #打开本地字体文件01.ttf
    # font.saveXML('./ccw.xml')
    fontDict = fontConvert("../text_dazhong1.ttf")
    # print("*" * 50)
    # print(fontDict)
