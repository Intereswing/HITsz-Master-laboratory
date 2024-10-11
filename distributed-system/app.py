import os
import threading
import time

from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, emit, join_room, leave_room

from db import get_db, init_app

app = Flask(__name__, instance_relative_config=True)
socketio = SocketIO(app, cors_allowed_origins="*")
app.config["SECRET_KEY"] = "Secret of MoGoKu"
app.config['async_mode'] = 'eventlet'
app.config['DATABASE'] = os.path.join(app.instance_path, 'gomoku.sqlite')
try:
    os.makedirs(app.instance_path)
except OSError:
    pass

init_app(app) # database
lock = threading.Lock()


""" 用户登录与注册部分 """


@app.route("/")
def login():
    # 渲染登录界面视图函数
    return render_template('loginAndSign/login.html')


@socketio.on("login")
def handleLogin(data):
    db = get_db()
    error = None
    # 获取用户登录输入的数据
    username = data["userName"]
    password = data["password"]
    # 从数据库中筛选是否存在该用户
    user = db.execute(
        'SELECT * FROM user WHERE username = ?', (username,)
    ).fetchone()
    if username is None:
        error = 'Incorrect username.'
    elif user['password'] != password:
        error = 'Incorrect password.'

    if error is None:
        emit("login_success", {"userId": user['id']})
    else:
        emit(error)


@socketio.on("toSign")
def turnSign():
    # 从登录界面跳转到注册界面
    emit("go", {"url": "/sign"})


@app.route("/sign")
def sign():
    # 渲染注册界面视图函数
    return render_template('loginAndSign/sign.html')


@socketio.on("sign")
def handleSign(data):
    # 获取用户用于注册的用户名，查看数据库中是否已被注册过
    username = data["nickname"]
    password = data["password"]
    db = get_db()
    error = None

    if not username:
        error = 'Please enter your username.'
    elif not password:
        error = 'Please enter your password.'

    if error is None:
        lock.acquire()
        try:
            db.execute(
                'INSERT INTO user (username, password, totalGame, winGame) VALUES (?, ?, ?, ?)',
                (username, password, 0, 0)
            )
            db.commit()
        except db.IntegrityError:
            error = 'Username already taken.'
        else:
            emit("sign_success")
        finally:
            lock.release()


    # if exist is None:
    #     # 如用户名未被注册，则为用户注册一个新账户
    #     name = data["nickname"]
    #     password = data["password"]
    #     newUser = User(userName=name, password=password)
    #     lock.acquire()
    #     try:
    #         db.session.add(newUser)
    #         db.session.commit()
    #     finally:
    #         lock.release()
    #     emit("sign_success")
    # else:
    #     # 如该用户名已被注册，不可以用此用户名注册一个新账户
    #     emit("sign_fail")


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
    db = get_db()
    # user = db.session.query(User).get(userId)
    user = db.execute(
        'SELECT * FROM user WHERE id = ?', (userId,)
    ).fetchone()

    data = {
        "userName": user['username'],
        "totalGameTime": user['totalGame'],
        "winGameTime": user['winGame'],
        "winRate": round((100 * user['winGame'] / user['totalGame']), 2) if user['totalGame'] > 0 else 0
    }
    emit("user_info", data)


# GAME CORE REFACTOR
class UserInGame:
    def __init__(self, userId, username, IsBlack: bool):
        self.userId = userId
        self.username = username
        self.IsBlack = IsBlack

    def get_userID(self):
        return self.userId
    def get_username(self):
        return self.username
    def get_IsBlack(self):
        return self.IsBlack

    def set_userID(self, userId):
        self.userId = userId
    def set_username(self, username):
        self.username = username
    def set_IsBlack(self, IsBlack: bool):
        self.IsBlack = IsBlack
    def rotate_black(self):
        self.IsBlack = not self.IsBlack

""" 游戏交互部分 """
class Room:
    # 表示游戏房间的类
    def __init__(self, room_id, user1: UserInGame=None, user2: UserInGame=None):
        # 初始化房间
        self.room_id = room_id
        self.user1 = user1
        self.user2 = user2

        self.inPrePhase = True
        self.steps = 0
        self.board = [[0] * 10 for _ in range(10)]
        self.round = 0
        self.user1Heartbeat = None
        self.user2Heartbeat = None

    # Get Properties.
    def getRoomId(self) -> str:
        # 获取房间号
        return self.room_id

    def get_user1(self):
        return self.user1

    def get_user2(self):
        return self.user2

    def get_user_by_id(self, user_id):
        if self.user1.get_userID() == int(user_id):
            return self.user1
        elif self.user2.get_userID() == int(user_id):
            return self.user2
        else:
            return None

    def get_another_user(self, user):
        return self.user1 if self.user1 != user else self.user2

    def getUser1Heartbeat(self):
        # 获取玩家1的心跳信息
        return self.user1Heartbeat

    def getUser2Heartbeat(self):
        # 获取玩家2的信条信息
        return self.user2Heartbeat

    def isFull(self) -> bool:
        # 判断当前房间是否满了
        return self.user1 is not None and self.user2 is not None

    def getRound(self) -> int:
        return self.round

    def getSteps(self) -> int:
        return self.steps

    def isInPrePhase(self):
        return self.inPrePhase


    # Modify Properties.
    def setRoomId(self, newId: str):
        # 重新设置房间号
        self.room_id = newId

    def addUser(self, user):
        # 向房间中添加用户
        if self.user1 is None:
            self.user1 = user
            self.user1Heartbeat = time.time()
            # 暂时设置用户2的心跳时间，便于监听
            self.user2Heartbeat = time.time()
        else:
            self.user2 = user
            self.user2Heartbeat = time.time()

    def setUser1Heartbeat(self, t):
        # 设置玩家1的心跳信息
        self.user1Heartbeat = t

    def setUser2Heartbeat(self, t):
        # 设置玩家2的心跳信息
        self.user2Heartbeat = t

    def addRound(self) -> None:
        self.round = self.round + 1

    def setInPrePhase(self, inPrePhase: bool):
        self.inPrePhase = inPrePhase


    # Core.
    def playChess(self, cell: str, user: UserInGame) -> bool:
        # 在指定位置落子，1表示黑子，-1表示白子
        x, y = map(int, cell.split('-')[1:])
        if self.board[x][y] == 0:
            self.board[x][y] = 1 if user.get_IsBlack() else -1
            self.steps += 1
            return True
        else:
            return False


    def checkWin(self):
        # Every 5 continuous pieces has one highest then leftmost piece.
        # Then traversing every point with four patterns can simultaneously traverse any possible winning patterns.
        for i in range(10):
            for j in range(10):
                # east line
                if j < 6 and abs(sum([self.board[i][j + k] for k in range(5)])) == 5: return self.board[i][j]
                # southeast line
                if i < 6 and j < 6 and abs(sum([self.board[i+k][j+k] for k in range(5)])) == 5: return self.board[i][j]
                # south line
                if i < 6 and abs(sum([self.board[i+k][j] for k in range(5)])) == 5: return self.board[i][j]
                # southwest line
                if i < 6 and j > 3 and abs(sum([self.board[i+k][j-k] for k in range(5)])) == 5: return self.board[i][j]
        return None


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

    def getRoom(self, room_id: str) -> Room | None:
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
                return self.rooms[room_id]
            else:
                return None


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
    db = get_db()
    user = db.execute(
        'SELECT * FROM user WHERE id = ?', (userId,)
    ).fetchone()
    user_in_game = UserInGame(int(user['id']), user['username'], IsBlack=False)
    room: Room = roomManager.getAvailRoom()
    if room:
        # 如果找到了空闲房间，可以直接开始游戏
        room.addUser(user_in_game)
        # room.setRoomId(str(room.getRoomId()) + "-" + str(userId))
        # roomManager.updateRoom(room.getRoomId(), room)
        emit("joinSuccess", {
            "user1Name": room.get_user1().get_username(),
            "user2Name": room.get_user2().get_username(),
            "roomId": room.getRoomId(),
            "userId": user_in_game.get_userID(),
            "userName": user_in_game.get_username(),
            "IsBlack": user_in_game.get_IsBlack(),
        })
    else:
        # 如果没有空闲房间，需要进行新建
        global room_cnt
        room = roomManager.createRoom(str(room_cnt))
        room_cnt = room_cnt + 1
        user_in_game.set_IsBlack(True)
        room.addUser(user_in_game)
        i = 0
        while not room.isFull():
            i = i + 1
            time.sleep(1)
            emit("joinWait", {"time": i})
            if i > WAIT_TIME:
                break
        if i <= WAIT_TIME:
            emit("joinSuccess", {
                "user1Name": room.get_user1().get_username(),
                "user2Name": room.get_user2().get_username(),
                "roomId": room.getRoomId(),
                "userId": user_in_game.get_userID(),
                "userName": user_in_game.get_username(),
                "IsBlack": user_in_game.get_IsBlack(),
            })
        else:
            roomManager.removeRoom(room.getRoomId())
            emit("joinFail")


@app.route("/game", methods=["POST"])
def game():
    # 游戏界面的渲染
    roomId = request.form.get("roomId")
    userId = request.form.get("userId")
    room: Room = roomManager.getRoom(roomId)
    user = room.get_user_by_id(userId)
    IsBlack = user.get_IsBlack()
    # userName = request.form.get("userName")
    # first = request.form.get("first")
    return render_template(
        "gamePart/game.html",
        user1Name=room.get_user1().get_username(),
        user2Name=room.get_user2().get_username(),
        roomId=roomId,
        userId=userId,
        userName=user.get_username(),
        IsBlack=IsBlack,
    )


@socketio.on("start")
def handleStart(data):
    # 处理游戏初始化时的客户端状态
    join_room(data["roomId"])
    room = roomManager.getRoom(data["roomId"])
    user = room.get_user_by_id(data["userId"])

    if user.get_IsBlack():
        # 执黑方先下棋
        emit("updateBoard", {"id": user.get_userID()}, room=data["roomId"])

@socketio.on("move")
def handleMove(data):
    room = roomManager.getRoom(data["roomId"])
    user = room.get_user_by_id(data["userId"])

    # handle the move's image.
    if room.playChess(data["place"], user):
        # Phase 1: tentative first player places three stones, two black and one white.
        if room.getSteps() <= 2:
            emit(
                "updateBoard",
                {
                    "place": data["place"],
                    "IsBlack": user.get_IsBlack(),
                    "id": user.get_userID(), # Next move user is the same.
                    "msg": "假先方任下三手",
                },
                room=data["roomId"]
            )
            user.rotate_black()

        # Tentative second player choose: black, white or places two stones and let opposite choose.
        elif room.getSteps() == 3:
            other_user = room.get_another_user(user)
            emit("updateBoard",
                 {"place": data["place"], "IsBlack": user.get_IsBlack()}, room=data["roomId"])
            emit("phase1Choose",
                 {"id": other_user.get_userID(), "msg": "假后方选择"}, room=data["roomId"])

        # Phase 2: tentative second player places two stones, one black and one white.
        elif room.isInPrePhase():
            if room.getSteps() <= 4:
                emit(
                    "updateBoard",
                    {
                        "place": data["place"],
                        "IsBlack": user.get_IsBlack(),
                        "id": user.get_userID(),  # Next move user is the same.
                        "msg": "假后方任下两手",
                    },
                    room=data["roomId"]
                )
                user.rotate_black()
            elif room.getSteps() == 5:
                other_user = room.get_another_user(user)
                emit("updateBoard",
                     {"place": data["place"], "IsBlack": user.get_IsBlack()}, room=data["roomId"])
                emit("phase2Choose",
                     {"id": other_user.get_userID(), "msg": "假先方选择"}, room=data["roomId"])
            else: raise RuntimeError("Already placed 5 stones, but not get in normal phase.")

        # Normal play.
        else:
            other_user = room.get_another_user(user)
            result = room.checkWin()
            if result:  # this user win!
                db = get_db()
                db.execute(
                    'UPDATE user SET totalGame = totalGame + 1 WHERE id IN (?, ?)',
                    (user.get_userID(), other_user.get_userID())
                )
                db.execute(
                    'UPDATE user SET winGame = winGame + 1 WHERE id = ?',
                    (user.get_userID(),)
                )
                db.commit()
                emit("updateBoard",{"place": data["place"], "IsBlack": user.get_IsBlack(),}, room=data["roomId"])
                emit("GameOver", user.get_userID(), room=data["roomId"])
            else:
                emit(
                    "updateBoard",
                    {
                        "place": data["place"],
                        "IsBlack": user.get_IsBlack(),
                        "id": other_user.get_userID(),  # Next move user is another user.
                        "msg": "黑方回合" if other_user.get_IsBlack() else "白方回合",
                    },
                    room=data["roomId"]
                )
                if room.getSteps() > DRAW_ROUND:
                    emit("draw", room=room.getRoomId())


@socketio.on("chooseBlack")
def handleChooseBlack(data):
    room = roomManager.getRoom(data["roomId"])
    user = room.get_user_by_id(data["userId"])
    other_user = room.get_another_user(user)
    IsBlack = data["IsBlack"]

    user.set_IsBlack(IsBlack)
    other_user.set_IsBlack(not IsBlack)
    room.setInPrePhase(False)
    # When the player choose white, then he can place, because there are BWB or BWBWB on the board, the next is W.
    # B: Black; W: White
    emit(
        "updateBoard",
        {
            "id": user.get_userID() if not IsBlack else other_user.get_userID(),
            "msg": "选择黑方" if IsBlack else "选择白方",
            "user1_msg": f"用户名：{room.get_user1().get_username()}（{'黑' if room.get_user1().get_IsBlack() else '白'}子）",
            "user2_msg": f"用户名：{room.get_user2().get_username()}（{'黑' if room.get_user2().get_IsBlack() else '白'}子）",
            "clear": True,
        },
        room=data["roomId"]
    )


@socketio.on("choosePhase2")
def handleChoosePhase2(data):
    room = roomManager.getRoom(data["roomId"])
    user = room.get_user_by_id(data["userId"])
    # user.set_IsBlack(True)
    emit(
        "updateBoard",
        {
            "id": user.get_userID(),  # Next move user is the same.
            "msg": "假后方任下两手",
            "clear": True,
        },
        room=data["roomId"]
    )


@socketio.on("applyDraw")
def applyDraw(data):
    # 申请和局
    roomId = data["roomId"]
    userId = data["userId"]
    emit("apply", {"userId": userId}, room=roomId)


@socketio.on("acceptApply")
def acceptApply(data):
    # 接受和局
    roomId = data["roomId"]
    emit("drawn", room=roomId)
    room = roomManager.getRoom(roomId)

    db = get_db()
    db.execute(
        'UPDATE user SET totalGame = totalGame + 1 WHERE id IN (?, ?)',
        (room.get_user1().get_userID(), room.get_user2().get_userID())
    )
    db.commit()


@socketio.on("rejectApply")
def rejectApply(data):
    # 拒绝和局
    emit("rejected", {"userId": data["userId"]}, room=data["roomId"])


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
        socketio.emit("timeout", room=data["roomId"])
    if data["userId"] == room.get_user1().get_userID():
        room.setUser1Heartbeat(time.time())
    else:
        room.setUser2Heartbeat(time.time())


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
