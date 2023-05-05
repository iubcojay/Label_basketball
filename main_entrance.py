from My_design import *

if __name__ == "__main__":
    app = QApplication(sys.argv)  # QT制作的app，有且只有一个QApplication对象

    show_login = video_player()
    #show_login = video_login()
    #show_login = video_image()

    show_login.show()
    app.exec()  # 进入事件循环，直到退出窗口 
