#从给定的文件夹中读取小块图像

def getImage(imageDir):
    """
    从给定目录里加载所有替换图像
    @param {str} imageDir 目录路径
    @return {List[Image]} 替换图像列表
    """
    
    files = os.listdir(imageDir)
    images = []
    for file in files:
        #得到文件绝对路径
        filePath = os.path.abspath(os.path.join(imageDir,file))
        try:
            fp = open(filePath, "rb")
            im = Image.open(fp)
            images.append(im)
            #确定了图像信息，但没有加载全部图像数据，用到时才会
            im.load()
            #用完关闭文件，防止资源泄露
            fp.close()
        except: 
            #加载某个图像识别，直接跳过
            print("Invalid image: %s" % (filePath,))
    return images
