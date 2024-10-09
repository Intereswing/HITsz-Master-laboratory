import threading
import time
from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
app.config["SECRET_KEY"] = "Secret of MoGoKu"
app.config['async_mode'] = 'eventlet'
lock = threading.Lock()

""" 数据库的连接 """
# 配置数据库信息
HOSTNAME = "localhost"
PORT = 3306
USERNAME = "root"
PASSWORD = "root"
DATABASE = "gomoku"
app.config["SQLALCHEMY_DATABASE_URI"] = \
    f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}?charset=utf8mb4"

# 创建与APP关联的数据库对象
#  SQLAlchemy会读取和app.config关联的数据库信息
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    userName = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    totalGameTime = db.Column(db.Integer, default=0)
    winGameTime = db.Column(db.Integer, default=0)
    valid = db.Column(db.Boolean, default=True)


""" 用户登录与注册部分 """


@app.route("/")
def login():
    # 渲染登录界面视图函数
    return render_template("loginAndSign/login.html")


@socketio.on("login")
def handleLogin(data):
    # 获取用户登录输入的数据
    userName = data["userName"]
    password = data["password"]
    # 从数据库中筛选是否存在该用户
    user = db.session.query(User).filter_by(userName=userName).first()
    if user is not None and user.password == password:
        emit("login_success", {"userId": user.id})
    else:
        emit("login_fail")


@socketio.on("toSign")
def turnSign():
    # 从登录界面跳转到注册界面
    emit("go", {"url": "/sign"})


@app.route("/sign")
def sign():
    # 渲染注册界面视图函数
    return render_template("loginAndSign/sign.html")


@socketio.on("sign")
def handleSign(data):
    # 获取用户用于注册的用户名，查看数据库中是否已被注册过
    userName = data["nickname"]
    exist = db.session.query(User).filter_by(userName=userName).first()
    if exist is None:
        # 如用户名未被注册，则为用户注册一个新账户
        name = data["nickname"]
        password = data["password"]
        newUser = User(userName=name, password=password)
        lock.acquire()
        try:
            db.session.add(newUser)
            db.session.commit()
        finally:
            lock.release()
        emit("sign_success")
    else:
        # 如该用户名已被注册，不可以用此用户名注册一个新账户
        emit("sign_fail")


@socketio.on("toLogin")
def toLogin():
    # 从注册界面跳转到登录界面
    emit("go", {"url": "/"})



""" 用户中心的操作 """


@app.route("/userCenter", methods=["GET", "POST"])
def userCenter():
    # 实现用户中心界面，当用户没有登录时要求用户进行登录
    if request.method == "GET":
        return redirect(url_for('login'))
    else:
        userId = request.form.get("userId")
        return render_template('gamePart/userCenter.html', userId=userId)


@socketio.on("connected")
def updateUserinfo(data):
    # 进入用户中心页面后，更新显示用户个人信息
    userId = data["userId"]
    user = db.session.query(User).get(userId)
    data = {
        "userName": user.userName,
        "totalGameTime": user.totalGameTime,
        "winGameTime": user.winGameTime,
        "winRate": round((100 * user.winGameTime / user.totalGameTime), 2) if user.totalGameTime > 0 else 0
    }
    emit("user_info", data)




""" 游戏交互部分 """


class Room:
    # 表示游戏房间的类
    def __init__(self, room_id):
        # 初始化房间
        self.room_id = room_id
        self.user1Id = None
        self.user2Id = None
        self.user1Name = None
        self.user2Name = None
        self.board = [[0] * 10 for _ in range(10)]
        self.round = 0
        self.user1Heartbeat = None
        self.user2Heartbeat = None

    def addUser(self, user: User):
        # 向房间中添加用户
        if self.user1Id is None:
            self.user1Id = user.id
            self.user1Name = user.userName
            self.user1Heartbeat = time.time()
            # 暂时设置用户2的心跳时间，便于监听
            self.user2Heartbeat = time.time()
        else:
            self.user2Id = user.id
            self.user2Name = user.userName
            self.user2Heartbeat = time.time()

    def getRoomId(self) -> str:
        # 获取房间号
        return self.room_id

    def setRoomId(self, newId: str):
        # 重新设置房间号
        self.room_id = newId

    def isFull(self) -> bool:
        # 判断当前房间是否满了
        return self.user1Id is not None and self.user2Id is not None

    def getUser1Id(self) -> int:
        # 获取玩家1的ID
        return self.user1Id

    def getUser2Id(self) -> int:
        # 获取玩家2的ID
        return self.user2Id

    def getUser1Name(self) -> str:
        # 获取玩家1的名称
        return self.user1Name

    def getUser2Name(self) -> str:
        # 获取玩家2的名称
        return self.user2Name

    def setUser1Heartbeat(self, t):
        # 设置玩家1的心跳信息
        self.user1Heartbeat = t

    def getUser1Heartbeat(self):
        # 获取玩家1的信条信息
        return self.user1Heartbeat

    def setUser2Heartbeat(self, t):
        # 设置玩家2的心跳信息
        self.user2Heartbeat = t

    def getUser2Heartbeat(self):
        # 获取玩家2的信条信息
        return self.user2Heartbeat

    def playChess(self, cell: str, first: bool) -> bool:
        # 在指定位置落子，1表示黑子，-1表示白子
        x, y = map(int, cell.split('-')[1:])
        if self.board[x][y] == 0:
            self.board[x][y] = 1 if first else -1
            return True
        else:
            return False

    def checkWin(self):
        # 检查行
        for i in range(10):
            for j in range(6):
                if abs(sum(self.board[i][j:j + 5])) == 5:
                    return self.board[i][j]
        # 检查列
        for i in range(6):
            for j in range(10):
                if abs(sum(self.board[k][j] for k in range(i, i + 5))) == 5:
                    return self.board[i][j]
        # 检查左上到右下的对角线
        for i in range(6):
            for j in range(6):
                if abs(sum(self.board[i + k][j + k] for k in range(5))) == 5:
                    return self.board[i][j]
        # 检查右上到左下的对角线
        for i in range(6):
            for j in range(9, 3, -1):
                if abs(sum(self.board[i + k][j - k] for k in range(5))) == 5:
                    return self.board[i][j]
        return None

    def getRound(self) -> int:
        return self.round

    def addRound(self) -> None:
        self.round = self.round + 1


class RoomManager:
    # 管理当前活动房间的类
    def __init__(self):
        # 初始化房间链表和互斥锁
        self.rooms = {}
        self.availableRoomIds = []
        self.lock = threading.Lock()

    def createRoom(self, room_id: str) -> Room:
        # 创建一个新的游戏房间，并加入列表和字典
        room = Room(room_id)
        with self.lock:
            self.rooms[room_id] = room
            self.availableRoomIds.append(room_id)
        return room

    def removeRoom(self, room_id: str):
        # 删除一个结束游戏的房间
        with self.lock:
            if room_id in self.rooms:
                del self.rooms[room_id]
            if room_id in self.availableRoomIds:
                self.availableRoomIds.remove(room_id)

    def getRoom(self, room_id: str):
        # 获取一个指定ID的游戏房间
        with self.lock:
            if room_id in self.rooms:
                return self.rooms[room_id]
            else:
                return None

    def getAvailRoom(self):
        # 获取一个可用的游戏房间
        with self.lock:
            if len(self.availableRoomIds) > 0:
                room_id = self.availableRoomIds.pop(0)
                return self.rooms.pop(room_id)
            else:
                return None

    def updateRoom(self, roomId: str, room: Room):
        # 更新字典中的键值对
        with self.lock:
            self.rooms[roomId] = room


# 实例化RoomManager
roomManager = RoomManager()

# 设置用户最长等待时间，小于心跳检测时间
WAIT_TIME = 10

# 设置可以进行和局的回合数
DRAW_ROUND = 40

room_cnt = 0

@socketio.on("joinGame")
def joinGame(data):
    # 实现用户进入游戏
    userId = data["userId"]
    room = roomManager.getAvailRoom()
    if room:
        # 如果找到了空闲房间，可以直接开始游戏
        user = db.session.query(User).get(userId)
        room.addUser(user)
        room.setRoomId(str(room.getRoomId()) + "-" + str(userId))
        roomManager.updateRoom(room.getRoomId(), room)
        emit("joinSuccess", {
            "user1Name": room.getUser1Name(),
            "user2Name": room.getUser2Name(),
            "roomId": room.getRoomId(),
            "userId": userId,
            "userName": user.userName,
            "first": False
        })
    else:
        # 如果没有空闲房间，需要进行新建
        user = db.session.query(User).get(userId)
        global room_cnt
        room = roomManager.createRoom(room_cnt)
        room_cnt = room_cnt + 1
        room.addUser(user)
        i = 0
        while not room.isFull():
            i = i + 1
            time.sleep(1)
            emit("joinWait", {"time": i})
            if i > WAIT_TIME:
                break
        if i <= WAIT_TIME:
            emit("joinSuccess", {
                "user1Name": room.getUser1Name(),
                "user2Name": room.getUser2Name(),
                "roomId": room.getRoomId(),
                "userId": userId,
                "userName": user.userName,
                "first": True
            })
        else:
            roomManager.removeRoom(room.getRoomId())
            emit("joinFail")


@app.route("/game", methods=["POST"])
def game():
    # 游戏界面的渲染
    user1Name = request.form.get("user1Name")
    user2Name = request.form.get("user2Name")
    roomId = request.form.get("roomId")
    userId = request.form.get("userId")
    userName = request.form.get("userName")
    first = request.form.get("first")
    return render_template("gamePart/game.html", user1Name=user1Name, user2Name=user2Name,
                           roomId=roomId, userId=userId, userName=userName, first=first)


@socketio.on("start")
def handleStart(data):
    # 处理游戏初始化时的客户端状态
    join_room(data["roomId"])
    if data["first"]:
        # 执黑方先下棋
        emit("startChecked")


@socketio.on("change")
def handleChange(data):
    # 回合处理
    place = data["place"]
    roomId = data["roomId"]
    first = data["first"]
    room = roomManager.getRoom(roomId)
    if room.playChess(place, first):
        emit("changeChecked", {"place": place, "isBlack": first}, room=roomId)
        room.addRound()
        result = room.checkWin()
        if result is not None:
            # 有一方胜出
            user1Id, user2Id = map(int, roomId.split("-"))
            # user1 = db.session.query(User).get(user1Id)
            # user1.totalGameTime = user1.totalGameTime + 1
            # user2 = db.session.query(User).get(user2Id)
            # user2.totalGameTime = user2.totalGameTime + 1
            if result == 1:
                emit("gameOver", {"firstWin": True}, room=roomId)
                # user1.winGameTime = user1.winGameTime + 1
            else:
                emit("gameOver", {"firstWin": False}, room=roomId)
                # user2.winGameTime = user2.winGameTime + 1
            db.session.commit()
        elif room.getRound() > DRAW_ROUND:
            # 回合较多，可以进行和棋
            emit("draw", room=roomId)


@socketio.on("applyDraw")
def applyDraw(data):
    # 申请和局
    roomId = data["roomId"]
    first = data["first"]
    emit("apply", {"first": first}, room=roomId)


@socketio.on("acceptApply")
def acceptApply(data):
    # 接受和局
    roomId = data["roomId"]
    emit("drawn", room=roomId)
    user1Id, user2Id = map(int, roomId.split("-"))
    user1 = db.session.query(User).get(user1Id)
    user1.totalGameTime = user1.totalGameTime + 1
    user2 = db.session.query(User).get(user2Id)
    user2.totalGameTime = user2.totalGameTime + 1
    db.session.commit()


@socketio.on("rejectApply")
def rejectApply(data):
    # 拒绝和局
    emit("rejected", room=data["roomId"])


@socketio.on("leave")
def handleLeave(data):
    # 处理用户退出游戏房间
    roomId = data["roomId"]
    leave_room(roomId)
    roomManager.removeRoom(roomId)


""" 处理游戏的心跳信息 """
TIMEOUT = 100


def checkHeartbeat():
    # 检查心跳信息是否超时
    with app.app_context():
        flag = True
        while flag:
            for room in list(roomManager.rooms.values()):
                print('check heartbeat',room.getUser1Heartbeat(),room.getUser2Heartbeat(),room.getRoomId())
                if time.time() - room.getUser1Heartbeat() > TIMEOUT:
                    print('player1 out!!!')
                    roomId = room.getRoomId()
                    socketio.emit("timeout", room=roomId)
                    roomManager.removeRoom(roomId)
                    # flag = False
                    break
                elif time.time() - room.getUser2Heartbeat() > TIMEOUT:
                    print('player2 out!!!')
                    roomId = room.getRoomId()
                    socketio.emit("timeout", room=roomId)
                    roomManager.removeRoom(roomId)
                    # flag = False
                    break
            time.sleep(1)


# 开启心跳线程
checkBeatThread = threading.Thread(target=checkHeartbeat)
checkBeatThread.start()


@socketio.on("heartbeat")
def handleHeartbeat(data):
    # 更新心跳时间
    room = roomManager.getRoom(data["roomId"])
    try:
        
        room.getUser1Heartbeat()
        room.getUser2Heartbeat()    
    except:
        socketio.emit("timeout", room=room)
    if data["first"]:
        room.setUser1Heartbeat(time.time())
    else:
        room.setUser2Heartbeat(time.time())


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
