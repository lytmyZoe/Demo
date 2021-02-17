#curses 在终端上显示图形界面
import curses;
#random 模块用来生成随机数
from random import randrange,choice
#collection提供一个字典的子类defaultdict,可以指定ley值不存在时，value的默认值
from collections import defaultdict

#此游戏中所有的有效输入都可以转换为“上，下，左，右，游戏重置，退出”
actions = ['Up','Left','Down','Right','Restart','Exit']
#有效输入键是最常见的W(上），A(左），S（下），D(右）,R(重置）,Q(退出）

#ord() 函数以一个字符作为参数，返回参数对应的ASCII数值，便于和后面捕捉的键位关联
letter_codes = [ord(ch) for ch in 'WASDRQwasdrq']

#将输入与行为进行关联
actions_dict = dict(zip(letter_codes,actions * 2))

# actions_dict 输出结果为
{87: 'Up', 65: 'Left', 83: 'Down', 68: 'Right', 82: 'Restart', 81: 'Exit', 119: 'Up', 97: 'Left', 115: 'Down', 100: 'Right', 114: 'Restart', 113: 'Exit'}

#用戶輸入處理
#阻塞+循環，直到獲得用戶有效輸入才返回對應行爲
def get_user_action(keyboard):
    char = "N"
    while char not in actions_dict:
        #返回按下鍵位的ASCII 碼值
        char = keyboard.getch()
    #返回輸入鍵位對應的行爲
    return actions_dict[char]

#zip(*)進行矩陣轉置
def transpose(field):
    return [list(row) for row in zip(*field)]

#矩陣逆轉（非逆矩陣）
#將矩陣的每一行倒序
def invert(field):
    return [row[::-1] for row in field]


#創建鍵盤
#初始化鍵盤的參數，可以指定棋盤的高和寬以及遊戲勝利條件，默認4*4
class GameField(object):
    def __init__(self, height=4,width=4,win=2048):
        self.height = height    #高
        self.width = wdth       #寬
        self.win_value = 2048   #過關分數
        self.score = 0          #當前分數
        self.highscore = 0      #最高分
        self.reset()            #棋盤重置

    #鍵盤初始化的時候被調用，將棋盤所有位置元素復原爲0，然後在在隨機位置上生成遊戲初始的數值
    def reset(self):
        #更新分數
        if self.score > self.highscore:
            self.highscore = self.score
        self.score = 0
        #初始化遊戲開始界面
        self.field = [[0 for i in range(self.width)] for j in range(self.height)]
        self.spawn()
        self.spawn()

    def move(self,direction):
        def move_row_left(row):
            def tighten(row):
                '''把零散的非零单元挤到一块'''
                #先将非零的元素全拿出来加入到新列表
                new_row = [i for i in row if i != 0]
                #按照原列表的大小，给新列表后面补零
                new_row += [0 for i in range(len(row) - len(new_row))]
                return new_row
            def merge(row):
                #对邻近元素进行合并
                pair = False
                new_row = []
                for i in range(len(row)):
                    if pair:
                        #合并后，加入乘2后的元素在0元素后面
                        new_row.append(2 * row[i])
                        #更新分数
                        self.score += 2 * row[i]
                        pair = False
                    else:
                        #判断邻近元素能否合并
                        if i + 1 < len(row) and row[i] == row[i+1]:
                            pair = True
                            #可以合并时，新列表加入元素0
                            new_row.append(0)
                        else:
                            #不能合并，新列表加入该元素
                            new_row.append(row[i])
                #断言合并后不会改变行列大小，否则报错
                assert len(new_row) == len(row)
                return new_row
            return tighten(merge(tighten(row)))
        #棋盘走一步
        #通过对矩阵进行转置和逆转，可以直接从左移得到其余三个方向的移动操作
        #创建moves字典，把不同的棋盘操作作为不同的key，对应不同的方法函数 
        moves = {}
        moves['Left'] = lambda field: [move_row_left(row) for row in field]
        moves['Right'] = lambda field: invert(moves['Left'](invert(field)))
        moves['Up'] = lambda field: transpose(moves['Left'](transpose(field)))
        moves['Down'] = lambda field: transpose(moves['Right'](transpose(field)))
        #判断棋盘操作是否存在且可行
        if direction in moves:
            if self.move_is_possible(direction):
                self.field = moves[direction](self.field)
                self.spawn()
                return True
            else:
                return False

    #any函数：接收一个可迭代对象作为参数(iterable)，返回bool值
    #里层的any传入了每一行的元素并依次比较这一行的每个元素与self.win_value的大小
    #如果有任何一个元素大于self.win_value,就返回True,否则返回False;
    #外层的any传入的是矩阵每一行元素在内层any里处理后返回的bool值，如果有任何一个bool值为True，外层的any就返回True
    def is_win(self):
        #任意一个位置的数大于设定的win值时，游戏胜利
        return any(any(i >= self.win_value for i in row) for row in self.field)
   
    def is_gameover(self):
        #无法移动和合并时，游戏失败
        return not any(self.move_is_possible(move) for move in actions)



    #隨機生成一個2或4
    def spawn(self):
        #從100種取一個隨機數，如果這個隨機數大於89，new_element等於4，否則等於2
        new_element = 4 if randrange(100) > 89 else 2
        #得到一個隨機空白位置的元組坐標
        #choice方法會從一個非空的序列(list,str,tuple等）中隨機返回一個元素
        (i,j) = choice([(i,j) for i in range(self.width) for j in range(self.height) if self.field[i][j] == 0])
        self.field[i][j] = new_element

    #判断是否能移动
    def move_is_possible(self,direction):
        #传入要移动的方向，判断能否向这个方向移动 
        def row_is_left_movable(row):
            def change(i):
                #当左边有空位（0），右边有数字时，可以向左移动
                if row[i] == 0 and row[i + 1] != 0:
                    return True
                #当左边有一个数和右边的数相等时，可以向左合并
                if row[i] != 0 and row[i + 1] == row[i]:
                    return True
                return False
            return any(change(i) for i in range(len(row) - 1))
        


#遊戲主邏輯
def main(stdscr):
 
    def init():
        #初始化遊戲鍵盤
        return 'Game'
    
    def not_game(state):
        '''畫出GameOver或者Win的界面
        讀取用戶輸入得到action，判斷是重啓遊戲還是結束遊戲
        '''
        #默認是當前狀態，美譽‘Restart’或‘Exit’行爲就會一直保持當前狀態
        responses = defaultdict(lambda: state)
        #新建鍵值對，將行爲和狀態對應
        responses['Restart'], responses['Exit'] = 'Init','Exit'
        return responses[action]

    def game():
        #畫出當前棋盤狀態
        #讀取用戶輸入得到action
        if action == 'Restart':
            return 'Init'
        if action == 'Exit':
            return 'Exit'
        #if 成功移動了一步
            if 遊戲勝利了:
                return 'Win'
            if 遊戲失敗了:
                return 'Gameover'
        return 'Game'

    state_actions = {
            'Init': init,
            'Win': lambda: not_game('Win'),
            'Gamwover': lambda: not_game('Gameover'),
            'Game': game
    }

    state = 'Init'

    #狀態機開始循環
    while state != 'Exit':
        state = state_actions[state]()
















