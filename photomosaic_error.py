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

def getAverageRGB(image):
    """
    \u8BA1\u7B97\u56FE\u50CF\u7684\u5E73\u5747 RGB \u503C

    \u5C06\u56FE\u50CF\u5305\u542B\u7684\u6BCF\u4E2A\u50CF\u7D20\u70B9\u7684 R?G?B \u503C\u5206\u522B\u7D2F\u52A0?\u7136\u540E\u9664\u4EE5\u50CF\u7D20\u70B9\u6570?\u5C31\u5F97\u5230\u56FE\u50CF\u7684\u5E73\u5747 R?G?B
    \u503C

    @param {Image} image PIL Image \u5BF9\u8C61
    @return {Tuple[int, int, int]} \u5E73\u5747 RGB \u503C
    """

    # \u8BA1\u7B97\u50CF\u7D20\u70B9\u6570
    npixels = image.size[0] * image.size[1]
    # \u83B7\u5F97\u56FE\u50CF\u5305\u542B\u7684\u6BCF\u79CD\u989C\u8272\u53CA\u5176\u8BA1\u6570?\u7ED3\u679C\u7C7B\u4F3C
    # [(c1, (r1, g1, b1)), (c2, (r2, g2, b2)), ...]
    cols = image.getcolors(npixels)
    # \u83B7\u5F97\u6BCF\u79CD\u989C\u8272\u7684 R?G?B \u7D2F\u52A0\u503C?\u7ED3\u679C\u7C7B\u4F3C
    # [(c1 * r1, c1 * g1, c1 * b1), (c2 * r2, c2 * g2, c2 * b2), ...]
    sumRGB = [(x[0] * x[1][0], x[0] * x[1][1], x[0] * x[1][2]) for x in cols]
    # \u5148\u7528 zip \u65B9\u6CD5\u5BF9 sumRGB \u5217\u8868\u91CC\u7684\u5143\u7EC4\u5BF9\u8C61\u6309\u5217\u8FDB\u884C\u5408\u5E76?\u7ED3\u679C\u7C7B\u4F3C
    # [(c1 * r1, c2 * r2, ...), (c1 * g1, c2 * g2, ...),
    # (c1 * b1, c2 * b2, ...)]
    # \u7136\u540E\u8BA1\u7B97\u6240\u6709\u989C\u8272\u7684 R?G?B \u5E73\u5747\u503C?\u7B97\u6CD5\u4E3A
    # (sum(ci * ri) / np, sum(ci * gi) / np, sum(ci * bi) / np)
    avg = tuple([int(sum(x) / npixels) for x in zip(*sumRGB)])
    return avg

def splitImage(image, size):
    """
    \u5C06\u56FE\u50CF\u6309\u7F51\u683C\u5212\u5206\u6210\u591A\u4E2A\u5C0F\u56FE\u50CF

    @param {Image} image PIL Image \u5BF9\u8C61
    @param {Tuple[int, int]} size \u7F51\u683C\u7684\u884C\u6570\u548C\u5217\u6570
    @return {List[Image]} \u5C0F\u56FE\u50CF\u5217\u8868
    """

    W, H = image.size[0], image.size[1]
    m, n = size
    w, h = int(W / n), int(H / m)
    imgs = []
    # \u5148\u6309\u884C\u518D\u6309\u5217\u88C1\u526A\u51FA m * n \u4E2A\u5C0F\u56FE\u50CF
    for j in range(m):
        for i in range(n):
            # \u5750\u6807\u539F\u70B9\u5728\u56FE\u50CF\u5DE6\u4E0A\u89D2
            imgs.append(image.crop((i * w, j * h, (i + 1) * w, (j + 1) * h)))
    return imgs


def getBestMatchIndex(input_avg, avgs):
    """
    找出颜色值最接近的索引

    把颜色值看做三维空间里的一个点，依次计算目标点跟列表里每个点在三维空间里的距离，从而得到距离最近的那个点的索引

    @param {Tuple[int,int,int]} input_avg 目标颜色值
    @param {List[Tuple[int,int,int]]} avgs 要搜索的颜色值列表
    @return {int} 命中元素的索引
    """
    index = 0
    min_index = 0
    min_dist = float("inf")
    for val in avgs:
        # 三维空间两点距离计算公式 (x1-x2)*(x1-x2)+(y1-y2)*(y1-y2)+(z1-z2)*(z1-z2),这里只需要比较大小，所以无需求平方根值
        dist = ((val[0] - input_avg[0]) * (val[0] - input_avg[0]) + (val[1] - input_avg[1]) * (val[1] - input_avg[1]) + (val[2] - input_avg[2]) * (val[2] - input_avg[2]))
        if dist < min_dist:
            min_dist =  dist
            min_index = index
        index += 1
    return min_index

def createImageGrid(images, dims):
    """
    将图像列表里的小图像按先行后列的顺序拼接为一个大图像
   
    @param {List[Image]} images 小图像列表
    @param {Tuple[int,int]} dims 大图像的行数和列表
    @return Image 拼接得到的大图像
    """
    
    m, n = dims

    #确保小图像个数满足要求
    assert m * n == len(images)
    
    #计算所有小图像的最大宽度和高度
    width = max([img.size[0] for img in images])
    height = max([img.size[1] for img in images])
    
    #创建大图像对象
    grid_img = Image.new('RGB', (n * width, m * height))
    #依次将每个小图像粘贴到大图像里
    for index in range(len(images)):
        # 计算要粘贴到网格的哪行
        row = int(index / n)
        # 计算要粘贴到网格的哪列
        col = index - n * row
        # 根据行列数以及网格的大小得到网格的左上角坐标，把小图像粘贴到这里
        grid_img.paste(images[index], (col * width, row * height))
    return grid_img

def createPhotomosaic(target_image, input_images, grid_size, reuse_images=True):
    """
    图片马赛克生成
    
    @param {Image} target_image 目标图像
    @param {image} input_images 替换图像列表
    @param {Tuple[int, int]} grid_size 网格行数和列数
    @param {bool} reuse_images 是否允许重复使用替换图像
    @return {Image} 马赛克图像
    """
    #将目标图像切成网格小图像
    print('splitting input image...')
    target_images = splitImage(target_image, grid_size)
    #为每个网格小图像在替换图像列表里找到颜色最相似的替换图像
    print('finding image matches...')
    output_images = []
    # 分10组进行，每组完成后打印进度信息，避免用户长时间等待
    count = 0
    batch_size = int(len(target_images) / 10)

    #计算替换图像列表里每个图像的颜色平均值
    avgs = []
    for img in input_images:
        avgs.append(getAverageRGB(img))
   
    #对每个网格小图像，从替换图像列表找到颜色最相似的那个，添加到 output_images 里
    for img in target_images:
        #计算颜色平均值
        avg = getAverageRGB(img)
        #找到最匹配的那个小图像，添加到output_images
        match_index = getBestMatchIndex(avg, avgs)
        output_images.append(input_images[match_index])
        #如果完成了一组，打印进度信息
        if count > 0 and batch_size > 10 and count % batch_size == 0:
            print('processed %d of %d...' % (count, len(target_images)))
        count += 1
        #如果不允许重用替换图像，则用过后就从列表里移除
        if not reuse_images:
            input_images.remove(match)
        
    #将 output_images 里的图像按网格大小拼接成一个大图像
    print('createing mosaic...')
    mosaic_image = createImageGrid(output_images, grid_size)
    return mosaic_image
        
def main():
    #定义程序接收的命令行参数
    parser = argparse.ArgumentParser(description = 'Creates a photomosaic from input images')
    parser.add_argument('--target-image',dest='target_image',required = True)
    parser.add_argument('--input_folder', dest = 'input_folder', required = True)
    parser.add_argument('--grid-size', nargs = 2, dest = 'grid_size', required = True)
    parser.add_argument('--output-file', dest = 'outfile', required = False)

    #解析命令行参数
    args = parser.parse_agrs()
    
    #网格大小
    grid_size = (int(args.grid_size[0]), int(args.grid_size[1]))

    #马赛克图像保存路径，默认为mosaic.png
    output_filename = 'mosaic.png'
    if args.output:
        output_filename = args.outfile

    #打开目标图像
    print('reading targe image...')
    target_image = Image.open(args.target_image)

    #从指定文件夹下加载所有替换图像
    print('reading input images...')
    intput_images = getImages(args.input_folder)
    #如果替换图像列表为空则退出程序
    if input_images == []:
        print('No input iamges found in %s. Exiting.' %(args.input_folder, ))
        exit()

    #将所有替换图像缩放到指定的网格大小
    print('resizing images...')
    dims = (int(target_image.size[0] / grid_size[1]), int(target_image.size[1] / grid_size[0]))
    for img in input_images:
        img.thumbnail(dims)

    #生成马赛克图像
    print('starting photomosaic creation...')
    mosaic_image = createPhotomosaic(target_image, input_images, grid_size)

    #保存马赛克图像
    mosaic_image.save(output_filename, 'PNG')
    print("saved output to %s" % (output_filename,))

    print('done.')

if __name__ == '__main__':
    main()








