from asyncio import set_event_loop
import os
import sys
import numpy as np
import cv2
import tkinter as tk
import tkinter.scrolledtext
from tkinter import filedialog
import tkinter.font as font
from PIL import Image, ImageTk
import threading
import datetime
from time import sleep
import time 

class Application(tk.Frame):
    def __init__(self,master,video_source=0):
        super().__init__(master)
        self.pack()
        self.master.geometry("1000x700")
        self.master.title("test")
        self.judge = 0
        self.cam_res = False
        #font
        self.font_attention = font.Font(self.master, family="Meiryo UI",size=12)
        self.font_frame = font.Font( family="Meiryo UI", size=12, weight="normal" )
        self.font_btn_big = font.Font( family="Meiryo UI", size=20, weight="normal" )
        self.font_btn_small = font.Font( family="Meiryo UI", size=12, weight="normal" )
        self.font_lbl_bigger = font.Font( family="Meiryo UI", size=45, weight="normal" )
        self.font_lbl_big = font.Font( family="Meiryo UI", size=30, weight="normal" )
        self.font_lbl_middle = font.Font( family="Meiryo UI", size=15, weight="normal" )
        self.font_lbl_small = font.Font( family="Meiryo UI", size=12, weight="normal" )
        #open video 
        self.vcap = cv2.VideoCapture( video_source )
        self.width = self.vcap.get( cv2.CAP_PROP_FRAME_WIDTH )
        self.height = self.vcap.get( cv2.CAP_PROP_FRAME_HEIGHT )
        #widget
        self.create_widgets()
        #canvas update
        self.video_update()

    def create_widgets(self):

        #Frame_Camera
        self.frame_cam = tk.LabelFrame(self.master, text = 'Screen', font=self.font_frame)
        self.frame_cam.place(x = 20, y = 150)
        self.frame_cam.configure(width = self.width+30, height = self.height+50)
        self.frame_cam.grid_propagate(0)
        #Canvas
        self.canvas = tk.Canvas(self.frame_cam)
        self.canvas.configure( width= self.width, height=self.height)
        self.canvas.grid(column= 0, row=0,padx = 10, pady=10)

        #Frame_Button
        self.frame_btn = tk.LabelFrame( self.master, text='Control', font=self.font_frame )
        self.frame_btn.place(x = 20, y = 30 )
        self.frame_btn.configure( width=self.width + 30, height= 120 )
        self.frame_btn.grid_propagate( 0 )

        #Snapshot Button
        self.btn_snapshot = tk.Button( self.frame_btn, text='Snapshot', font=self.font_btn_small)
        self.btn_snapshot.configure(width = 10, height = 1, command=self.press_snapshot_button)
        self.btn_snapshot.grid(column=0, row=0, padx=10, pady= 10)

        #Close
        self.btn_close = tk.Button( self.frame_btn, text='Close', font=self.font_btn_small)
        self.btn_close.configure( width=10, height=1, command=self.press_close_button )
        self.btn_close.grid( column=1, row=0, padx=10, pady=10 )

        #Detection
        self.btn_detection = tk.Button( self.frame_btn, text='Detection', font=self.font_btn_small)
        self.btn_detection.configure( width=10, height=1, command=self.press_detection_button )
        self.btn_detection.grid( column=2, row=0, padx=10, pady=10 )

        #Trim
        self.btn_trim = tk.Button( self.frame_btn, text='Trim', font=self.font_btn_small)
        self.btn_trim.configure( width=10, height=1, command=self.press_trim_button )
        self.btn_trim.grid( column=3, row=0, padx=10, pady=10 )

    #Videoアップデート関数
    def video_update(self):
        ret, frame_org = self.vcap.read()
        if self.cam_res == False:
            if ret == False:
                frame_org = np.zeros((640, 480, 3), np.uint8)
            self.frame_resize = cv2.resize(frame_org , (640, 480) )
            if self.judge == 0:
                self.frame_rgb = cv2.cvtColor(self.frame_resize, cv2.COLOR_BGR2RGB) # imreadはBGRなのでRGBに変換
                self.frame_pil = Image.fromarray(self.frame_rgb) # RGBからPILフォーマットへ変換
                self.frame_tk  = ImageTk.PhotoImage(self.frame_pil) # ImageTkフォーマットへ変換
            else:
                self.res = cv2.matchTemplate(self.img_target,self.frame_resize,self.method)
                self.loc = np.where(self.res >= self.threshold)
                self.results = self.frame_resize.copy()
                if len(self.loc[0]) != 0:
                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(self.res)
                    h = self.img_target.shape[0]
                    w = self.img_target.shape[1]
                    if self.method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
                        top_left = min_loc
                        exe_val = min_val
                    else:
                        top_left = max_loc
                        exe_val = max_val
                    bottom_right = (top_left[0] + w, top_left[1] + h)
                    self.results =  cv2.rectangle(self.frame_resize, top_left, bottom_right, (0, 255, 0), 10) 
                self.frame_rgb = cv2.cvtColor(self.results, cv2.COLOR_BGR2RGB) # imreadはBGRなのでRGBに変換
                self.frame_pil = Image.fromarray(self.frame_rgb) # RGBからPILフォーマットへ変換
                self.frame_tk  = ImageTk.PhotoImage(self.frame_pil) # ImageTkフォーマットへ変換
    
        self.canvas.create_image(0, 0, image=self.frame_tk, anchor='nw',tag="image")
        self.after_id = self.master.after(15, self.video_update)

    #スナップショット撮影ボタン
    def press_snapshot_button(self):
        ret, frame_org = self.vcap.read()
        if ret == False:
            frame_org = np.zeros((640, 480, 3), np.uint8)
        frame_resize = cv2.resize(frame_org , (640, 480) )
        frame_rgb = cv2.cvtColor(frame_resize, cv2.COLOR_BGR2RGB)
        cv2.imwrite( "frame-" + time.strftime( "%Y-%d-%m-%H-%M-%S" ) + ".jpg",cv2.cvtColor( frame_rgb, cv2.COLOR_BGR2RGB ) )        

    #ターゲットの読み込み
    def press_detection_button(self):
        if self.judge == 0:
            self.judge = 1
            self.method = eval('cv2.TM_CCOEFF_NORMED')
            self.img_target = cv2.imread("trimming_img.png")
            self.threshold = 0.5
        else:
            self.judge = 0

    #Closeボタン
    def press_close_button(self):
        self.master.destroy()
        self.vcap.release()

    #トリミング関数
    def press_trim_button(self):
        if self.cam_res == False:
            self.cam_res = True
            self.master.after_cancel(self.after_id)
            self.selection = []
            self.set_events()
            # self.img_draw()
        else:
            self.cam_res = False
            self.after_id = self.master.after(15, self.video_update)

    def img_draw(self):
        selection = [226,92,510,434]
        self.canvas.create_rectangle(
            selection[0],
            selection[1],
            selection[2],
            selection[3],
            outline="red",
            width=3,
            tag="selection_rectangle"
        )
        
    def draw_selection(self, selection):
        '選択範囲を描画'

        self.delete_selection()

        if selection:
            # 選択範囲を長方形で描画
            self.canvas.create_rectangle(
                selection[0],
                selection[1],
                selection[2],
                selection[3],
                outline="red",
                width=3,
                tag="selection_rectangle"
            )

    def delete_selection(self):
        '選択範囲表示用オブジェクトを削除する'

        # キャンバスに描画済みの選択範囲を削除
        objs = self.canvas.find_withtag("selection_rectangle")
        for obj in objs:
            self.canvas.delete(obj)

    def set_events(self):
        '受け付けるイベントを設定する'
        self.pressing = False
        self.selection = None
        # キャンバス上のマウス押し下げ開始イベント受付
        self.canvas.bind(
            "<ButtonPress>",
            self.button_press
        )

        # キャンバス上のマウス動作イベント受付
        self.canvas.bind(
            "<Motion>",
            self.mouse_motion,
        )

        # キャンバス上のマウス押し下げ終了イベント受付
        self.canvas.bind(
            "<ButtonRelease>",
            self.button_release,
        )

        # 画像の描画用のタイマーセット
        self.master.after(15, self.timer)

    def timer(self):
        '一定間隔で画像等を描画'
        # トリミング選択範囲を左側のキャンバスに描画
        self.draw_selection(
            self.selection,
        )

        # 再度タイマー設定
        self.master.after(10, self.timer)

    def button_press(self, event):
        'マウスボタン押し下げ開始時の処理'

        # マウスクリック中に設定
        self.pressing = True

        self.selection = None

        # 現在のマウスでの選択範囲を設定
        self.selection = [
            event.x,
            event.y,
            event.x,
            event.y
        ]

        # 選択範囲を表示するオブジェクトを削除
        self.delete_selection()

    def mouse_motion(self, event):
        'マウスボタン移動時の処理'

        if self.pressing:
            # マウスでの選択範囲を更新
            self.selection[2] = event.x
            self.selection[3] = event.y

    def button_release(self, event):
        'マウスボタン押し下げ終了時の処理'

        if self.pressing:

            # マウスボタン押し下げ終了
            self.pressing = False

            # マウスでの選択範囲を更新
            self.selection[2] = event.x
            self.selection[3] = event.y

            # 画像の描画位置を取得
            objs = self.canvas.find_withtag("image")
            if len(objs) != 0:
                draw_coord = self.canvas.coords(objs[0])

                # 選択範囲をキャンバス上の座標から画像上の座標に変換
                x1 = self.selection[0] - draw_coord[0]
                y1 = self.selection[1] - draw_coord[1]
                x2 = self.selection[2] - draw_coord[0]
                y2 = self.selection[3] - draw_coord[1]

                # 画像をcropでトリミング
                self.crop(
                    (int(x1), int(y1), int(x2), int(y2))
                )

    def crop(self,param):
        x1, y1, x2, y2 = param
        self.trim_img = self.frame_pil.crop((x1,y1,x2,y2))
        self.trim_img.save("trimming_img.png")
        # cv2.imwrite("triming_test.jpg",self.trim_img)
        # print("トリミングが完了しました")

def main():
    root = tk.Tk()
    app = Application(master=root)
    app.mainloop()
    
if __name__ == "__main__":
    main()