#coding=utf-8

from PIL import Image , ImageDraw , ImageFont , ImageFilter

import json

from skimage import io
from scipy import ndimage
import numpy as np
import math
import random

import pdb
alpha = 2
'''

Input：
    Title , Subtitle , Images , size(这里的size表示图像的尺寸) , template json

"templets": {
    "count": 3,
    "balance": ,
    "align": ,
    "space": ,
    "interval":,
    id:1,  //模板个数
    sizew:4,
    sizey:3,
    "data": {
        "横轴平衡点": 0.5
        "纵轴平衡点": 0.5
        "左对齐比例": 0.5
        "上对齐比例": 0.5
        "元素间隔": 
        "title2SubTitle": 2
        "imageRatio": 0.5
        "titleRatio": 0.3
        "标题描述间隔": 
        "padding比例":
        "children": [
            {
              "type": "title",        
              "x": 30%,
              "y": 33%,
            },{
              "type": "subtitle",        
              "x": 30%,
              "y": 66%,
            },{
              "type": "image",       
              "x": 60%,
              "y": 50%,
            }
        ]
    }
}

output:
    images
'''
import time
from functools import wraps

def fn_timer(function):
    @wraps(function)
    def function_timer(*args , **kwargs):
        t0 = time.time()
        result = function(*args , **kwargs)
        t1 = time.time()
        print "Total time running %s: %s seconds" % (function.func_name , str(t1 - t0))
        return result
    return function_timer


from django.http import HttpResponse
from django.shortcuts import render_to_response

def hello(request):
    return render_to_response('index.html' , {'flag': True , 'op': False , 'balance': 0.0 , 'scale': 0.0 , 'space' : 0.0 , 'alignment': 0.0 , 'overlap': 0.0 , 'unity': 0.0})

cnt = 0
bestLayout = {}
background = "aliBanner/back.png"
def upload(request):
    #tmpRequest = request
    global cnt
    global bestLayout
    global background
    print request
    #assert False
    title = None
    subtitle = None
    width = 0
    height = 0
    images = []
    pos = None
    area = None
    balance = None
    scale = None
    space = None
    alignment = None
    overlap = None
    myLayout = {}

    postKeys = request.POST.keys()
    #print postKeys
    #assert False
    isError = False
    error = []
    if request.POST['title'] == "":
        isError = True
        error.append("please input the Title")
    else:
        title = request.POST['title']

    

    if request.POST['color'] == "":
    	isError = True
    	error.append("please select a color")
    	color = ""
    else:
    	color = request.POST['color']
    if 'subtitle' in postKeys:
        subtitle = request.POST['subtitle']
    else:
        subtitle = "  "
    
    
    title = title
    subtitle = subtitle
    
    

    if request.POST['w'] =="":
        isError = True
        error.append("please input the width")
    else:
        width = int(request.POST['w'])

    if request.POST['h'] == "":
        isError = True
        error.append("please input the height")
    else:
        height = int(request.POST['h'])
    #print 'title' , title
    #print 'subtitle' , subtitle
    #assert False
    #pos , area= merge_init(title , subtitle , images , (width , height) ,background ,  'templateM.json')
    
    Dis =[]

    '''
    for key , value in context.items():
        show.append(key + " : " + str(value))
        print key + " : " + str(value)
    '''
    print request.FILES.keys()
    #assert False
    if request.method == 'POST':
        if request.POST['submit'] == 'generate':
            cnt = 0
            keys = request.FILES.keys()
            if "image" not in keys:
                isError = True
                error.append("please upload your image")            	
            else:
                img = request.FILES['image']
                with open('aliBanner/image.png' , 'wb+') as des:
                    des.write(img.read())
                pic = Image.open('aliBanner/image.png')
                if "A" not in pic.mode:
                	isError = True
                	error.append("pic should have alpha channel")
                images = ['aliBanner/image.png']

            if 'background' in keys:
                back = request.FILES['background']
                with open('aliBanner/background.png' , 'wb+') as desBack:
                    desBack.write(back.read())
                pic = Image.open('aliBanner/background.png')
                #if "A" not in pic.mode:
                
                ##	isError = True
                #	error.append("the background picture should have alpha channel")

                background = 'aliBanner/background.png'
            else:
                background = 'aliBanner/back.png'
            #tmpRequest = request
            '''
            title = request.POST['title']
            subtitle = request.POST['subtitle']
            img = request.FILES['image']
            with open('aliBanner/image.png' , 'wb+') as des:
                des.write(img.read())
            title = title
            subtitle = subtitle
            images = ['aliBanner/image.png']
            width = int(request.POST['w'])
            height = int(request.POST['h'])
            # initialize.png
            pos , area , context = merge_init(title , subtitle , images , (width , height) , 'templateM.json')
            show =[]
            for key , value in context.items():
                show.append(key + " : " + str(value))
            '''
            if isError:
                return render_to_response("index.html" , {"isError": isError , 'error':error , 'flag': True ,  'color': color  , 'title': title , 'subtitle': subtitle ,  'width':width , 'height':height })
            else:
                merge_init(title , subtitle , images , color , (width , height) ,background ,  'templateM.json')
                return render_to_response('index.html' , {'isError':isError , 'color': color , 'error': error , 'op': False , 'flag': False , 'title': title , 'subtitle': subtitle ,  'width':width , 'height':height , 'balance': 0.0 , 'scale': 0.0 , 'space' : 0.0 , 'alignment': 0.0 , 'overlap': 0.0 , 'unity': 0.0})
        elif request.POST['submit'] == 'optimize':
            images = ['aliBanner/image.png']
            #background = 'aliBanner/background.png'
            if cnt == 0 :                               
                #if len(myLayout) == 0:
                pos , area = getElementInfo(images , (width , height) , template = 'templateM.json')
                '''
                imageWidth , imageHeight = getImageSize(Image.open(images[0]) , area)
                x , y = pos['image']
                w , h = area['image']
                diffW = (w - imageWidth) / 2
                diffH = (h - imageHeight) / 2
                pos['image'] = (int(x + diffW) , int(y + diffH))
                '''
                myLayout['pos'] = pos
                myLayout['area'] = area
                myLayout['size'] = (width , height)
                myLayout['title'] = title
                myLayout['subtitle'] = subtitle
                myLayout['images'] = images
                myLayout['elementGroup'] = [0 , 0 , -1]
                myLayout['color'] = color

                
            else:
                myLayout = bestLayout

            balance = float(request.POST['balance'])
            scale = float(request.POST['scale'])
            space = float(request.POST['space'])  
            alignment = float(request.POST['alignment'])
            overlap = float(request.POST['overlap'])
            unity = float(request.POST['unity'])


            '''
            # 风格方面的东西，之后再考虑
            #final.png
            newWeights = NIO(myLayout , getWeight(balance , scale , space , alignment , overlap) , Dis, elements , elementSize, background)
            # 当前生成的layout已经算是一个模板，代入NIO的时候学习出这个模板所对应的权重，然后需要用这个权重去优化另外一种无序的layout
            userLayout = copy.deepcopy(myLayout)
            
            # 对userlayout作为修改，此处下次应该做成一个接口
            pos = userLayout['pos']
            for key , value in pos.items():
                pos[key] = (random.randint(0 , 100) , value[1])
            userLayout['pos'] = pos
            initialize(background , userLayout['pos'] , userLayout['area'] , userLayout['title'] , userLayout['subtitle'] , userLayout['images'] , userLayout['size'] , 'user.png')
            '''
            bestLayout = optimize(myLayout , 50 , getWeight(balance , scale , space , alignment , overlap) , Dis , background)
            cnt += 1
            #optimize(myLayout , 51 , getWeight() , Dis , elements , elementSize, background)
            return render_to_response('index.html' ,{'color':color , 'op': True , 'flag': False , 'title': title , 'subtitle': subtitle , 'width':width , 'height':height  , 'balance': balance , 'scale': scale , 'space' : space , 'alignment': alignment , 'overlap': overlap , 'unity': unity})
       


# filename = *.png mode = 'RGBA'
def rgba2Gray(filename , savepath):
    png = Image.open(filename)
    png.load()

    background = Image.new('RGB' , png.size , (255 , 255 , 255))
    background.paste(png , mask = png.split()[3])

    background = background.convert('L')
    background.save(savepath)


# filename = *.jpg , mode = 'L'
def getGravityCenter(filename):
    im = io.imread(filename)
    reguler = np.ones(im.shape) * 255
    imageGrayArray = (reguler - im) * 1.0 / 255

    return tuple(reversed(ndimage.measurements.center_of_mass(imageGrayArray)))

#@fn_timer
def getBalanceGravityCenter(size , elements , elementSize , elementType , elementLine , elementGroup , imageElement):
    gravity = []
    center = []
    for item in imageElement:
        back = Image.new('RGB' , item.size , (255 ,255 , 255))
        back.paste(item , mask = item.split()[3])
        back = back.convert('L')
        back = np.array(back)
        reguler = np.ones(back.shape) * 255
        imageGrayArray = (reguler - back) * 1.0 / 255
        center.append(tuple(reversed(ndimage.measurements.center_of_mass(imageGrayArray))))
        gra = imageGrayArray.sum() * 1.0 / (imageGrayArray.shape[0] * imageGrayArray.shape[1])
        gravity.append(gra)


    sumGravity = sum(gravity)
    for idx in range(len(elements)):
        x , y = center[idx]
        x += elements[idx][0]
        y += elements[idx][1]
        center[idx] = (x , y)

    sumXAxis = 0.0
    sumYAxis = 0.0
    for item in range(len(center)):
        weight = gravity[item]
        sumXAxis += weight * center[item][0]
        sumYAxis += weight * center[item][1]


    x_axis = sumXAxis * 1.0 / sumGravity
    y_axis = sumYAxis * 1.0 / sumGravity

    d = dis((x_axis , y_axis) , (size[0] * 1.0 / 2 , size[1] * 1.0 / 2) , size)

    E_balance = sigmod(d , alpha)

    res = {}
    res['balance'] = E_balance

    return res


# Json 返回模板的参数(字典)
def getTemplateInfo(filename = 'templateM.json' , templateId = '1'):
    f = file(filename)
    s = json.load(f)
    #print templateId
    #print s.keys()
    return s[templateId]


# 筛选模板,返回模板id
def templateSelect(size , Images):
    ratioCanvas = size[0] * 1.0 / size[1]
    image = Image.open(Images[0])
    imageRatio = image.size[0] * 1.0 / image.size[1]
    templateId = '1'
    if ratioCanvas > 0.67 and ratioCanvas < 2:
        if imageRatio >0.67 and imageRatio < 2:
            templateId = '2'
        elif imageRatio < 0.67:
            templateId = '3'
        elif imageRatio > 2:
            templateId = '1'
    elif ratioCanvas > 2:
        templateId = '4'
    elif ratioCanvas < 0.67:
        templateId = '6'

    #templateId = '1'
    return templateId




'''
def getElementInfo(data , size):
    #elemNum = templateInfo['count']
    children = data['children']
    sumRatio = 0.0

    for item in children.values():
        sumRatio += item["ratio"]

    area = {}
    pos = {}
    clsize = data['clsize']
    elementArea = size[0] * size[1] * clsize

    for key , value in children.items():
        area[key] = (elementArea * value['ratio']) / sumRatio
        pos[key] = (size[0] * value['x'] , size[1] * value['y'])

    return area , pos
'''



# 计算重心的差距，并调整pos
# Image 参数应该是路径名字
def getStartPos(pos , area , title , Subtitle , Images):
    # title
    font_size = getFontSize(area['title'] , title)
    font = ImageFont.truetype('msyh.ttf' , font_size)

    img = Image.new('RGBA' , font.getsize(title))
    Draw = ImageDraw.ImageDraw(img , 'RGBA')
    Draw.text((0 , 0) , title , fill = 'black' , font = font)
    img.save('title.png')
    rgba2Gray('title.png' , 'title.jpg')
    titlePos = getGravityCenter('title.jpg')

    # 假设所有图片初始的时候都在(0,0)点
    #print pos['title']
    #print pos['detail']
    #print pos['image']

    #titleStartPos = (int(math.fabs((titlePos[0] - pos['title'][0]))) ,int(math.fabs((titlePos[1] - pos['title'][1]))))
    titleStartPos = (int(pos['title'][0] - titlePos[0]) , int(pos['title'][1] - titlePos[1]))

    # Subtitle
    font_size = getFontSize(area['detail'] , Subtitle)
    font = ImageFont.truetype('msyh.ttf' , font_size)
    img = Image.new('RGBA' , font.getsize(Subtitle))
    Draw = ImageDraw.ImageDraw(img , 'RGBA')
    Draw.text((0 , 0) , Subtitle , fill = 'black' , font = font)
    img.save('detail.png')
    rgba2Gray('detail.png' , 'detail.jpg')
    SubtitlePos = getGravityCenter('detail.jpg')

    #SubtitleStartPos = (int(math.fabs((SubtitlePos[0] - pos['detail'][0]))) , int(math.fabs((SubtitlePos[1] - pos['detail'][1]))))
    SubtitleStartPos = (int(pos['detail'][0] - SubtitlePos[0]) , int(pos['detail'][1] - SubtitlePos[1]))

    # Image
    pic = Image.open(Images)
    picSize = getImageSize(Images , area)
    img = Image.new('RGBA' , picSize)
    
    pic = pic.resize(picSize , Image.ANTIALIAS)
    img.paste(pic , (0 , 0))
    img.save('context.png')
    rgba2Gray('context.png' , 'context.jpg')
    imagePos = getGravityCenter('context.jpg')

    #imageStartPos = (int(math.fabs((imagePos[0] - pos['image'][0]))) , int(math.fabs((imagePos[1] - pos['image'][1]))))
    imageStartPos = (int(pos['image'][0] - imagePos[0]) , int(pos['image'][1] - imagePos[1]))

    #print titlePos , SubtitlePos , imagePos

    return titleStartPos , SubtitleStartPos , imageStartPos


def getImageSize(Images , area):
    pic = Image.open(Images)
    ratio = pic.size[0] * 1.0 / pic.size[1]
    y = (area['image'] * 1.0 / ratio) ** 0.5
    x = y * ratio

    return (int(x) , int(y))








# image = Image.open('*.png')
def getPosAxis(image , startPos):
    w , h = image.size
    xmin , ymin = startPos
    xmax = xmin + w
    ymax = ymin + h

    return (xmin , xmax , ymin , ymax)



def sigmod(x , alpha):
    return math.atan(x * alpha) * 1.0 / math.atan(alpha)


def C(d):
    return 5.0 * math.atan(d * 1.0 / 0.015)
'''
Aligment 
参数 ，startPos

需要求得的参数矩阵
针对每一种对齐方式，要求矩阵A
B是两个元素之间的元素个数

# alignments types:
    left
    X-Center
    Right Top
    Y_Center
    Bottom
I = A & B

d_ij indicates the distance
between two elements i and j depending on the alignment
type using element’s bounding boxes. 

I = A 没有实现B
E_align_left
E_misalign_left
'''
types = ["left" , "xcenter" , "right" , "top" , "ycenter" , "bottom"]
def distance(alignType , elements , elementSize , a , b):
    if alignType == types[0]:
        d = math.fabs(elements[a][0] - elements[b][0])

    elif alignType == types[1]:
        d = math.fabs((elements[a][0] + elementSize[a][0] * 0.5) - (elements[b][0] + elementSize[b][0] * 0.5))

    elif alignType == types[2]:
        d = math.fabs((elements[a][0] + elementSize[a][0]) - (elements[b][0] + elementSize[b][0]))

    elif alignType == types[3]:
        d = math.fabs(elements[a][1] - elements[b][1])

    elif alignType == types[4]:
        d = math.fabs((elements[a][1] + elementSize[a][1] * 0.5) - (elements[b][1] + elementSize[b][1] * 0.5))

    elif alignType == types[5]:
        d = math.fabs((elements[a][1] + elementSize[a][1]) - (elements[b][1] + elementSize[b][1]))
    else:
        return None

    return d

def ATypeCalc(alignType , elements , elementSize):    
    threshold = 0.065
    A = np.zeros((len(elements) , len(elements)))

    for i in range(len(elements)):
        for j in range(len(elements)):
            d = distance(alignType , elements , elementSize , j , i)
            if d is not None and d < threshold:
                A[i , j] = 1

    '''
    if alignType == types[0]:
        for i in range(len(elements)):
            for j in range(len(elements)):
                d = distance(alignType , elements , elementSize , j , i)
                d = math.fabs(elements[j][0] - elements[i][0])
                if d < threshold:
                    A[i , j] = 1
    elif alignType == types[1]:
        for i in range(len(elements)):
            for j in range(len(elements)):
                d = math.fabs((elements[j][0] + elementSize[j][0] * 0.5) - (elements[i][0] + elementSize[i][0] * 0.5))
                if d < threshold:
                    A[i , j] = 1
    elif alignType == types[2]:
        for i in range(len(elements)):
            for j in range(len(elements)):
                d = math.fabs((elements[j][0] + elementSize[j][0]) - (elements[i][0] + elementSize[i][0]))
                if d < threshold:
                    A[i ,j] = 1
    elif alignType == types[3]:
        for i in range(len(elements)):
            for j in range(len(elements)):
                d = math.fabs(elements[j][1] - elements[i][1])
                if d < threshold:
                    A[i , j] = 1
    elif alignType == types[4]:
        for i in range(len(elements)):
            for j in range(len(elements)):
                d = math.fabs((elements[j][1] + elementSize[j][1] * 0.5) - (elements[i][1] + elementSize[i][1] * 0.5))
                if d < threshold:
                    A[i , j] = 1
    elif alignType == types[5]:
        for i in range(len(elements)):
            for j in range(len(elements)):
                d = math.fabs((elements[j][1] + elementSize[j][1]) - (elements[i][1] + elementSize[i][1]))
                if d < threshold:
                    A[i , j] = 1
    else:
        return None
    '''

    return A







#alignType = types = ["left" , "xcenter" , "right" , "top" , "ycenter" , "bottom"]
# Output 针对每一个对齐类型返回两个energy term ,一共是12个energyterm
'''
def alignCalc(titleInfo , subtitleInfo , imageInfo):
    #titleStartPos , SubtitleStartPos , imageStartPos = getStartPos(pos , area , title , subtitle ,images)
    titleStartPos , titleSize = titleInfo
    SubtitleStartPos , subtitleSize = subtitleInfo
    imageStartPos , imageSize = imageInfo

    
    # Left
    elements = [titleStartPos , SubtitleStartPos ,  imageStartPos]
    elementSize = [titleSize.size , subtitleSize.size , imageSize.size]
'''
#@fn_timer
def alignCalc(size , elements , elementSize , elementType , elementLine , elementGroup , imageElement):  

    '''
    B = np.zeros((len(elements) , len(elements)))

    # 使用矩形区域的方法，但是要判断两个元素的位置来做不同的区域
    cnt = 0
    for i in range(len(elements)):
        for j in range(len(elements)):
            if (elements[i][1] < elements[j][1]) and (elements[j][1] > (elements[i][1] + elementSize[i].size)):
                pass
            elif elements[i][1] > elements[j][1] and ():
                pass
            else:
                pass

            for k in range(len(elements)):
    '''
    n = len(elements)
    
    E_align = []

    for item in range(len(types)):
        sum = 0.0
        for i in range(len(elements)):
            for j in range(len(elements)):
                if i != j :
                    A = ATypeCalc(types[item] , elements , elementSize)
                    I = A
                    sum += I[i , j]
            #print I
            sum += 1
            #print sum
        #print sum 
        tmp =  sum * 1.0 / (n ** 2)
        tmp = -1.0 * sigmod(tmp , alpha)
        E_align.append(tmp)

    

    sum_mis = 0
    for item in range(3):
        for i in range(len(elements)):
            for j in range(len(elements)):
                A = ATypeCalc(types[item] , elements , elementSize)
                I = A
                d = distance(types[item] , elements , elementSize , j , i)
                sum_mis += I[i , j] * C(d)

    E_misalign_x = sum_mis * 1.0 / (3 * n**2)


    for item in range(3 , 6):
        for i in range(len(elements)):
            for j in range(len(elements)):
                A = ATypeCalc(types[item] , elements , elementSize)
                I = A
                d = distance(types[item] , elements , elementSize , j , i)
                sum_mis += I[i , j] * C(d)
    E_misalign_y = sum_mis * 1.0 / (3 * n**2)


    res = {}
    for item in range(len(types)):
        res[types[item]] = E_align[item]
    res['misalignx'] = E_misalign_x
    res['misaligny'] = E_misalign_y
    # Grouping 

    return res

# ==================White Space

# 返回E_white_space
#@fn_timer
def whiteSpace(size , elements , elementSize , elementType , elementLine , elementGroup , imageElement ):
    #pdb.set_trace()
    sum = size[0] * size[1]
    for item in range(len(elements)):
        sum -= elementSize[item][0] * elementSize[item][1]

    sum = sum * 1.0 / (size[0] * size[1])

    E_white_space =  -1.0 * sigmod(sum , alpha)
    res = {}
    res['whiteSpace'] = E_white_space
    return res


#pixel = (x , y)
def dis(x , y , size):
    return math.sqrt(((x[0] - y[0])* 1.0 / size[0]) ** 2 + ((x[1] - y[1]) * 1.0 / size[1]) **2)

def euclideanDis(pixel , element , elementSize , size):
    #print pixel , element
    d = 0.0
    if pixel[0] < element[0] and pixel[1] < element[1]:
        d = dis(pixel , element , size)
    elif pixel[0] > (element[0] + elementSize[0]) and pixel[1] < element[1]:
        d = dis(pixel , (element[0] + elementSize[0] , element[1]) , size)
    elif pixel[0] < element[0] and pixel[1] > (element[1] + elementSize[1]):
        d = dis(pixel , (element[0] , element[1] + elementSize[1]) , size)
    elif pixel[0] > (element[0] + elementSize[0]) and pixel[1] > (element[1] + elementSize[1]):
        d = dis(pixel , (element[0] + elementSize[0] , element[1] + elementSize[1]) , size)
    elif pixel[0] >= element[0] and pixel[0] <= (element[0] + elementSize[0]) and pixel[1] <= element[1]:
        d = (element[1] - pixel[1]) * 1.0 / size[1]
    elif pixel[0] >= element[0] and pixel[0] <= (element[0] + elementSize[0]) and pixel[1] >= (element[1] + elementSize[1]):
        d = (pixel[1] - (element[1] + elementSize[1]))  * 1.0 / size[1]
    elif pixel[1] >= element[1] and pixel[1] <= (element[1] + elementSize[1]) and pixel[0] <= element[0]:
        d = (element[0] - pixel[0]) * 1.0 / size[0]
    elif pixel[1] >= element[1] and pixel[1] <= (element[1] + elementSize[1]) and pixel[0] >= (element[0] + elementSize[0]):
        d = (pixel[0] - element[0]) * 1.0 / size[0]
    else:
        return 0


    return d


def ifScan(pixel , elements , elementSize):
    flag = True

    for item in range(len(elements)):
        if (pixel[0] >= elements[item][0]) and (pixel[0] <= (elements[item][0] + elementSize[item][0])) and (pixel[1] >= elements[item][1]) and (pixel[1] <= (elements[item][1] + elementSize[item][1])):
            flag = False

    return flag


# ndimage.distance_transform_edt(a)
#@fn_timer
def spread(size , elements , elementSize , elementType , elementLine , elementGroup , imageElement):
    img = Image.new('L' , size , 255)
    for item in range(len(elements)):
        img.paste(0 , (elements[item][0] , elements[item][1] , elements[item][0] + elementSize[item][0] , elements[item][1] + elementSize[item][1]))

    #img.show()

    img = np.array(img)
    #reguler = np.ones(img.shape) * 255
    img = img / 255

    distanceMap = ndimage.distance_transform_edt(img)
    #print distanceMap
    distanceMap = distanceMap / 255

    E_spread = distanceMap.sum() * 1.0 / (size[0] * size[1])
    E_spread = sigmod(E_spread , alpha)

    res = {}
    res['spread'] = E_spread

    return res
'''
# elements 存放的是每个元素的起始位置
def spread(size , elements , elementSize , Dis):
    sum = 0
    min = 10000000000.0
    for i in range(size[1]):
        for j in range(size[0]):
            min = 10000000000.0
            if ifScan((i , j) , elements , elementSize): #保证不会扫到元素内部，只扫描除元素的空白处
                for item in range(len(elements)):
                    #d = euclideanDis((j , i) , elements[item] , elementSize[item] , size)
                    d = Dis[item][i , j]
                    #d = d *
                    if min > d:
                        min = d
                #print min
                sum += min
    #print sum


    E_spread = sum * 1.0 / (size[0] * size[1])
    E_spread = sigmod(E_spread , alpha)

    return E_spread
'''
'''
def elementDis(size , elements , elementSize , Distance):
    Dis = np.zeros((len(elements) , len(elements)))
    min = 10000000000.0



    for a in range(len(elements)):
        for b in range(len(elements)):
            if a == b :
                continue
            min = 10000000000.0            
            for i in range(size[1]):                
                for j in range(size[0]):
                    #d1 = euclideanDis((j , i) ,  elements[a] , elementSize[a] , size)
                    #d2 = euclideanDis((j , i) , elements[b] , elementSize[b] , size)
                    d1 = Distance[a][i , j]
                    d2 = Distance[b][i , j]
                    #print d1 , d2
                    #print d1 , d2
                    d = math.sqrt(0.5 * ((d1 * 1.0) ** 2 + (d2 * 1.0) ** 2))
                    #print d , d1 , d2 , i , j
                    #assert d != 0
                    #print d
                    if min > d:
                        min = d
            #print min
            Dis[a , b] = min

    return Dis
'''
#@fn_timer
def elementDis(size , elements , elementSize):
    distanceMap = []
    mask = Image.new('L' , size , 1)
    for item in range(len(elements)):
        img = Image.new('L' , size , 255)
        img.paste(0 , (elements[item][0] , elements[item][1] , elements[item][0] + elementSize[item][0] , elements[item][1] + elementSize[item][1]))
        mask.paste(255 , (elements[item][0] , elements[item][1] , elements[item][0] + elementSize[item][0] , elements[item][1] + elementSize[item][1]))
        img = np.array(img)
        img = img / 255
        disMap = ndimage.distance_transform_edt(img)
        distanceMap.append(disMap + 1)

    mask = np.array(mask)
    Dis = np.zeros((len(elements) , len(elements)))
    for i in range(len(distanceMap)):
        for j in range(len(distanceMap)):
            if i == j:
                Dis[i , j] = 0
                continue
            tmp = distanceMap[i] ** 2 + distanceMap[j] ** 2
            tmp = tmp * 0.5
            tmp = np.sqrt(tmp)
            tmp = tmp * mask
            Dis[i , j] = tmp.min()

    #print Dis
    return Dis


#@fn_timer
def dist(size , elements , elementSize , elementType , elementLine , elementGroup , imageElement):
    min = 10000000000.0
    sum = 0.0
    numSum = 0.0
    #Dis = elementDis(size , elements , elementSize , Distance)
    Dis = elementDis(size , elements , elementSize)
    #print Dis
    for i in range(len(elements)):
        min = 10000000000.0
        for j in range(len(elements)):
            if i != j:
                d = Dis[i , j]
                if d < min:
                    min = d
                #print d ,min
        #print min
        sum = sigmod(min , alpha)
        numSum += (1 - sum)

    E_dist = numSum * 1.0 / len(elements)
    res = {}
    res['dist'] = E_dist

    return res


'''
# 重叠问题没有解决（元素之间的是否还有其他元素）
def textSepVar(elements , elementSize , elementType):
    Dis = np.zeros((len(elements) , len(elements)))

    for i in range(len(elements)):
        if elementType[i] == 'text':
            for j in range(len(elements)):
                if elementType[j] == "text":
                    if (elements[j][0] >= (elements[i][0] - elementSize[j][0])) and (elements[j][0] < (elements[i][0] + elementSize[i][0])):
                        

                        if elements[i][1] > elements[j][1]:
                            for k in range(len(elements)):
                                if elementType[k] == 'text' and (elements[j][0] >= (elements[i][0] - elementSize[j][0])) and (elements[j][0] < (elements[i][0] + elementSize[i][0])):
                        else:

                        if no element:
                            
                        d = math.fabs(elements[i][1] + 0.5 * elementSize[i][1] - (elements[j][1] + 0.5 * elementSize[j][1])) - 0.5 * elementSize[i][1] - 0.5 * elementSize[j][1]
                        Dis[i , j] = d
    
    for i in range(len(elements)):
        if elementType[i] == "text":
            for j in range(len(elements)):
                if elements[j]
    




    return E_tetxSepVar

'''
#@fn_timer
def margin(size , elements , elementSize , elementType , elementLine , elementGroup , imageElement):
    # 0 , 1 , 2 , 3代表 left , top , right , bottom
    M = np.zeros((len(elements) , 4))

    for i in range(len(elements)):
        M[i , 0] = elements[i][0] * 1.0 / (size[0] * 0.5)
        M[i , 1] = elements[i][1] * 1.0 / (size[1] * 0.5)
        M[i , 2] = (size[0] - (elements[i][0] + elementSize[i][0])) / (size[0] * 0.5)
        M[i , 3] = (size[1] - (elements[i][1] + elementSize[i][1])) / (size[1] * 0.5)

    sum_text = 0.0
    sum_graphic = 0.0
    for i in range(len(elements)):
        min = 10000000000.0
        for j in range(4):
            d = M[i , j]
            if d < min:
                min = d
        #print min
        if elementType[i] == 'text':
            #print sum_text
            sum_text += (1 - sigmod(min , alpha))

        else:
            sum_graphic += (1 - sigmod(min , alpha))

    #print sum_text ,sum_graphic
    E_margin_text = sum_text * 1.0 / len(elements)
    E_margin_graphic = sum_graphic * 1.0 / len(elements)

    res = {}
    res['textMargin'] = E_margin_text
    res['graphicMargin'] = E_margin_graphic


    return res


# 文本元素有个行数参数 , elementLine 中，在录入的时候，会把对应的元素的行数录入，如果是图片元素，则为-1
#@fn_timer
def textSize(size , elements , elementSize , elementType , elementLine , elementGroup , imageElement):
    countText = 0
    countGra = 0
    sum_text = 0.0
    sum_graphic = 0.0
    tau_s = 1
    for i in range(len(elements)):
        if elementType[i] == 'text':
            countText += 1
            M = tau_s * elementSize[i][1] * 1.0 / (elementLine[i] * size[1])
            sum_text += sigmod(M , alpha)
        else:
            countGra += 1
            M = elementSize[i][1] * elementSize[i][0] * 1.0 / (size[0] * size[1])
            sum_graphic += sigmod(M , alpha)

    # 判断是否有文本或者图片元素
    if countText == 0:
        print "there is no text element"
        E_textSize = 0
    else:
        E_textSize = -1.0 * sum_text / countText

    if countGra == 0:
        print "there is no graphic element"
        E_graphic = 0
    else:
        E_graphic =  -1.0 * sum_graphic / countGra

    res = {}
    res['textSize'] = E_textSize
    res['graphicSize'] = E_graphic

    return res

#@fn_timer
def textVar(size , elements , elementSize , elementType , elementLine , elementGroup , imageElement):
    M_text = []
    M_graphic = []
    tau_s = 1
    for i in range(len(elements)):
        if elementType[i] == 'text':
            M = tau_s * elementSize[i][1] * 1.0 / (elementLine[i] * size[1])
            M_text.append(M)
        else:
            M = elementSize[i][1] * elementSize[i][0] * 1.0 / (size[0] * size[1])
            M_graphic.append(M)

    arr_text = np.array(M_text)
    arr_graphic = np.array(M_graphic)

    E_textVar = sigmod(np.var(arr_text) , alpha)
    E_graphic = sigmod(np.var(arr_graphic) , alpha)
    res = {}
    res['textVar'] = E_textVar
    res['graphicVar'] = E_graphic
    return res


# 计算值为0 ，不知道是否有问题
#@fn_timer
def minTextSize(size , elements , elementSize , elementType , elementLine , elementGroup , imageElement):
    tau_text = 0.0275
    tau_graph = 0.04
    sum_text = 0.0
    sum_graphic = 0.0
    tau_s = 1

    for i in range(len(elements)):
        if elementType[i] == 'text':
            M_text = tau_s * elementSize[i][1] * 1.0 / (elementLine[i] * size[1])
            d = tau_text - M_text
            res = max(d , 0)
            sum_text += res
        else:
            M_gra = elementSize[i][1] * elementSize[i][0] * 1.0 / (size[0] * size[1])
            d = tau_graph - M_gra
            res = max(d , 0)
            sum_graphic += res

    E_minTextSize = sum_text
    E_minGraphicSize = sum_graphic

    res = {}
    res['minTextSize'] = E_minTextSize
    res['minGraphicSize'] = E_minGraphicSize


    return res


# 计算文本元素与背景的颜色差异
# background  = Image.open("*.png") 相当于一个图片以铺满的形式放在画布上
# 这里要先转换为一张灰度图，不然有三个通道很难抉择 , 这里的background是经过resize到这个画布的
# imageElement 里的也必须是灰度图才能用
'''
png = Image.open(filename)
    png.load()

    background = Image.new('RGB' , png.size , (255 , 255 , 255))
    background.paste(png , mask = png.split()[3])

    background = background.convert('L')
'''
#@fn_timer
def textContrast(size , elements , elementSize , elementType , elementLine , elementGroup , imageElement , back):
    background = Image.new('RGB' , back.size , (255 , 255 , 255))
    background.paste(back , mask = back.split()[3])
    background = background.convert('L')

    #rgba2Gray(background , "background.jpg")
    #background = Image.open("background.jpg")
    #background = Image.open("background.jpg") # 转换成矩阵，方便做差值
    #background = background.resize(size , Image.ANTIALIAS)
    #background = np.array(background)
    M_con = []
    cnt = 0
    different = []
    mean = 0.0

    imageGray = []

    # 灰度处理
    for item in range(len(imageElement)):
        image = Image.new('RGB' , imageElement[item].size , (255 , 255 , 255))
        image.paste(imageElement[item] , mask = imageElement[item].split()[3])
        image = image.convert('L')
        imageGray.append(image)




    for item in range(len(elements)):
        if elementType[item] != 'text':
            continue
        cnt += 1
        box = (elements[item][0] , elements[item][1] , elements[item][0] + elementSize[item][0] , elements[item][1] + elementSize[item][1])
        backCrop = background.crop(box)
        #backCrop.show()
        backCrop = np.array(backCrop)
        #print backCrop.shape
        image = np.array(imageGray[item])
        #print image.shape
        for i in range(image.shape[1]):
            mean = 0.0
            for j in range(image.shape[0]):
                diff = math.fabs(int(image[j , i]) - int(backCrop[j , i]))
                mean += diff
            mean = mean * 1.0 / image.shape[0]
            mean  = mean * 1.0 / 255
            different.append(mean)

        different = sorted(different , reverse = True)
        #print different
        limit = int(len(different) * 0.2)
        m = 0.0
        for item in different[:limit]:
            m += item
        m = m * 1.0 / limit
        M_con.append(m)

    sum = 0.0
    for item in M_con:
        sum += sigmod(item , alpha)
    E_textContrast = sum * 1.0 / cnt

    res = {}
    res['textContrast'] = E_textContrast

    return res



def if_intersection(xmin_a, xmax_a, ymin_a, ymax_a, xmin_b, xmax_b, ymin_b, ymax_b):
    if_intersect = False
    if xmin_a < xmax_b <= xmax_a and (ymin_a < ymax_b <= ymax_a or ymin_a <= ymin_b < ymax_a):
        if_intersect = True
    elif xmin_a <= xmin_b < xmax_a and (ymin_a < ymax_b <= ymax_a or ymin_a <= ymin_b < ymax_a):
        if_intersect = True
    elif xmin_b < xmax_a <= xmax_b and (ymin_b < ymax_a <= ymax_b or ymin_b <= ymin_a < ymax_b):
        if_intersect = True
    elif xmin_b <= xmin_a < xmax_b and (ymin_b < ymax_a <= ymax_b or ymin_b <= ymin_a < ymax_b):
        if_intersect = True
    else:
        return False

    '''
    if if_intersect == True:
        x_sorted_list = sorted([xmin_a, xmax_a, xmin_b, xmax_b])
        y_sorted_list = sorted([ymin_a, ymax_a, ymin_b, ymax_b])
        x_intersect_w = x_sorted_list[2] - x_sorted_list[1] 
        y_intersect_h = y_sorted_list[2] - y_sorted_list[1]
        area_inter = x_intersect_w * y_intersect_h
        #return area_inter
    '''
    return if_intersect

# imageElement mode is RGBA
# img 是当前已经生成好的预想图了，相当于将整个画布传过来
# 注意元素内的位置和相对于整个画布的位置区别,重叠是基于整个画布找出来的，crop的时候当然也要在整个画布的alpha通道上进行crop
# region 要相对于元素的位置？
#@fn_timer
def textOverlap(size , elements , elementSize , elementType , elementLine , elementGroup , imageElement ):
    #imgAlpha = img.split()[3]
    '''
    imageAlpha = []
    for item in imageElement:
        alpha = imageElement[item].split()[3]
        imageAlpha.append(alpha)
    '''
    sum = 0.0
    flag = np.zeros((len(elements) , len(elements))) # 用来控制不要重复叠加
    for i in range(len(elements)):
        if elementType[i] == 'text':
            for j in range(len(elements)):
                if j == i:
                    continue
                if flag[i , j] or flag[j , i]:
                    continue
                else:
                    flag[i , j] = 1
                if if_intersection(elements[i][0] , elements[i][0] + elementSize[i][0] , elements[i][1] , elements[i][1] + elementSize[i][1] , elements[j][0] , elements[j][0] + elementSize[j][0] , elements[j][1] , elements[j][1] + elementSize[j][1]):
                    x_sorted_list = sorted([elements[i][0], elements[i][0] + elementSize[i][0], elements[j][0], elements[j][0] + elementSize[j][0]])
                    y_sorted_list = sorted([elements[i][1], elements[i][1] + elementSize[i][1], elements[j][1], elements[j][1] + elementSize[j][1]])
                    x_intersect_w = x_sorted_list[2] - x_sorted_list[1] 
                    y_intersect_h = y_sorted_list[2] - y_sorted_list[1]
                    startPos = (x_sorted_list[1] , y_sorted_list[1])
                    box = (x_sorted_list[1] , y_sorted_list[1] , x_sorted_list[1] + x_intersect_w  , y_sorted_list[1] + y_intersect_h )
                    #print "box" , box
                    imageCopy = Image.new("RGBA" , size)
                    imageCopy.paste(imageElement[j] , elements[j] , mask = imageElement[j])
                    imageCopy = imageCopy.split()[3]
                    region = imageCopy.crop(box)
                    region = np.array(region)
                    sum += region.sum()


    O_textOverlap = sum * 1.0 / (size[0] * size[1])
    E_textOverlap = sigmod(O_textOverlap , alpha)

    res = {}
    res['textOverlap'] = E_textOverlap
    
    return res

#@fn_timer
def graphicTextOverlap(size , elements , elementSize , elementType , elementLine , elementGroup , imageElement):
    sum = 0.0
    flag = np.zeros((len(elements) , len(elements))) # 用来控制不要重复叠加
    for i in range(len(elements)):
        if elementType[i] == 'graphic':
            for j in range(len(elements)):
                if j == i:
                    continue
                if elementType[j] != 'text':
                    continue
                if flag[i , j] or flag[j , i]:
                    continue
                else:
                    flag[i , j] = 1
                if if_intersection(elements[i][0] , elements[i][0] + elementSize[i][0] , elements[i][1] , elements[i][1] + elementSize[i][1] , elements[j][0] , elements[j][0] + elementSize[j][0] , elements[j][1] , elements[j][1] + elementSize[j][1]):
                    x_sorted_list = sorted([elements[i][0], elements[i][0] + elementSize[i][0], elements[j][0], elements[j][0] + elementSize[j][0]])
                    y_sorted_list = sorted([elements[i][1], elements[i][1] + elementSize[i][1], elements[j][1], elements[j][1] + elementSize[j][1]])
                    x_intersect_w = x_sorted_list[2] - x_sorted_list[1] 
                    y_intersect_h = y_sorted_list[2] - y_sorted_list[1]
                    startPos = (x_sorted_list[1] , y_sorted_list[1])
                    box = (x_sorted_list[1] , y_sorted_list[1] , x_sorted_list[1] + x_intersect_w  , y_sorted_list[1] + y_intersect_h )
                    imageCopy = Image.new("RGBA" , size)
                    imageCopy.paste(imageElement[j] , elements[j] , mask = imageElement[j])
                    imageCopy = imageCopy.split()[3]
                    regionCopy = imageCopy.crop(box)
                    #region.show()
                    imageText = Image.new('RGBA' , size)
                    imageText.paste(imageElement[i] , elements[i] , mask = imageElement[i])
                    imageText = imageText.split()[3]
                    regionText = imageText.crop(box)
                    regionText = np.array(regionText)
                    #region.show()
                    regionCopy = np.array(regionCopy)
                    #print region.sum()
                    tmp = np.zeros(regionText.shape)
                    for k in range(regionText.shape[0]):
                        for z in range(regionText.shape[1]):
                            tmp[k , z] = min(regionText[k , z] , regionCopy[k , z])

                    sum += tmp.sum()


    O_graphicTextOverlap = sum * 1.0 / (size[0] * size[1])
    E_graphicTextOverlap = sigmod(O_graphicTextOverlap , alpha)

    res = {}
    res['textOverlapGraphic'] = E_graphicTextOverlap
    return res

'''
def graphicGraphicOverlap(size , imageElement , elements , elementSize , elementType):
    sum = 0.0
    flag = np.zeros((len(elements) , len(elements))) # 用来控制不要重复叠加
    for i in range(len(elements)):
        if elementType[i] == 'graphic':
            for j in range(len(elements)):
                if j == i:
                    continue
                if elementType[j] != 'graphic':
                    continue
                if flag[i , j] or flag[j , i]:
                    continue
                else:
                    flag[i , j] = 1
                if if_intersection(elements[i][0] , elements[i][0] + elementSize[i][0] , elements[i][1] , elements[i][1] + elementSize[i][1] , elements[j][0] , elements[j][0] + elementSize[j][0] , elements[j][1] , elements[j][1] + elementSize[j][1]):
                    x_sorted_list = sorted([elements[i][0], elements[i][0] + elementSize[i][0], elements[j][0], elements[j][0] + elementSize[j][0]])
                    y_sorted_list = sorted([elements[i][1], elements[i][1] + elementSize[i][1], elements[j][1], elements[j][1] + elementSize[j][1]])
                    x_intersect_w = x_sorted_list[2] - x_sorted_list[1] 
                    y_intersect_h = y_sorted_list[2] - y_sorted_list[1]
                    startPos = (x_sorted_list[1] , y_sorted_list[1])
                    box = (x_sorted_list[1] , y_sorted_list[1] , x_sorted_list[1] + x_intersect_w  , y_sorted_list[1] + y_intersect_h )
                    imageCopy = Image.new("RGBA" , size)
                    imageCopy.paste(imageElement[j] , elements[j] , mask = imageElement[j])
                    imageCopy = imageCopy.split()[3]
                    region = imageCopy.crop(box)
                    region = np.array(region)
                    sum += region.sum()


    O_graphicGraphicOverlap = sum * 1.0 / (size[0] * size[1])
    E_graphicGraphicOverlap = sigmod(O_graphicGraphicOverlap , alpha)
    return E_graphicGraphicOverlap
'''


def ifInBound(pixel , size):
    flag = 0
    if pixel[0] <= size[0] and pixel[1] <= size[1]:
        flag = 1
    return flag


# if_intersection(xmin_a, xmax_a, ymin_a, ymax_a, xmin_b, xmax_b, ymin_b, ymax_b)
'''
    if if_intersect == True:
        x_sorted_list = sorted([xmin_a, xmax_a, xmin_b, xmax_b])
        y_sorted_list = sorted([ymin_a, ymax_a, ymin_b, ymax_b])
        x_intersect_w = x_sorted_list[2] - x_sorted_list[1] 
        y_intersect_h = y_sorted_list[2] - y_sorted_list[1]
        area_inter = x_intersect_w * y_intersect_h
        #return area_inter
    '''
#@fn_timer
def graphicBoundary(size , elements , elementSize , elementType , elementLine , elementGroup , imageElement ):
    sum = 0.0
    for item in range(len(elements)):
        img = imageElement[item].split()[3]
        img = np.asarray(img)
        I = np.zeros((int(elementSize[item][1]) , int(elementSize[item][0])))
        xmin_a , ymin_a = elements[item]
        xmax_a , ymax_a = (elements[item][0] + elementSize[item][0] , elements[item][1] + elementSize[item][1])
        xmin_b , ymin_b = (0 , 0)
        xmax_b , ymax_b = size
        if if_intersection(xmin_a, xmax_a, ymin_a, ymax_a, xmin_b, xmax_b, ymin_b, ymax_b):
            x_sorted_list = sorted([xmin_a, xmax_a, xmin_b, xmax_b])
            y_sorted_list = sorted([ymin_a, ymax_a, ymin_b, ymax_b])
            x_intersect_w = x_sorted_list[2] - x_sorted_list[1] 
            y_intersect_h = y_sorted_list[2] - y_sorted_list[1]

            #相对位置和绝对位置的问题
            if x_sorted_list[0] >= 0 and y_sorted_list[0] >= 0:
                I[0: y_intersect_h , 0: x_intersect_w] = 1
            elif x_sorted_list[0] < 0 and y_sorted_list[0] >= 0:
                I[0: y_intersect_h , -x_intersect_w : ] = 1
            elif x_sorted_list[0] >= 0 and y_sorted_list[0] < 0 :
                I[-y_intersect_h: , 0: x_intersect_w] = 1
            elif x_sorted_list[0] < 0 and y_sorted_list[0] < 0:
                I[-y_intersect_h: , -x_intersect_w:] = 1
        AI = img * I
        tmp = AI.sum() * 1.0 / img.sum()
        tmp = 1 - tmp
        #print tmp
        sum += tmp
    B_graphic = sum * 1.0 / len(elements)
    E_graphicBoundary = sigmod(B_graphic , alpha)

    res = {}
    res['graphicBoundary'] = E_graphicBoundary
    #print res
    return res



'''

@fn_timer
def graphicBoundary(size , imageElement , elements , elementSize , elementType):
    A = 0.0
    sum = 0.0
    sumAI = 0.0
    for i in range(len(elements)):
        #if elementType[i] == "graphic":
        img = imageElement[i].split()[3]
        img = np.array(img)
        #A = img.sum()

        I = np.zeros((int(elementSize[i][1]) , int(elementSize[i][0])))
        #print I.shape
        for x_axis in range(int(elements[i][0]) , int(elements[i][0] + elementSize[i][0]) ):
            for y_axis in range(int(elements[i][1]) , int(elements[i][1] + elementSize[i][1]) ):
                I[(y_axis - elements[i][1]) , (x_axis - elements[i][0])] = ifInBound((x_axis , y_axis) , size)
        #print I
        AI = img * I
        sumAI = AI.sum()
        A = img.sum()

        if A != 0:
            sum += (1 - sumAI * 1.0 / A)
            #print sum
        else:
            sum += 0

    B_graphic = sum * 1.0 / len(elements)
    E_graphicBoundary = sigmod(B_graphic , alpha)
    return E_graphicBoundary

'''
# elementGroup 是每个元素有属于自己的一个分组，比如-0 , 1 , 2,都是整数,是个列表 ， 没有分组的为-1
#@fn_timer
def groupSizeVar(size , elements , elementSize , elementType , elementLine , elementGroup , imageElement):
    group = list(set(elementGroup))
    numGroup = len(group)

    sum = 0.0
    for item in group:
        if item == -1:
            numGroup -= 1
            continue
        M = []
        for i in range(len(elements)):            
            if elementGroup[i] == item:
                M.append((elementSize[i][0] * elementSize[i][1]) * 1.0 / (size[0] * size[1]))
        #print M
        M = np.array(M)
        #print M
        #print M.var()
        sum += M.var()


    #print numGroup
    if numGroup != 0:
        E_groupSizeVar = 1.0 * sum / numGroup
    else:    
        E_groupSizeVar = 0

    res = {}
    res['groupSizeVar'] = E_groupSizeVar
    return res



# 这里取两个矩形区域的中心点
def elementBoundDis(elements , elementSize ,size):
    Dis = np.zeros((len(elements) , len(elements)))

    for i in range(len(elements)):
        for j in range(len(elements)):
            di = (elements[i][0] + 0.5 * elementSize[i][0] , elements[i][1] + 0.5 * elementSize[i][1])
            dj = (elements[j][0] + 0.5 * elementSize[j][0] , elements[j][1] + 0.5 * elementSize[j][1])
            Dis[i , j] = dis(di , dj , size)

    return Dis

#@fn_timer
def groupDistMean(size , elements , elementSize , elementType , elementLine , elementGroup , imageElement):
    group = list(set(elementGroup))
    numGroup = len(group)

    Dis = elementBoundDis(elements , elementSize , size)
    #print Dis
    sum = 0.0

    sumGroup =0.0
    
    for item in group:
        cnt = 0
        if item == -1:
            numGroup -= 1
            continue
        sum = 0.0
        for i in range(len(elements)):
            #print elementType[i] , item
            if elementGroup[i] == item:
                min = 1000000000.0
                cnt += 1
                for j in range(len(elements)):
                    if i != j and elementGroup[j] == item:
                        #cnt += 1
                        d = Dis[i , j]
                        if min > d:
                            min = d
                sum += min
                #print sum
        if cnt != 0:
            sum = sum * 1.0 / cnt
        else:
            sum = 0
        sumGroup += sum 

    #print numGroup
    if numGroup != 0:
        sumGroup = sumGroup * 1.0 / numGroup
    else:
        sumGroup = 0


    E_groupDistMean = sumGroup

    res = {}
    res['groupDistMean'] = E_groupDistMean
    return res




#import textwrap
# 文本换行 , 假设行间距为0
def getWrapSize(text , font_size ,  line_space = 0 , font_type = 'msyh.ttf'):
    font = ImageFont.truetype(font_type , font_size)
    #lines = textwrap.wrap(text , width = max_width)
    lines = text

    width = 0
    height = 0

    for line in lines:
        w , h = font.getsize(line)
        if width < w:
            width = w
        height += (h + line_space)


    return (width , height - line_space)

# 这里的text是分行之后的列表的第一项
def getFontSize(area , text):
    font_size = 1
    font = ImageFont.truetype('msyh.ttf' , font_size)
    fontPixel= font.getsize(text[0])
    #fontArea = fontPixel[0] * fontPixel[1] * 1.0

    while fontPixel[0] <= area[0] and fontPixel[1] <= area[1]:
        font_size += 1
        font = ImageFont.truetype('msyh.ttf' , font_size)
        fontPixel= font.getsize(text)
        fontArea = fontPixel[0] * fontPixel[1] * 1.0

    font_size -= 1
    return font_size


# image = Image.open(images)
def getImageSize(image , area):
    w , h = area['image']
    width , height = image.size

    ratio = width * 1.0 / height

    # 假设宽度设置为w
    h_size = w * 1.0 / ratio
    if h_size > h:
        w_size = h * ratio
        return (w_size , h)
    else:
        return (w , h_size)



# title 根据\n来识别行数
diffW = 0
diffH = 0
#@fn_timer
def getInitInfo(size , area , pos , title , subtitle , images , background , color):
    global diffW
    global diffH
    elements = []
    elementType = []
    elementLine = []
    elementSize = []
    imageElement = []

    background = Image.open(background)
    background = background.resize(size , Image.ANTIALIAS)
    # title
    text = title.split('\r\n')
    lines = len(text)
    elementLine.append(lines)
    elementType.append("text")
    w , h = area["title"]
    lineSize = h / lines
    #print w , lineSize
    #print lines[0]
    fontSize = getFontSize((w , lineSize) , text[0])
    titleSize = getWrapSize(text , fontSize ,  line_space = 0 , font_type = 'msyh.ttf')
    elementSize.append((int(titleSize[0]) , int(titleSize[1])))
    elements.append(pos['title'])

    # 直接绘制title
    img = Image.new("RGBA" , titleSize)
    draw = ImageDraw.ImageDraw(img , "RGBA")
    font = ImageFont.truetype('msyh.ttf' , fontSize)
    #draw.text((0 , 0))
    y_text = 0
    for item in text:
        width , height = font.getsize(item)
        draw.text((0 , y_text) , item , fill = color , font = font)
        y_text += height
    imageElement.append(img)
    img.save("title.png")

    #subtitle
    if subtitle != "":
        text = subtitle.split('\r\n')
        lines = len(text)
        elementLine.append(lines)
        elementType.append("text")
        w , h = area["subtitle"]
        lineSize = h / lines
        fontSize = getFontSize((w , lineSize) , text[0])
        subtitleSize = getWrapSize(text , fontSize ,  line_space = 0 , font_type = 'msyh.ttf')
        elementSize.append((int(subtitleSize[0]) , int(subtitleSize[1])))
        elements.append(pos['subtitle'])

        # 直接绘制subtitle
        img = Image.new("RGBA" , subtitleSize)
        draw = ImageDraw.ImageDraw(img , "RGBA")
        font = ImageFont.truetype('msyh.ttf' , fontSize)
        #draw.text((0 , 0))
        y_text = 0
        for item in text:
            width , height = font.getsize(item)
            draw.text((0 , y_text) , item , fill = 'black' , font = font)
            y_text += height
        imageElement.append(img)
        img.save("subtitle.png")
    else:
        subtitleSize = (1 , 1) 
        #elementLine.append(1)
        #elementType.append("text")
        #elementSize.append((0 , 0))
        #elements.append(pos['subtitle'])

    # 直接绘制subtitle
    '''
    img = Image.new("RGBA" , subtitleSize)
    draw = ImageDraw.ImageDraw(img , "RGBA")
    font = ImageFont.truetype('msyh.ttf' , fontSize)
    #draw.text((0 , 0))
    y_text = 0
    for item in text:
        width , height = font.getsize(item)
        draw.text((0 , y_text) , item , fill = 'black' , font = font)
        y_text += height
    imageElement.append(img)
    img.save("subtitle.png")
    '''
    #images
    # 这里有个问题，如何区分每个area
    image = 0
    for item in images:
        img = Image.open(item)
        imageSize = getImageSize(img , area)
        imageWidth , imageHeight = imageSize
        #print 'before' , pos['image']

        x , y = pos['image']
        w , h = area['image']
        diffW = (w - imageWidth) / 2
        diffH = (h - imageHeight) / 2
        #pos['image'] = (int(x + diffW) , int(y + diffH))

        #print 'after' , pos['image']
        image = img.resize((int(imageSize[0]) , int(imageSize[1])) , Image.ANTIALIAS)
        elementSize.append((int(imageSize[0]) , int(imageSize[1])))

        elementType.append('graphic')
        elementLine.append(-1)
        elements.append(pos['image'])
    imageElement.append(image)

    elementGroup = [0 , 0 , -1]
    return size , elements , elementSize , elementType , elementLine , elementGroup , imageElement , background




# area 存放的是框（应该是要元素适应的，这里只是获取）
# pos 是起始位置
def getElementInfo(Images , size , template):
    templateId = templateSelect(size , Images)
    templateInfo = getTemplateInfo(template , templateId)
    data = templateInfo['data']['children']
    pos = {}
    area = {}

    children = data

    for key , value in children.items():
        area[key] = (value['w'] * size[0] , value['h'] * size[1])
        pos[key] = (int(value['x'] * size[0]) , int(value['y'] * size[1]))
    return pos , area



'''
1. 通过json获取元素相对重心位置
2. 使用图片重心进行微调
3. 绘制初始方案

如何确定字号大小

'''


def ifInElement(pixel , element , elementSize):
    flag = True
    if pixel[0] >= element[0] and pixel[0] <= (element[0] + elementSize[0]) and pixel[1] >= element[1] and pixel[1] <= (element[1] + elementSize[1]):
        flag = False
    return flag

#@fn_timer
def merge_init(title , Subtitle , Images , color , size , background , template = 'templateM.json'):
    #pdb.set_trace()
    # 获取json信息
    #templateId = templateSelect(size , Images)
    #templateInfo = getTemplateInfo(template , templateId)
    #data = templateInfo['data']['children']
    layout = {}

    # 获取位置，大小信息
    pos , area = getElementInfo(Images , size , template)

    #for key , value in pos.items():
    #    pos[key] = (int(value[0]) , int(value[1]))

    size , elements , elementSize , elementType , elementLine , elementGroup , imageElement , back = getInitInfo(size , area , pos , title , Subtitle , Images , background , color)
    initialize(size , elements , elementSize , elementType , elementLine , elementGroup , imageElement , back , 'initialize.png')
    layout['pos'] = pos
    layout['area'] = area
    layout['size'] = size
    layout['title'] = title
    layout['subtitle'] = Subtitle
    layout['images'] = Images
    layout['elementGroup'] = elementGroup

    
    '''
    Dis = []
    #elementMatrix = np.zeros((size[1] , size[0]))
    for i in range(len(elements)):
        elementMatrix = np.zeros((size[1] , size[0]))
        for k in range(size[1]):
            for z in range(size[0]):
                #print k , z
                if ifInElement((k , z) , elements , elementSize):
                    elementMatrix[k , z] = euclideanDis((k , z) , elements[i] , elementSize[i] , size)
                else:
                    elementMatrix[k , z] = 0
        

        Dis.append(elementMatrix)
    '''
    #np.set_printoptions(threshold=np.NaN)
    #np.savetxt("a.txt", Dis[0])
    #print Dis[0].shape

    #res , energy = calcLayout(layout , getWeight(balancePara = None , scale = None , space = None, alignment = None , overlap = None) , Dis , background)
    #print res
    #print NIO(layout , getWeight())

    n = 51
    #optimize(layout , n , getWeight(balancePara = 5 , scale = 5 , space = 5, alignment = 0 , overlap = 5) , Dis , elements , elementSize)

    return pos , area


# background = *.png
#@fn_timer
def initialize(size , elements , elementSize , elementType , elementLine , elementGroup , imageElement , background , filename):
    global diffH
    global diffW
    Img = Image.new('RGBA' , size , (255 , 255 , 255))
    Draw = ImageDraw.ImageDraw(Img , "RGBA")

    Img.paste(background , (0 , 0))
    x , y = elements[-1]
    elements[-1] = (int(x + diffW) , int(y + diffH))
    for item in range(len(elements)):
        Img.paste(imageElement[item] , elements[item] , mask = imageElement[item])
    folder = 'aliBanner/static/img/'
    Img.save(folder + filename)


'''
@fn_timer
def initialize(background , pos , area , title , Subtitle , Images , size  , filename):
    
    #titleStartPos , SubtitleStartPos , imageStartPos = getStartPos(pos , area , title , Subtitle ,Images)
    elements , elementSize , elementType , elementLine , elementGroup = getInitInfo(area , pos , title , Subtitle , Images)
    

    # 开始绘制
    Img = Image.new("RGBA" , size , (255 , 255 , 255))
    Draw = ImageDraw.ImageDraw(Img , "RGBA")

    back = Image.open(background)
    back = back.resize(size , Image.ANTIALIAS)
    Img.paste(back , (0 , 0) , mask = back)
    
    titleImage = Image.open('title.png')
    subtitleImage = Image.open('subtitle.png')

    Img.paste(titleImage , pos['title'] , mask = titleImage)
    Img.paste(subtitleImage , pos['subtitle'] , mask = subtitleImage)

    idx = 2
    image = 0
    for item in Images:
        image = Image.open(item)
        imageSize = elementSize[idx]
        image = image.resize((int(imageSize[0]) , int(imageSize[1])) , Image.ANTIALIAS)
        #pos = elements[idx]
        Img.paste(image , pos['image'] , mask = image)
        idx += 1

    folder = 'aliBanner/static/img/'
    Img.save(folder + filename)
    #Img.save(filename)

    
    imageElement = [titleImage , subtitleImage , image]

    #titleInfo = (pos['title'] , titleImage)
    #subtitleInfo = (pos['subtitle'] , subtitleImage)
    #imageInfo = (pos['image'] , image)

    return size , elements , elementSize , elementType , elementLine , elementGroup , imageElement , back
'''

# 可以用来计算当前布局的Energy term

import multiprocessing
#@fn_timer
def getEnergyTerm(size , elements , elementSize , elementType , elementLine , elementGroup , imageElement , Dis , background):
    #pdb.set_trace()
    '''
    functionList = [alignCalc , whiteSpace , getBalanceGravityCenter , spread , dist , margin , textSize , textVar , minTextSize ,textOverlap , graphicTextOverlap , graphicBoundary ,  groupSizeVar , groupDistMean]
    pool = multiprocessing.Pool()

    result = []
    #whiteSpace(size , elements , elementSize , elementType , elementLine , elementGroup , imageElement , background)
    #pool.apply_async(whiteSpace , args = (size , elements , elementSize , elementType , elementLine , elementGroup , imageElement , background))
    for func in functionList:
        res = pool.apply_async(func , args = (size , elements , elementSize , elementType , elementLine , elementGroup , imageElement))
        result.append(res)

    pool.close()
    pool.join()

    #print result
    
    for item in result:
        print item.get()
    
    #assert False
    energy = {k:v for item in result for k , v in item.get().items()}
    return energy
    '''
    
    energy = {}
    res = []
    res.append(alignCalc(size , elements , elementSize , elementType , elementLine , elementGroup , imageElement ))
    res.append(whiteSpace(size , elements , elementSize , elementType , elementLine , elementGroup , imageElement ))
    res.append(getBalanceGravityCenter(size , elements , elementSize , elementType , elementLine , elementGroup , imageElement))
    res.append(spread(size , elements , elementSize , elementType , elementLine , elementGroup , imageElement ))
    res.append(dist(size , elements , elementSize , elementType , elementLine , elementGroup , imageElement ))
    res.append(margin(size , elements , elementSize , elementType , elementLine , elementGroup , imageElement ))
    res.append(textSize(size , elements , elementSize , elementType , elementLine , elementGroup , imageElement ))
    res.append(textVar(size , elements , elementSize , elementType , elementLine , elementGroup , imageElement ))
    res.append(minTextSize(size , elements , elementSize , elementType , elementLine , elementGroup , imageElement ))
    res.append(textOverlap(size , elements , elementSize , elementType , elementLine , elementGroup , imageElement ))
    res.append(graphicTextOverlap(size , elements , elementSize , elementType , elementLine , elementGroup , imageElement ))
    res.append(graphicBoundary(size , elements , elementSize , elementType , elementLine , elementGroup , imageElement ))
    res.append(groupSizeVar(size , elements , elementSize , elementType , elementLine , elementGroup , imageElement ))
    res.append(groupDistMean(size , elements , elementSize , elementType , elementLine , elementGroup , imageElement))

    energy = {k:v for item in res for k , v in item.items()}
    return energy
    
    '''
    a , b , c = alignCalc(elements , elementSize)
    for item in range(len(types)):
        #print types[item] + " " + str(a[item])
        energy[types[item]] = a[item]
    #print "alignment energy term [E_align , E_misalign_x , E_misalign_y] :" , a , b , c
    energy['misalignx'] = b
    energy['misaligny'] = c



    a = whiteSpace(size , elements , elementSize)
    #print "whiteSpace :" , a
    energy['whiteSpace'] = a


    # whiteSpace(size , elements):

    a = getBalanceGravityCenter(elements , imageElement ,size)
    #print "Balance" , a
    energy['balance'] = a

    #spread(size , elements , elementSize):

    #a = spread(size , elements , elementSize , Dis)
    a = spread(size , elements , elementSize)
    #print "spread :" , a
    energy['spread'] = a


    # dist(size , elements , elementSize)
    #a = dist(size , elements , elementSize , Dis)
    a = dist(size , elements , elementSize)
    #print "dist :" , a
    energy['dist'] = a


    a , b = margin(size , elements , elementSize , elementType)
    #print "margin [text , graphic]:" , a , b
    energy['textMargin'] = a
    energy['graphicMargin'] = b

    a , b = textSize(size , elements , elementSize , elementType , elementLine)
    #print "text/graphic size :" , a , b
    energy['textSize'] = a
    energy['graphicSize'] = b

    #picSize = getImageSize(Images , area)
    #pic = pic.resize(picSize , Image.ANTIALIAS)

    a , b = textVar(size , elements , elementSize , elementType , elementLine)
    #print "text/graphic Var :" , a , b
    energy['textVar'] = a
    energy['graphicVar'] = b

    a , b = minTextSize(size , elements , elementSize , elementType , elementLine)
    #print "min Text/Graphic size :" , a , b
    energy['minTextSize'] = a
    energy['minGraphicSize'] = b

    #background = "background.png" # 记得要resize
    a = textContrast(background , size , imageElement , elements , elementSize , elementType)
    #print "text Contrast" , a
    energy['textContrast'] = a

    a = textOverlap(size , imageElement , elements , elementSize , elementType)
    #print "text overlap :" , a
    energy['textOverlap'] = a
    
    a = graphicTextOverlap(size , imageElement , elements , elementSize , elementType)
    #print "text overlaping on graphic :" , a
    energy['textOverlapGraphic'] = a
    
    #a = graphicGraphicOverlap(size , imageElement , elements , elementSize , elementType)
    #print "graphic overlapping on graphic" , a
    #energy['graphicOverlapGraphic'] = a
    
    a = graphicBoundary(size , imageElement , elements , elementSize , elementType)
    #print "graphic Boundary :" , a
    energy['graphicBoundary'] = a

    a = groupSizeVar(size , elements , elementSize , elementType , elementGroup)
    #print "group size variance :" , a
    energy['groupSizeVar'] = a

    
    a = groupDistMean(size , elements , elementSize , elementType , elementGroup)
    #print "group dist mean :" , a
    energy['groupDistMean'] = a
    return energy
    '''




# types = ["left" , "xcenter" , "right" , "top" , "ycenter" , "bottom"]
# 用来获取权重参数的 , 输入应该暂定为以下参数
'''
balance = request.POST['balance']
            scale = request.POST['scale']
            space = request.POST['space']
            alignment = request.POST['alignment']
            overlap = request.POST['overlap']
'''
def getWeight(balancePara = None , scale = None , space = None , alignment = None , overlap = None):
    weight = {}
    #平衡   1-10 分数 * 10
    balance = 100

    #留白
    dist = 75
    whiteSpace = 50
    spread = 50

    #重叠
    textOverlap = 500
    textOverlapGraphic = 500

    #大小
    textSize = 55
    graphicSize = 100



    #对齐
    left = 100
    xcenter = 50
    right = 12.5
    top = 75
    ycenter = 50
    bottom = 12.5


    #统一
    groupSizeVar = 50
    groupDistMean = 250



    #textContrast = 100
    minTextSize = 125
    minGraphicSize = 125
    textMargin = 150
    graphicMargin = 150
    graphicBoundary = 500
    textVar = 50
    graphicVar = 50
    misalignx = 50
    misaligny = 50
    
    #平衡   1-10 分数 * 10

    
    
    
    #graphicOverlapGraphic = 500
    '''

    balance = 100

    #留白
    dist = 50
    whiteSpace = 100
    spread = 50

    #重叠
    textOverlap = 500

    #大小
    textSize = 75
    graphicSize = 200



    #对齐
    left = 150
    xcenter = 50
    right = 12.5
    top = 75
    ycenter = 50
    bottom = 50


    #统一
    groupSizeVar = 50
    groupDistMean = 250



    textContrast = 0
    minTextSize = 125
    minGraphicSize = 125
    textMargin = 150
    graphicMargin = 150
    graphicBoundary = 500
    textVar = 500
    graphicVar = 50
    misalignx = 50
    misaligny = 50
    
    #平衡   1-10 分数 * 10

    
    
    textOverlapGraphic = 500
    #graphicOverlapGraphic = 500
    '''
    if balancePara is not None:
        balance += balancePara * 20

    if scale is not None:
        textSize += scale * 11
        graphicSize += scale * 20
        

    if space is not None:
        dist += space * 15
        whiteSpace += space * 10
        spread += space * 10
        

    if alignment is not None:
        left = 175 - math.fabs(alignment + 5 ) * 15
        xcenter = 100 - math.fabs(alignment) * 10
        right = 40 - math.fabs(alignment - 5) * 2


    if overlap is not None:
        textOverlap += overlap * 100
        textOverlapGraphic += overlap * 100

    weight['graphicBoundary'] = graphicBoundary
    weight['textSize'] = textSize
    weight['graphicSize'] = graphicSize
    weight['textVar'] = textVar
    weight['graphicVar'] = graphicVar
    weight['minTextSize'] = minTextSize
    weight['minGraphicSize'] = minGraphicSize
    #weight['textContrast'] = textContrast
    weight['textOverlap'] = textOverlap
    weight['textOverlapGraphic'] = textOverlapGraphic
    #weight['graphicOverlapGraphic'] = graphicOverlapGraphic
    weight['left'] = left
    weight['xcenter'] = xcenter
    weight['right'] = right
    weight['top'] = top
    weight['ycenter'] = ycenter
    weight['bottom'] = bottom
    weight['misalignx'] = misalignx
    weight['misaligny'] = misaligny
    weight['dist'] = dist
    weight['textMargin'] = textMargin
    weight['graphicMargin'] = graphicMargin
    weight['groupSizeVar'] = groupSizeVar
    weight['groupDistMean'] = groupDistMean
    weight['spread'] = spread
    weight['whiteSpace'] = whiteSpace
    weight['balance'] = balance


    return weight


# 给定layout(pos , area) , 计算参数指标（加权）
#@fn_timer
def calcLayout(layout , weights , Dis , background):
    pos = layout['pos']
    area = layout['area']
    title = layout['title']
    subtitle = layout['subtitle']
    image = layout['images']
    size = layout['size']
    color = layout['color']
    result = 0.0
    size , elements , elementSize , elementType , elementLine , elementGroup , imageElement , background = getInitInfo(size , area , pos , title , subtitle , image , background , color)
    #size , elements , elementSize , elementType , elementLine , elementGroup , imageElement , titleInfo , subtitleInfo , imageInfo  , background= initialize('background.png' , pos , area , title , subtitle , image , size  , 'gabage.png')
    energy = getEnergyTerm(size , elements , elementSize , elementType , elementLine , elementGroup , imageElement , Dis , background)
    #weight = getWeight()

    for key in energy.keys():
        tmp = energy[key] * weights[key]
        result += tmp
    
    return (result , energy)

'''
def merge_init(title , Subtitle , Images , size , template = 'templateM.json'):
    templateId = templateSelect(size , Images)
    templateInfo = getTemplateInfo(template , templateId)
    
    data = templateInfo['data']
    pos , area = getElementInfo(data , size)
    #print "area" , area
    #print "pos" ,pos

    for key , value in pos.items():
        pos[key] = (int(value[0]) , int(value[1]))
    #titleStartPos , SubtitleStartPos , imageStartPos = getStartPos(pos , area , title , Subtitle ,Images)
    elements , elementSize , elementType , elementLine = getInitInfo(area , pos , title , Subtitle , Images)

    elementGroup = [0 , 0 , -1]
    # 开始绘制
    Img = Image.new("RGBA" , size , (255 , 255 , 255))
    Draw = ImageDraw.ImageDraw(Img , "RGBA")
    
    titleImage = Image.open('title.png')
    subtitleImage = Image.open('subtitle.png')

    Img.paste(titleImage , pos['title'] , mask = titleImage)
    Img.paste(subtitleImage , pos['subtitle'] , mask = subtitleImage)

    idx = 2
    image = 0
    for item in Images:
        image = Image.open(item)
        imageSize = elementSize[idx]
        image = image.resize((int(imageSize[0]) , int(imageSize[1])) , Image.ANTIALIAS)
        #pos = elements[idx]
        Img.paste(image , pos['image'] , mask = image)
        idx += 1

    Img.save('banner.png')

    
    imageElement = [titleImage , subtitleImage , image]
      

    Img = Image.new("RGBA" , size , (255 , 255 , 255))
    Draw = ImageDraw.ImageDraw(Img , "RGBA")

    titleImage = Image.open('title.png')
    subtitleImage = Image.open('detail.png')
    pic = Image.open('context.png')


    elements = [titleStartPos , SubtitleStartPos ,  imageStartPos]
    #elementSize = [titleSize , subtitleSize , imageSize]

    imageElement = [titleImage , subtitleImage , pic]
    #elements = [titleImage , subtitleImage , pic]
    elementType = ['text' , 'text' , 'graphic']
    elementGroup = [0 , 0 , -1]
    elementLine = [1 , 1 , -1]
    elementSize = [titleImage.size , subtitleImage.size , pic.size]

    titleInfo =(titleStartPos , titleImage)
    subtitleInfo = (SubtitleStartPos , subtitleImage)
    imageInfo = (imageStartPos , pic)
   
    ####call Energy Function

    #alignCalc(titleInfo , subtitleInfo , imageInfo):
    titleInfo = (pos['title'] , titleImage)
    subtitleInfo = (pos['subtitle'] , subtitleImage)
    imageInfo = (pos['image'] , image)
    a , b , c = alignCalc(titleInfo , subtitleInfo , imageInfo)
    for item in range(len(types)):
        print types[item] + " " + str(a[item])
    print "alignment energy term [E_align , E_misalign_x , E_misalign_y] :" , a , b , c



    a = whiteSpace(size , elements , elementSize)
    print "whiteSpace :" , a


    # whiteSpace(size , elements):


    #spread(size , elements , elementSize):

    a = spread(size , elements , elementSize)
    print "spread :" , a


    # dist(size , elements , elementSize)
    a = dist(size , elements , elementSize)
    print "dist :" , a


    a , b = margin(size , elements , elementSize , elementType)
    print "margin [text , graphic]:" , a , b

    a , b = textSize(size , elements , elementSize , elementType , elementLine)
    print "text/graphic size :" , a , b

    #picSize = getImageSize(Images , area)
    #pic = pic.resize(picSize , Image.ANTIALIAS)

    a , b = textVar(size , elements , elementSize , elementType , elementLine)
    print "text/graphic Var :" , a , b

    a , b = minTextSize(size , elements , elementSize , elementType , elementLine)
    print "min Text/Graphic size :" , a , b

    background = "testBack.png" # 记得要resize
    a = textContrast(background , size , imageElement , elements , elementSize , elementType)
    print "text Contrast" , a

    a = textOverlap(size , imageElement , elements , elementSize , elementType)
    print "text overlap :" , a

    a = graphicTextOverlap(size , imageElement , elements , elementSize , elementType)
    print "text overlaping on graphic :" , a

    a = graphicGraphicOverlap(size , imageElement , elements , elementSize , elementType)
    print "graphic overlapping on graphic" , a

    a = graphicBoundary(size , imageElement , elements , elementSize , elementType)
    print "graphic Boundary :" , a

    a = groupSizeVar(size , elements , elementSize , elementType , elementGroup)
    print "group size variance :" , a

    
    a = groupDistMean(size , elements , elementSize , elementType , elementGroup)
    print "group dist mean :" , a




    #mg.paste(pic , imageStartPos , mask = pic)
    #print imageStartPos
    #Img.paste(titleImage , titleStartPos , mask = titleImage)
    #print titleStartPos
    #Img.paste(subtitleImage , SubtitleStartPos , mask = subtitleImage)
    #print SubtitleStartPos
    

    #Img.save('banner.png' , 'png')
    '
    font_type = "msyh.ttf"
    font_size_forTitle = 60
    #line_words_image_space = 10
    #line_space = 5

    font = ImageFont.truetype(font_type , font_size_forTitle)
    #Draw.setfont(font)

    # Title begin

    ## generate title location from template
    x , y = generateLocation(size , template.get(type = 'title'))
    startPosition = (x ,  y)
    Draw.text(startPosition , title , fill = 'black' , font = font)


    ## generate subtitle location from template
    title2SubTitle = template.get()
    sub_x , sub_y = generateLocation(size , template.get(type = 'title'))
    sub_startPosition = (sub_x , sub_y)
    font_size_fotSubTitle = font_size_forTitle / title2SubTitle

    font = ImageFont.truetype(font_type , font_size_fotSubTitle)
    Draw.text(sub_startPosition , Subtitle , fill = 'black' , font = font)


    ## generate images location from template
    imageRatio = template.get() # 图片占画布的比例
    imageX , imageY= generateLocation(size , template.get(type = 'images'))
    image_startPosition = (imageX , imageY)
    width = size.x
    height = size.y
    imageSize = (width * imageRatio , height * imageRatio)

    baseim = Image.open(Images)
    baseim = baseim.resize(imageSize , Image.ANTIALIAS)
    Img.paste(baseim , image_startPosition)

    Img.save('test.png' , 'png')
    '''

def updateSingleElePosition(layout):
    resultLayout = layout
    size = resultLayout['size']
    pos = resultLayout['pos']
    area = resultLayout['area']
    keys = pos.keys()
    # 随机选择一个元素
    elemIdx = random.choice(range(len(keys)))
    # 随机选择移动坐标(0 = x_axis , 1 = y_axis)
    axis = random.randint(0 , 1)

    offset = random.gauss(0 , 0.1)
    #position = pos[keys[elemIdx]]
    x , y = pos[keys[elemIdx]]
    #print pos[keys[elemIdx]]
    if axis == 0:
        offset *= size[0]
        #print offset 
        x += offset      
        #position[0] += offset
        pos[keys[elemIdx]] = (int(x) , int(y))
    else:
        offset *= size[1]
        y += offset
        pos[keys[elemIdx]] = (int(x) , int(y))

    #print pos[keys[elemIdx]]
    resultLayout['pos'] = pos
    resultLayout['area'] = area
    resultLayout['size'] = size

    return resultLayout

def updateHeight(layout):
    resultLayout = layout
    size = resultLayout['size']
    area = resultLayout['area']
    keys = area.keys()
    elemIdx = random.choice(range(len(keys)))
    offset = random.gauss(0 , 0.2)
    w , h = area[keys[elemIdx]]
    ratio = w * 1.0 /h
    h += (offset * h)
    w = h * ratio
    h = math.fabs(h)
    area[keys[elemIdx]] = (int(w) , int(h))

    resultLayout['size'] = size
    resultLayout['area'] = area
    return resultLayout

def alignElements(layout):
    resultLayout = layout
    size = resultLayout['size']
    pos = resultLayout['pos']
    area = resultLayout['area']
    axis = random.randint(0 , 1)
    keys = pos.keys()
    elemIdx1 = random.choice(range(len(keys)))

    elemIdx2 = random.choice(range(len(keys)))

    while elemIdx2 == elemIdx1:
        elemIdx2 = random.choice(range(len(keys)))

    x1 , y1 = pos[keys[elemIdx1]]
    w1 , h1 = area[keys[elemIdx1]]

    x2 , y2 = pos[keys[elemIdx2]]
    w2 , h2 = area[keys[elemIdx2]]

    if x1 == x2 and ((x1 + w1) != (x2 + w2)):
        if w1 > w2:
            w2 = w1
        else:
            w1 = w2
    elif y1 == y2 and ((y1 + h1) != (y2 + h2)):
        if h1 > h2:
            h2 = h1
        else:
            h1 = h2
    else:
        if axis == 0:
            sel = random.randint(0 , 1)
            if sel == 0:
                x1 = x2
            else:
                x2 = x1
        else:
            sel = random.randint(0 , 1)
            if sel == 0:
                y1 = y2
            else:
                y2 = y1


    pos[keys[elemIdx1]] = (int(x1) , int(y1))
    area[keys[elemIdx1]] = (int(w1) , int(h1))

    pos[keys[elemIdx2]] = (int(x2) , int(y2))
    area[keys[elemIdx2]] = (int(w2) , int(h2))

    resultLayout['size'] = size
    resultLayout['pos'] = pos
    resultLayout['area'] = area

    return resultLayout


def updateElementPos(layout):
    resultLayout = layout
    pos = resultLayout['pos']
    area = resultLayout['area']

    offset = random.gauss(0 , 0.2) * 100
    axis = random.randint(0 , 1)
    keys = pos.keys()
    for i in range(len(keys)):
        item = keys[i]
        x ,y = pos[item]        
        #print pos[item] 
        if axis == 0:
            x += offset
        else:
            y += offset
        pos[item] = (int(x) , int(y))
        #print pos[item] 

    resultLayout['pos'] = pos
    return resultLayout
# 默认一个组至少有两个元素
def updateElementGroup(layout):
    resultLayout = layout
    pos = resultLayout['pos']
    area = resultLayout['area']
    size = resultLayout['size']
    elementGroup = resultLayout['elementGroup']
    idxType = ['title' , 'subtitle' , 'image']
    keys = pos.keys()
    group = list(set(elementGroup))
    numGroup = len(group)
    for item in group:
        if item == -1:
            numGroup -= 1
    groupId = random.choice(group)

    while groupId == -1:
        groupId = random.choice(group)

    # elementGroup = [0 , 0 , -1](title , subtitle , image )
    # 有个问题，如何区分同组中属于什么元素(title , subtitle)
    sameGroup = []
    for i in range(len(elementGroup)):
        if elementGroup[i] == groupId:
            sameGroup.append(idxType[i])

    key1 = random.choice(sameGroup)
    key2 = random.choice(sameGroup)
    while key2 == key1:
        key2 = random.choice(sameGroup)

    x1 ,y1 = pos[key1]
    w1 , h1 = area[key1]

    x2 , y2 = pos[key2]
    w2 , h2 = area[key2]

    # 0 代表改变高度， 1代表改变位置
    offsetHeight = random.gauss(0 , 0.2) * size[1]
    #axis = random.randint(0 , 1)
    offsetPos = random.gauss(0 , 0.1)
    


    sel = random.randint(0 , 1)
    if sel == 0:
        h1 += offsetHeight
        h2 += offsetHeight
    else:
        axis = random.randint(0 , 1)
        if axis == 0:
            x1 += (offsetPos * size[0])
            x2 += (offsetPos * size[0])
        else:
            y1 += (offsetPos * size[1])
            y2 += (offsetPos * size[1])

    pos[key1] = (int(x1) , int(y1))
    area[key1] = (int(w1) , int(h1))

    pos[key2] = (int(x2) , int(y2))
    area[key2] = (int(w2) , int(h2))

    resultLayout['pos'] = pos
    resultLayout['area'] = area
    return resultLayout

def fillImage(layout):
    resultLayout = layout
    area = resultLayout['area']
    size = resultLayout['size']
    w ,h = area['image']
    #w , h = areaItem
    #imageRatio = w * 1.0 / h

    axis = random.randint(0 , 1)
    if axis == 0:
        w = size[0]
    else:
        h = size[1]
    area['image'] = (int(w) , int(h))

    resultLayout['area'] = area
    return resultLayout


def swapTwoElem(layout):
    resultLayout = layout
    pos = resultLayout['pos']
    keys = pos.keys()
    key1 = random.choice(keys)
    key2 = random.choice(keys)
    while key1 == key2:
        key2 = random.choice(keys)
    position = pos[key1]
    pos[key1] = pos[key2]
    pos[key2] = position

    resultLayout['pos'] = pos

    return resultLayout


import pdb
import copy
# layout (pos , area , title , subtitle , images , size , elementGroup)
# layout dict type
# layout made by the function calling
#@fn_timer
def optimize(layout , n , weights ,Dis , background):    
    bestLayout = copy.deepcopy(layout)
    currentLayout = copy.deepcopy(layout)
    nextLayout = None
    size = layout['size']

    currentEnergy = calcLayout(copy.deepcopy(currentLayout) , weights , Dis , background)[0]
    minEnergy = currentEnergy
    #print 'Bestenergy ' , calcLayout(bestLayout)
    

    T = n

    while T > 0:
        #print 'currentEnergy' , currentEnergy
        #print '============================'
        if T % 10 == 1:
            pos = bestLayout['pos']
            area = bestLayout['area']
            title = bestLayout['title']
            Subtitle = bestLayout['subtitle']
            Images = bestLayout['images']
            size = bestLayout['size']
            color = bestLayout['color']
            
            filename = str(T) + '.png'
            #initialize(size , elements , elementSize , elementType , elementLine , elementGroup , imageElement , background , filename):
            size , elements , elementSize , elementType , elementLine , elementGroup , imageElement , back = getInitInfo(size , area , pos , title , Subtitle , Images , background , color)
            initialize(size , elements , elementSize , elementType , elementLine , elementGroup , imageElement , back , filename)
            print '%s bestLayout energy term' % T , calcLayout(copy.deepcopy(bestLayout) , weights , Dis , background)[0]
        seed = random.randint(0 , 60)
        #seed = 9

        if seed <= 10:
            nextLayout = updateSingleElePosition(copy.deepcopy(currentLayout))
        elif seed <= 30:
            nextLayout = updateHeight(copy.deepcopy(currentLayout))
        elif seed <= 50:
            nextLayout = alignElements(copy.deepcopy(currentLayout))
        elif seed <= 60:
            nextLayout = updateElementPos(copy.deepcopy(currentLayout))
        elif seed <= 70:
            nextLayout = updateElementGroup(copy.deepcopy(currentLayout))
        elif seed <= 80:
            nextLayout = swapTwoElem(copy.deepcopy(currentLayout))
        elif seed <= 82:
            nextLayout = fillImage(copy.deepcopy(currentLayout))

        Dis = []
        #elementMatrix = np.zeros((size[1] , size[0]))
        '''
        for i in range(len(elements)):
            elementMatrix = np.zeros((size[1] , size[0]))
            for k in range(size[1]):
                for z in range(size[0]):
                    #print k , z
                    if ifInElement((k , z) , elements , elementSize):
                        elementMatrix[k , z] = euclideanDis((k , z) , elements[i] , elementSize[i] , size)
                    else:
                        elementMatrix[k , z] = 0
            

            Dis.append(elementMatrix)
        '''
        nextEnergy = calcLayout(copy.deepcopy(nextLayout) , weights , Dis , background)[0]
        #print '第%s次迭代' %  T , '  当前的能量值为： ' , calcLayout(copy.deepcopy(currentLayout) , weights , Dis , background)[0]
        #print 'nextEnergy' , nextEnergy
        #print 'currentEnergy' , calcLayout(currentLayout)
        #print 'bestEnergy' , calcLayout(copy.deepcopy(bestLayout) , weights , Dis , background)[0]
        #pdb.set_trace()
        if nextEnergy < currentEnergy:
            #print 'nextEnergy < currentEnergy'
            currentEnergy = nextEnergy
            currentLayout = copy.deepcopy(nextLayout)
            if currentEnergy < minEnergy:
                minEnergy = currentEnergy
                bestLayout = copy.deepcopy(currentLayout)
        else:
            a = random.random()
            #print a
            #print (currentEnergy - nextEnergy) * 1.0 / T
            if a < (math.e ** ((currentEnergy - nextEnergy) * 1.0 / T)):
                #print 'a < (math.e ** ((currentEnergy - nextEnergy) * 1.0 / T))'
                currentLayout = copy.deepcopy(nextLayout)
                currentEnergy = nextEnergy
                if currentEnergy < minEnergy:
                    #print 'currentEnergy < minEnergy'
                    minEnergy = currentEnergy
                    bestLayout = copy.deepcopy(currentLayout)
        #print 'minEnergy' , minEnergy
        #print 'Bestenergy ' , calcLayout(bestLayout)

        T -= 1
    #print 'minEnergy' , minEnergy

    '''
        layout['pos'] = pos
    layout['area'] = area
    layout['size'] = size
    layout['title'] = title
    layout['subtitle'] = Subtitle
    layout['images'] = Images
    layout['elementGroup'] = elementGroup
    '''

    pos = bestLayout['pos']
    area = bestLayout['area']
    title = bestLayout['title']
    Subtitle = bestLayout['subtitle']
    Images = bestLayout['images']
    size = bestLayout['size']
    color = bestLayout['color']

    size , elements , elementSize , elementType , elementLine , elementGroup , imageElement , back = getInitInfo(size , area , pos , title , Subtitle , Images , background ,color)
    initialize(size , elements , elementSize , elementType , elementLine , elementGroup , imageElement , back , 'final.png')
    #initialize(background , pos , area , title , Subtitle , Images , size  , 'final.png')

    return bestLayout
    #energy = getEnergyTerm(size , elements , elementSize , elementType , elementLine , elementGroup , imageElement , titleInfo , subtitleInfo , imageInfo)
    #initialize(pos , area , title , Subtitle , Images , size )
    #print 'energy ' , calcLayout(bestLayout)



def weightGradient(energyItem , betaWeightItem):
    res = 0.0
    res = energyItem * math.e ** betaWeightItem
    return res


def lineSearch(layout , layoutS , betaWeight , delatWeight , keys , Dis , background):
    res = 0.5
    weight1 = {}
    weight2 = {}
    for i in range(len(keys)):
        item = keys[i]
        weight1[item] = math.e ** (betaWeight[item] - res * delatWeight[item])
        weight2[item] = math.e ** (betaWeight[item] - 0.5 * res * delatWeight[item])
    G1 = calcLayout(layout , weight1 , Dis , background)[0] - calcLayout(layoutS , weight1 , Dis , background)[0]
    G2 = calcLayout(layout , weight2 , Dis , background)[0] - calcLayout(layoutS , weight2 , Dis , background)[0]
    print G2 , G1

    while G1 > G2 and res > 1e-3:
        res = res * 1.0 / 2
        for i in range(len(keys)):
            item = keys[i]
            weight1[item] = math.e ** (betaWeight[item] - res * delatWeight[item])
            weight2[item] = math.e ** (betaWeight[item] - 0.5 * res * delatWeight[item])
        G1 = calcLayout(layout , weight1 , Dis , background)[0] - calcLayout(layoutS , weight1 , Dis , background)[0]
        G2 = calcLayout(layout , weight2 , Dis , background)[0] - calcLayout(layoutS , weight2 , Dis , background)[0]

   
    return res


# weight is dict type
# betaWeight is dict
#optimize(layout , n , weights ,Dis , elements , elementSize , background):
def NIO(layout , weights , Dis, elements , elementSize , background):
    print weights
    betaWeight = {}

    C = []
    C.append(layout)
    keys = weights.keys()
    bestLayout = {}
    for i in range(len(keys)):
        item = keys[i]
        betaWeight[item] = math.log(weights[item])
    while True:
        minEnergy = 10000000000000.0
        layoutI = None
        currentWeight = {}
        for i in range(len(keys)):
            item = keys[i]
            currentWeight[item] = math.e ** betaWeight[item]


        for item in C:
            energy , E = calcLayout(item , currentWeight , Dis , background)
            if minEnergy > energy:
                minEnergy = energy
                layoutI = copy.deepcopy(item)

        layoutS = optimize(layoutI , 100 , currentWeight , Dis , elements , elementSize , background)
        C.append(layoutS)
        energyS , Es= calcLayout(layoutS , currentWeight , Dis , background)
        energyT  , Et= calcLayout(layout , currentWeight , Dis , background)
        print energyS , Es , Et , energyT

        if math.fabs(energyT - energyS) < 0.2:
            bestLayout = layoutS
            break

        delatWeight = {}
        
        for i in range(len(keys)):
            item = keys[i]
            delatWeight[item] = (weightGradient(Et[item], betaWeight[item]) - weightGradient(Es[item] , betaWeight[item]))

        p = lineSearch(layout , layoutS , betaWeight , delatWeight , keys , Dis , background)

        for i in range(len(keys)):
            item = keys[i]
            betaWeight[item] -= (p * delatWeight[item])


    for i in range(len(keys)):
        item = keys[i]
        weights[item] = math.e ** betaWeight[item]

    print weights
    pos = bestLayout['pos']
    area = bestLayout['area']
    title = bestLayout['title']
    Subtitle = bestLayout['subtitle']
    Images = bestLayout['images']
    size = bestLayout['size']
    
    #initialize(background , pos , area , title , Subtitle , Images , size  , 'nio.png')
    return weights






if __name__ == '__main__':
    title = "2016 New Arrivals\r\nReady to Wear Fashion"
    subtitle = "Shows & Designers\r\nNew tech, new function\r\nTrending Styles New Arrivals"
    images = ['test3.png']
    merge_init(title , subtitle , images , (600 , 800) , 'background.png' , 'templateM.json')





