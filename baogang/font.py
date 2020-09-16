import os.path

from fontTools.ttLib import TTFont


# 比较函数，用于对比两个字形列表的坐标信息是否相同
#（根据对字体文件的采样调研，认为只要x,y在一定的误差范围内就认为是相同的）
def comp(base_glyf, target_glyf):
    if len(base_glyf) != len(target_glyf):
        return 0
    else:
        mark = 1
        for i in range(len(base_glyf)):
            if abs(base_glyf[i][0] - target_glyf[i][0]) < 40 and abs(base_glyf[i][1] - target_glyf[i][1]) < 40:
                pass
            else:
                mark = 0
                break
        return mark


myfont1 = os.path.join(os.path.dirname(__file__), 'luntan_font1.ttf')
myfont2 = os.path.join(os.path.dirname(__file__), 'luntan_font2.ttf')

def get_map(target_font_file):
    font1 = TTFont(myfont1)
    # 手动确定一组编码和字符的正确对应关系
    uni_list = [
        'uniED82', 'uniECCF', 'uniED21', 'uniEC6D', 'uniEDAE', 'uniEE00', 'uniED4C', 'uniED9E', 'uniECEB', 'uniEC37', 'uniEC89', 'uniEDCA', 'uniED16', 
        'uniED68', 'uniECB5', 'uniED07', 'uniEC53', 'uniED94', 'uniEDE6', 'uniED32', 'uniEC7F', 'uniECD1', 'uniEC1D', 'uniEC6F', 'uniEDB0', 'uniECFC', 
        'uniED4E', 'uniEC9B', 'uniEDDB', 'uniEC39', 'uniED7A', 'uniEDCB', 'uniED18', 'uniEC65', 'uniECB6', 'uniEDF7', 'uniED44', 'uniED95'
    ]
    words = '二八六很呢七和高不五得近着了多十远上左好大长短坏是低三一小地九四更矮的右下少'
    words_list = list(words)
    
    font2 = TTFont(target_font_file)
    base_glyf_coordinates = []  # 存储38个字符的坐标信息
    for uni in uni_list:
        cdts = font1['glyf'][uni].coordinates
        base_glyf_coordinates.append(list(cdts))


    target_glyf_coordinates = []
    uni_list2 = font2.getGlyphOrder()[1:]
    for uni in uni_list2:
        cdts = font2['glyf'][uni].coordinates
        target_glyf_coordinates.append(list(cdts))

    font_map = {}
    for i, tgc in enumerate(target_glyf_coordinates):
        for j, bgc in enumerate(base_glyf_coordinates):
            if comp(tgc, bgc):
                font_map[uni_list2[i]] = words_list[j]
    return font_map


if __name__ == "__main__":    
    print(get_map(myfont2))      
    #分行打印出来，方便和FontCreator中进行比较确认
    # print(x_list[:16])
    # print(x_list[16:32])
    # print(x_list[-6:])
    # print(dict(zip(uni_list, words_list)))