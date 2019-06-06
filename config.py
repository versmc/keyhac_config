import sys
import os
import time

import pyauto
from keyhac import *

"""
keyhac の設定ファイル

問題点
1. 特に致命的なものは確認していない
2. キーボードマクロの動作で time inversion のメッセージが出る
3. とりあえずオブジェクティブなコードにしたが、密結合なのでなんとかしたい
4. IME の設定とか無変換キーを使った設定とかあるので日本語でいいのではないか
"""

"""
動的なキーマップを制御するためのクラス
keymap.defineWindowKeymap(...) の引数 check_func を適当に設定することにより動的キーマップを実現する
本クラスは静的クラスである
本クラスは静的メンバ flag_window により動的なキーマップモードを保持している
"""
class WindowmodeManager:
    window_limited=0
    window_cursor=1
    window_test=2
    flag_window=window_limited  # keymap mode flag


    """
    window のキーバインドモードフラグを limited に変更する
    この関数ではフラグを変更するのみであり、キーマップ自体は変更しない
    """
    @classmethod
    def set_window_limited(cls):
        cls.flag_window=cls.window_limited
    
    
    """
    window のキーバインドモードフラグを cursor に変更する
    この関数ではフラグを変更するのみであり、キーマップ自体は変更しない
    """    
    @classmethod
    def set_window_cursor(cls):
        cls.flag_window=cls.window_cursor

    """
    window のキーバインドモードフラグを test に変更する
    この関数ではフラグを変更するのみであり、キーマップ自体は変更しない
    """    
    @classmethod
    def set_window_test(cls):
        cls.flag_window=cls.window_test

    """
    window のキーバインドモードフラグを確認する関数群
    keymap.defineWindowKeymap の引数 check_func に指定することにより
    動的キー割り当てを実現するために使う
    """    
    @classmethod
    def window_is_limited(cls,window):
        return cls.flag_window==cls.window_limited

    @classmethod
    def window_is_cursor(cls,window):
        return cls.flag_window==cls.window_cursor
    
    @classmethod
    def window_is_emacs(cls,window):
        return window.getText().find("emacs")==0

    @classmethod
    def window_is_test(cls,window):
        return cls.flag_window==cls.window_test


"""
このクラスはキーボードマクロを制御するためのクラス
試作段階
"""
class MyMacro:

    # インスタンス化 keymap を保持させる
    def __init__(self,keymap):
        self.keymap=keymap
    


    """
    keymap を通して "abcde" と 0.5 sec おきに入力する関数
    この関数を直接キー入力に割り当てると意図したように動作しない

    現象としては実行中にキー入力が割り込む
    おそらく本関数のように実行に時間のかかる関数をキーに割り当てた場合、
    実行の終了以前にキー入力がなされる
    """
    def abcde_raw(self):
        self.keymap.InputKeyCommand("a")()
        time.sleep(0.5)
        self.keymap.InputKeyCommand("b")()
        time.sleep(0.5)
        self.keymap.InputKeyCommand("c")()
        time.sleep(0.5)
        self.keymap.InputKeyCommand("d")()
        time.sleep(0.5)
        self.keymap.InputKeyCommand("e")()


    """
    keymap を通して "abcde" と 0.5 sec おきに入力する関数
    keymap.delayedCall(...) を使って呼ぶ
    
    ひとまず意図した動作を行う
    
    しかし、
    Time stamp inversion happened.
    のメッセージが表示される
    入力キーの up イベントが関数終了後に行われている
    
    """
    def abcde_delay(self):
        self.keymap.delayedCall(self.abcde_raw,0)


"""
このクラスはキーマップを設定するためのクラス
内部に keymap クラスの参照を保持する
"""
class KeymapManager:
    
    """
    コンストラクタ
    本クラスはコンストラクタで keymap の設定を行う
    構築時には keymap の設定は終了している
    """
    def __init__(self,keymap_):
        self.keymap=keymap_
    
        # define modifier
        self.keymap.defineModifier(29,"User1")       #assign "muhenkan" "User1"
        self.keymap.defineModifier("Slash","User2")  #assign "/" "User2"

        # define dynamic keymap
        self.keymap_global=self.make_keymap_global()
        self.keymap_limited=self.make_keymap_limited()
        self.keymap_cursor=self.make_keymap_cursor()
        self.keymap_emacs=self.make_keymap_emacs()
        self.keymap_test=self.make_keymap_test()

    """
    keymap で割り当てるための便利関数
    """

    # IME ON
    def set_ime_on(self):
        self.keymap.wnd.setImeStatus(1)
    
    # IME OFF
    def set_ime_off(self):
        self.keymap.wnd.setImeStatus(0)
    

    """
    WindowmodeManager を用いたキーマップのモード切替を行うクラス群
    WindowmodeManager の持つフラグを変更し、キーバインドをアップデートする
    """
    
    def set_keymap_limited(self):
        WindowmodeManager.set_window_limited()
        self.keymap.updateKeymap()

    def set_keymap_cursor(self):
        WindowmodeManager.set_window_cursor()
        self.keymap.updateKeymap()

    def set_keymap_test(self):
        WindowmodeManager.set_window_test()
        self.keymap.updateKeymap()

    def set_keymap_limited_and_ime_on(self):
        self.set_keymap_limited()
        self.set_ime_on()

    def set_keymap_limited_and_ime_off(self):
        self.set_keymap_limited()
        self.set_ime_off()


    """
    各キーマップを生成して返す関数群
    """

    def make_keymap_global(self):
        return self.keymap.defineWindowKeymap()


    def make_keymap_limited(self):
        # check_func に limited モードかどうかを判定する関数を指定することで動的キー割り当てを実現している
        keymap_limited = self.keymap.defineWindowKeymap(check_func=WindowmodeManager.window_is_limited)
        
        # settings to change mode
        keymap_limited["U1-c"]=self.set_keymap_cursor    # muhenkan - c
        keymap_limited["U1-t"]=self.set_keymap_test      # muhenkan - t

        # settings of some shortcuts
        keymap_limited["A-z"]="A-Tab"
        keymap_limited["A-S-z"]="A-S-Tab"
        keymap_limited["RC-j"]="Enter"
        keymap_limited["RC-h"]="Back"
        keymap_limited["RC-d"]="Delete"
        for any in ("", "S-", "C-", "C-S-", "A-", "A-S-", "A-C-", "A-C-S-", "W-", "W-S-", "W-C-", "W-C-S-", "W-A-", "W-A-S-", "W-A-C-", "W-A-C-S-"):
            keymap_limited[any+"O-Slash"]=any+"Slash"
            keymap_limited[any+"U1-i"]=any+"Up"
            keymap_limited[any+"U1-j"]=any+"Left"
            keymap_limited[any+"U1-k"]=any+"Down"
            keymap_limited[any+"U1-l"]=any+"Right"
            keymap_limited[any+"U1-u"]=any+"PageUp"
            keymap_limited[any+"U1-h"]=any+"Home"
            keymap_limited[any+"U1-o"]=any+"PageDown"
            keymap_limited[any+"U1-Semicolon"]=any+"End"
            keymap_limited[any+"U1-n"]=any+"Enter"
            keymap_limited[any+"U1-m"]=any+"Tab"
        
        return keymap_limited
                
    def make_keymap_cursor(self):
        # check_func に cursor モードかどうかを判定する関数を指定することで動的キー割り当てを実現している
        keymap_cursor = self.keymap.defineWindowKeymap(check_func=WindowmodeManager.window_is_cursor)

        # settings of keymap_cursor
        # カーソルモード ijkl による移動などが楽になる 最近あまり使わない
        keymap_cursor["S-(241)"]=self.set_keymap_limited_and_ime_on  #Shift - katakana/hiragana/romaji
        keymap_cursor["S-(28)"]=self.set_keymap_limited_and_ime_off  #Shift - henkan
        keymap_cursor["(28)"]=self.set_keymap_limited                #henkan
        keymap_cursor["Alt-X"]="Alt-Tab"
        keymap_cursor["x"]="Delete"
        keymap_cursor["S-x"]="Back"
        keymap_cursor["h"]="Back"
        keymap_cursor["w"]="C-Tab"
        keymap_cursor["q"]="C-S-Tab"
        keymap_cursor["O-f"]="LButton"
        keymap_cursor["O-g"]="RButton"
        
        for any in ("", "S-", "C-", "C-S-", "A-", "A-S-", "A-C-", "A-C-S-", "W-", "W-S-", "W-C-", "W-C-S-", "W-A-", "W-A-S-", "W-A-C-", "W-A-C-S-"):
            keymap_cursor[any+"i"]=any+"Up"
            keymap_cursor[any+"j"]=any+"Left"
            keymap_cursor[any+"k"]=any+"Down"
            keymap_cursor[any+"l"]=any+"Right"

            keymap_cursor[any+"u"]=any+"Home"
            keymap_cursor[any+"o"]=any+"End"

            keymap_cursor[any+"U2-j"]=any+"Home"
            keymap_cursor[any+"U2-k"]=any+"PageDown"
            keymap_cursor[any+"U2-i"]=any+"PageUp"
            keymap_cursor[any+"U2-l"]=any+"End"
            
            keymap_cursor[any+"n"]=any+"Enter"
            keymap_cursor[any+"m"]=any+"Tab"
        
        return keymap_cursor
        
    def make_keymap_emacs(self):
        """
        emacs モードの設定
        emacs においても windows のキーバインドで操作するための設定
        emacs において LCtrl によるコマンドを windows のもので置き換える

        現在、レジストリによって CapsLock を RCtrl に変えているため emacs 本来のCtrl の役割は CapsLock キーにより利用する
        代わりに LCtrl による操作では windows のショートカットをエミュレートする
        
        思いついたときに加えていく方針
        """

        keymap_emacs=self.keymap.defineWindowKeymap(check_func=WindowmodeManager.window_is_emacs)

        keymap_emacs["LC-a"]="C-x","h"          # select all
        keymap_emacs["LC-c"]="A-w"              # copy to clipboard
        keymap_emacs["LC-f"]="C-s"              # find
        keymap_emacs["LC-h"]="A-S-5"            # replace
        keymap_emacs["LC-s"]="C-x","C-s"        # save
        keymap_emacs["LC-v"]="C-y"              # paste
        keymap_emacs["LC-x"]="C-w"              # cut
        keymap_emacs["LC-z"]="C-x","u"          # undo (redo は emacs では undo で代用する)

        return keymap_emacs

    def make_keymap_test(self):
        """
        テスト用キーマップモード
        現在はキーボードマクロのテストを実装している
        """
        keymap_test=self.keymap.defineWindowKeymap(check_func=WindowmodeManager.window_is_test)

        keymap_test["S-(241)"]=self.set_keymap_limited_and_ime_on  #Shift - katakana/hiragana/romaji
        keymap_test["S-(28)"]=self.set_keymap_limited_and_ime_off  #Shift - henkan
        keymap_test["(28)"]=self.set_keymap_limited                #henkan
        
        # マクロテスト
        if 1:            
            my_macro=MyMacro(self.keymap)
            keymap_test["U1-q"]=my_macro.abcde_delay  # 意図したとおり動くが time stamp inversion のメッセージが出る
            # keymap_limited["U1-p"]=my_macro.abcde_raw  # 意図したとおり動かない
        return keymap_test





"""
自分用の設定
"""
def my_configure(keymap):
    keymapmanager=KeymapManager(keymap)



"""
設定
基本的には my_configure(keymap)だけ呼んであとはスキップする
デフォルト設定ファイルをできるだけ保存しておくためにこのようにしている
"""
def configure(keymap):

    # --------------------------------------------------------------------
    # Text editer setting for editting config.py file

    # Setting with program file path (Simple usage)
    if 1:
        keymap.editor = "C:\Program Files\Microsoft VS Code\Code.exe"

    # Setting with callable object (Advanced usage)
    if 0:
        def editor(path):
            shellExecute( None, "notepad.exe", '"%s"'% path, "" )
        keymap.editor = editor

    # --------------------------------------------------------------------
    # Customizing the display

    # Font
    keymap.setFont( "MS Gothic", 12 )

    # Theme
    keymap.setTheme("black")

    # --------------------------------------------------------------------

    # My Definition
    if 1:   # limited mode and cursor mode (vim like) move with IJKL
        my_configure(keymap)

        


    # Simple key replacement
    
    # User modifier key definition
    keymap.defineModifier( "CapsLock", "User0" )

    # Global keymap which affects any windows
    if 0:
        keymap_global = keymap.defineWindowKeymap()

        # USER0-Up/Down/Left/Right : Move active window by 10 pixel unit
        keymap_global[ "U0-Left"  ] = keymap.MoveWindowCommand( -10, 0 )
        keymap_global[ "U0-Right" ] = keymap.MoveWindowCommand( +10, 0 )
        keymap_global[ "U0-Up"    ] = keymap.MoveWindowCommand( 0, -10 )
        keymap_global[ "U0-Down"  ] = keymap.MoveWindowCommand( 0, +10 )

        # USER0-Shift-Up/Down/Left/Right : Move active window by 1 pixel unit
        keymap_global[ "U0-S-Left"  ] = keymap.MoveWindowCommand( -1, 0 )
        keymap_global[ "U0-S-Right" ] = keymap.MoveWindowCommand( +1, 0 )
        keymap_global[ "U0-S-Up"    ] = keymap.MoveWindowCommand( 0, -1 )
        keymap_global[ "U0-S-Down"  ] = keymap.MoveWindowCommand( 0, +1 )

        # USER0-Ctrl-Up/Down/Left/Right : Move active window to screen edges
        keymap_global[ "U0-C-Left"  ] = keymap.MoveWindowToMonitorEdgeCommand(0)
        keymap_global[ "U0-C-Right" ] = keymap.MoveWindowToMonitorEdgeCommand(2)
        keymap_global[ "U0-C-Up"    ] = keymap.MoveWindowToMonitorEdgeCommand(1)
        keymap_global[ "U0-C-Down"  ] = keymap.MoveWindowToMonitorEdgeCommand(3)

        # Clipboard history related
        keymap_global[ "C-S-Z"   ] = keymap.command_ClipboardList     # Open the clipboard history list
        keymap_global[ "C-S-X"   ] = keymap.command_ClipboardRotate   # Move the most recent history to tail
        keymap_global[ "C-S-A-X" ] = keymap.command_ClipboardRemove   # Remove the most recent history
        keymap.quote_mark = "> "                                      # Mark for quote pasting

        # Keyboard macro
        keymap_global[ "U0-0" ] = keymap.command_RecordToggle
        keymap_global[ "U0-1" ] = keymap.command_RecordStart
        keymap_global[ "U0-2" ] = keymap.command_RecordStop
        keymap_global[ "U0-3" ] = keymap.command_RecordPlay
        keymap_global[ "U0-4" ] = keymap.command_RecordClear


    # USER0-F1 : Test of launching application
    if 0:
        keymap_global[ "U0-F1" ] = keymap.ShellExecuteCommand( None, "notepad.exe", "", "" )


    # USER0-F2 : Test of sub thread execution using JobQueue/JobItem
    if 0:
        def command_JobTest():

            def jobTest(job_item):
                shellExecute( None, "notepad.exe", "", "" )

            def jobTestFinished(job_item):
                print( "Done." )

            job_item = JobItem( jobTest, jobTestFinished )
            JobQueue.defaultQueue().enqueue(job_item)

        keymap_global[ "U0-F2" ] = command_JobTest


    # Test of Cron (periodic sub thread procedure)
    if 0:
        def cronPing(cron_item):
            os.system( "ping -n 3 www.google.com" )

        cron_item = CronItem( cronPing, 3.0 )
        CronTable.defaultCronTable().add(cron_item)


    # USER0-F : Activation of specific window
    if 0:
        keymap_global[ "U0-F" ] = keymap.ActivateWindowCommand( "cfiler.exe", "CfilerWindowClass" )


    # USER0-E : Activate specific window or launch application if the window doesn't exist
    if 0:
        def command_ActivateOrExecuteNotepad():
            wnd = Window.find( "Notepad", None )
            if wnd:
                if wnd.isMinimized():
                    wnd.restore()
                wnd = wnd.getLastActivePopup()
                wnd.setForeground()
            else:
                executeFunc = keymap.ShellExecuteCommand( None, "notepad.exe", "", "" )
                executeFunc()

        keymap_global[ "U0-E" ] = command_ActivateOrExecuteNotepad


    # Ctrl-Tab : Switching between console related windows
    if 0:

        def isConsoleWindow(wnd):
            if wnd.getClassName() in ("PuTTY","MinTTY","CkwWindowClass"):
                return True
            return False

        keymap_console = keymap.defineWindowKeymap( check_func=isConsoleWindow )

        def command_SwitchConsole():

            root = pyauto.Window.getDesktop()
            last_console = None

            wnd = root.getFirstChild()
            while wnd:
                if isConsoleWindow(wnd):
                    last_console = wnd
                wnd = wnd.getNext()

            if last_console:
                last_console.setForeground()

        keymap_console[ "C-TAB" ] = command_SwitchConsole


    # USER0-Space : Application launcher using custom list window
    if 0:
        def command_PopApplicationList():

            # If the list window is already opened, just close it
            if keymap.isListWindowOpened():
                keymap.cancelListWindow()
                return

            def popApplicationList():

                applications = [
                    ( "Notepad", keymap.ShellExecuteCommand( None, "notepad.exe", "", "" ) ),
                    ( "Paint", keymap.ShellExecuteCommand( None, "mspaint.exe", "", "" ) ),
                ]

                websites = [
                    ( "Google", keymap.ShellExecuteCommand( None, "https://www.google.co.jp/", "", "" ) ),
                    ( "Facebook", keymap.ShellExecuteCommand( None, "https://www.facebook.com/", "", "" ) ),
                    ( "Twitter", keymap.ShellExecuteCommand( None, "https://twitter.com/", "", "" ) ),
                ]

                listers = [
                    ( "App",     cblister_FixedPhrase(applications) ),
                    ( "WebSite", cblister_FixedPhrase(websites) ),
                ]

                item, mod = keymap.popListWindow(listers)

                if item:
                    item[1]()

            # Because the blocking procedure cannot be executed in the key-hook,
            # delayed-execute the procedure by delayedCall().
            keymap.delayedCall( popApplicationList, 0 )

        keymap_global[ "U0-Space" ] = command_PopApplicationList


    # USER0-Alt-Up/Down/Left/Right/Space/PageUp/PageDown : Virtul mouse operation by keyboard
    if 0:
        keymap_global[ "U0-A-Left"  ] = keymap.MouseMoveCommand(-10,0)
        keymap_global[ "U0-A-Right" ] = keymap.MouseMoveCommand(10,0)
        keymap_global[ "U0-A-Up"    ] = keymap.MouseMoveCommand(0,-10)
        keymap_global[ "U0-A-Down"  ] = keymap.MouseMoveCommand(0,10)
        keymap_global[ "D-U0-A-Space" ] = keymap.MouseButtonDownCommand('left')
        keymap_global[ "U-U0-A-Space" ] = keymap.MouseButtonUpCommand('left')
        keymap_global[ "U0-A-PageUp" ] = keymap.MouseWheelCommand(1.0)
        keymap_global[ "U0-A-PageDown" ] = keymap.MouseWheelCommand(-1.0)
        keymap_global[ "U0-A-Home" ] = keymap.MouseHorizontalWheelCommand(-1.0)
        keymap_global[ "U0-A-End" ] = keymap.MouseHorizontalWheelCommand(1.0)


    # Execute the System commands by sendMessage
    if 0:
        def close():
            wnd = keymap.getTopLevelWindow()
            wnd.sendMessage( WM_SYSCOMMAND, SC_CLOSE )

        def screenSaver():
            wnd = keymap.getTopLevelWindow()
            wnd.sendMessage( WM_SYSCOMMAND, SC_SCREENSAVE )

        keymap_global[ "U0-C" ] = close              # Close the window
        keymap_global[ "U0-S" ] = screenSaver        # Start the screen-saver


    # Test of text input
    if 0:
        keymap_global[ "U0-H" ] = keymap.InputTextCommand( "Hello / こんにちは" )


    # For Edit box, assigning Delete to C-D, etc
    if 0:
        keymap_edit = keymap.defineWindowKeymap( class_name="Edit" )

        keymap_edit[ "C-D" ] = "Delete"              # Delete
        keymap_edit[ "C-H" ] = "Back"                # Backspace
        keymap_edit[ "C-K" ] = "S-End","C-X"         # Removing following text


    # Customize Notepad as Emacs-ish
    # Because the keymap condition of keymap_edit overlaps with keymap_notepad,
    # both these two keymaps are applied in mixed manner.
    if 0:
        keymap_notepad = keymap.defineWindowKeymap( exe_name="notepad.exe", class_name="Edit" )

        # Define Ctrl-X as the first key of multi-stroke keys
        keymap_notepad[ "C-X" ] = keymap.defineMultiStrokeKeymap("C-X")

        keymap_notepad[ "C-P" ] = "Up"                  # Move cursor up
        keymap_notepad[ "C-N" ] = "Down"                # Move cursor down
        keymap_notepad[ "C-F" ] = "Right"               # Move cursor right
        keymap_notepad[ "C-B" ] = "Left"                # Move cursor left
        keymap_notepad[ "C-A" ] = "Home"                # Move to beginning of line
        keymap_notepad[ "C-E" ] = "End"                 # Move to end of line
        keymap_notepad[ "A-F" ] = "C-Right"             # Word right
        keymap_notepad[ "A-B" ] = "C-Left"              # Word left
        keymap_notepad[ "C-V" ] = "PageDown"            # Page down
        keymap_notepad[ "A-V" ] = "PageUp"              # page up
        keymap_notepad[ "A-Comma" ] = "C-Home"          # Beginning of the document
        keymap_notepad[ "A-Period" ] = "C-End"          # End of the document
        keymap_notepad[ "C-X" ][ "C-F" ] = "C-O"        # Open file
        keymap_notepad[ "C-X" ][ "C-S" ] = "C-S"        # Save
        keymap_notepad[ "C-X" ][ "C-W" ] = "A-F","A-A"  # Save as
        keymap_notepad[ "C-X" ][ "U" ] = "C-Z"          # Undo
        keymap_notepad[ "C-S" ] = "C-F"                 # Search
        keymap_notepad[ "A-X" ] = "C-G"                 # Jump to specified line number
        keymap_notepad[ "C-X" ][ "H" ] = "C-A"          # Select all
        keymap_notepad[ "C-W" ] = "C-X"                 # Cut
        keymap_notepad[ "A-W" ] = "C-C"                 # Copy
        keymap_notepad[ "C-Y" ] = "C-V"                 # Paste
        keymap_notepad[ "C-X" ][ "C-C" ] = "A-F4"       # Exit


    # Customizing clipboard history list
    if 1:
        # Enable clipboard monitoring hook (Default:Enabled)
        keymap.clipboard_history.enableHook(True)

        # Maximum number of clipboard history (Default:1000)
        keymap.clipboard_history.maxnum = 1000

        # Total maximum size of clipboard history (Default:10MB)
        keymap.clipboard_history.quota = 10*1024*1024

        # Fixed phrases
        fixed_items = [
            ( "name@server.net",     "name@server.net" ),
            ( "Address",             "San Francisco, CA 94128" ),
            ( "Phone number",        "03-4567-8901" ),
        ]

        # Return formatted date-time string
        def dateAndTime(fmt):
            def _dateAndTime():
                return datetime.datetime.now().strftime(fmt)
            return _dateAndTime

        # Date-time
        datetime_items = [
            ( "YYYY/MM/DD HH:MM:SS",   dateAndTime("%Y/%m/%d %H:%M:%S") ),
            ( "YYYY/MM/DD",            dateAndTime("%Y/%m/%d") ),
            ( "HH:MM:SS",              dateAndTime("%H:%M:%S") ),
            ( "YYYYMMDD_HHMMSS",       dateAndTime("%Y%m%d_%H%M%S") ),
            ( "YYYYMMDD",              dateAndTime("%Y%m%d") ),
            ( "HHMMSS",                dateAndTime("%H%M%S") ),
        ]

        # Add quote mark to current clipboard contents
        def quoteClipboardText():
            s = getClipboardText()
            lines = s.splitlines(True)
            s = ""
            for line in lines:
                s += keymap.quote_mark + line
            return s

        # Indent current clipboard contents
        def indentClipboardText():
            s = getClipboardText()
            lines = s.splitlines(True)
            s = ""
            for line in lines:
                if line.lstrip():
                    line = " " * 4 + line
                s += line
            return s

        # Unindent current clipboard contents
        def unindentClipboardText():
            s = getClipboardText()
            lines = s.splitlines(True)
            s = ""
            for line in lines:
                for i in range(4+1):
                    if i>=len(line) : break
                    if line[i]=='\t':
                        i+=1
                        break
                    if line[i]!=' ':
                        break
                s += line[i:]
            return s

        full_width_chars = "ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ！”＃＄％＆’（）＊＋，−．／：；＜＝＞？＠［￥］＾＿‘｛｜｝～０１２３４５６７８９　"
        half_width_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!\"#$%&'()*+,-./:;<=>?@[\]^_`{|}～0123456789 "

        # Convert to half-with characters
        def toHalfWidthClipboardText():
            s = getClipboardText()
            s = s.translate(str.maketrans(full_width_chars,half_width_chars))
            return s

        # Convert to full-with characters
        def toFullWidthClipboardText():
            s = getClipboardText()
            s = s.translate(str.maketrans(half_width_chars,full_width_chars))
            return s

        # Save the clipboard contents as a file in Desktop directory
        def command_SaveClipboardToDesktop():

            text = getClipboardText()
            if not text: return

            # Convert to utf-8 / CR-LF
            utf8_bom = b"\xEF\xBB\xBF"
            text = text.replace("\r\n","\n")
            text = text.replace("\r","\n")
            text = text.replace("\n","\r\n")
            text = text.encode( encoding="utf-8" )

            # Save in Desktop directory
            fullpath = os.path.join( getDesktopPath(), datetime.datetime.now().strftime("clip_%Y%m%d_%H%M%S.txt") )
            fd = open( fullpath, "wb" )
            fd.write(utf8_bom)
            fd.write(text)
            fd.close()

            # Open by the text editor
            keymap.editTextFile(fullpath)

        # Menu item list
        other_items = [
            ( "Quote clipboard",            quoteClipboardText ),
            ( "Indent clipboard",           indentClipboardText ),
            ( "Unindent clipboard",         unindentClipboardText ),
            ( "",                           None ),
            ( "To Half-Width",              toHalfWidthClipboardText ),
            ( "To Full-Width",              toFullWidthClipboardText ),
            ( "",                           None ),
            ( "Save clipboard to Desktop",  command_SaveClipboardToDesktop ),
            ( "",                           None ),
            ( "Edit config.py",             keymap.command_EditConfig ),
            ( "Reload config.py",           keymap.command_ReloadConfig ),
        ]

        # Clipboard history list extensions
        keymap.cblisters += [
            ( "Fixed phrase", cblister_FixedPhrase(fixed_items) ),
            ( "Date-time", cblister_FixedPhrase(datetime_items) ),
            ( "Others", cblister_FixedPhrase(other_items) ),
        ]

