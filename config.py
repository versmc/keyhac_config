"""
# Config file for [keyhac](https://sites.google.com/site/craftware/keyhac-en?authuser=0)

This scripts are derived from the default config.py in [keyhac](https://sites.google.com/site/craftware/keyhac-en?authuser=0).

## features

- Dynamic keybind
- Cursor movement with ijkl and so on.


## TODO
1. "time inversion" message is given by keyboard macro 

"""

import sys
import os
import time

import pyauto
from keyhac import *





    
class KeymapConfig:
    """This class provide the function to set keymap as `set_keymap(keymap)`. This class is a static class.
    
    Notably, in this class, dynamic keymap is realized by `keymap.defineWindowKeymap(checkfunc = {function to get current mode})`.
    `{function to get current mode}` is provided by KeymapMode class. 
    Mode changes are fired by "key"s, which call functions `KeymapMode.set_xxx()` and `keymap.updateKeymap()`.
    """


    class KeymapMode:
        """This class stores the current keymap mode flag. 
        This class does not change status of `keymap` itself. 
        This class is static class. 
        """
        
        _LIMITED = 0
        _CURSOR = 1
        _CELESTE = 2
        _TEST = 3

        _mode=_LIMITED # keymap mode flag default is _LIMITED


        # Methods to set current mode

        @classmethod
        def setLimited(cls):
            cls._mode = cls._LIMITED

        @classmethod
        def setCursor(cls):
            cls._mode = cls._CURSOR

        @classmethod
        def setCeleste(cls):
            cls._mode = cls._CELESTE

        @classmethod
        def setTest(cls):
            cls._mode = cls._TEST
        

        # Methods to get current mode. `dummy_window` is introduced for `keyfunc` for `keymap.defineWindowKeymap(keyfunc=hogehoge)`.

        @classmethod
        def isLimited(cls,dummy_window=None):
            return cls._mode == cls._LIMITED
        
        @classmethod
        def isCursor(cls,dummy_window=None):
            return cls._mode == cls._CURSOR

        @classmethod
        def isCeleste(cls,dummy_window=None):
            return cls._mode == cls._CELESTE

        @classmethod
        def isTest(cls,dummy_window=None):
            return cls._mode == cls._TEST


    @classmethod
    def configureKeymap(cls,keymap):

        # Editor
        keymap.editor = "C:\Program Files\Microsoft VS Code\Code.exe"
        
        # Font
        keymap.setFont( "MS Gothic", 12 )

        # Theme
        keymap.setTheme("black")

        # Modifier
        keymap.defineModifier(29,"User1")       #assign "muhenkan(無変換)" "User1"
        keymap.defineModifier("Slash","User2")  #assign "Slash(/)" "User2"


        # Functions to change WindowKeymap
        # In `keymap.updateKeymap()`, `WindowKeymap`s such as `windowKeymapLimited` (which will be defined later in this function) are activated or deactivated
        # through the `check_func` which will be substituted in `keymap.defineWindowKeymap(check_func=...)`.
        
        def change_window_keymap_limited():
            KeymapConfig.KeymapMode.setLimited()
            keymap.updateKeymap()

        def change_window_keymap_cursor():
            KeymapConfig.KeymapMode.setCursor()
            keymap.updateKeymap()
        
        def change_window_keymap_celeste():
            KeymapConfig.KeymapMode.setCeleste()
            keymap.updateKeymap()
        
        def change_window_keymap_test():
            KeymapConfig.KeymapMode.setTest()
            keymap.updateKeymap()


        # IME-ON/OFF Functions

        def enable_ime():
            keymap.wnd.setImeStatus(1)

        def disable_ime():
            keymap.wnd.setImeStatus(0)


        # Functions to change WindowKeymap and enable/disable IME coincidently. 

        def change_window_keymap_limited_and_enable_ime():
            change_window_keymap_limited()
            enable_ime()

        def change_window_keymap_limited_and_disable_ime():
            change_window_keymap_limited()
            disable_ime()


        
        if 1:   # define `windowKeymapGlobal` 
            
            # set `windowKeymapGlobal` as always-active WindowKeymap
            windowKeymapGlobal=keymap.defineWindowKeymap()   

            # Mode change keys
            windowKeymapGlobal["U1-c"]=change_window_keymap_cursor    # muhenkan - c
            windowKeymapGlobal["U1-q"]=change_window_keymap_celeste   # muhenkan - q
            windowKeymapGlobal["U1-t"]=change_window_keymap_test      # muhenkan - t
            windowKeymapGlobal["U1-(28)"]=change_window_keymap_limited_and_disable_ime     # muhenkan - henkan
            #windowKeymapGlobal["U1-(240)"]=change_window_limited_and_enable_ime   # muhenkan - hiragana (When IME is OFF) この設定はなくてもなぜか動作する。細かい仕様は調査が必要
            windowKeymapGlobal["U1-(242)"]=change_window_keymap_limited_and_enable_ime     # muhenkan - hiragana (When IME is ON?)
            windowKeymapGlobal["U1-q"]=change_window_keymap_celeste                    # muhenkan - q

            # IME ON / OFF with Shift - katakana / henkan
            windowKeymapGlobal["S-(241)"]=change_window_keymap_limited_and_enable_ime  #Shift - katakana/hiragana/romaji
            windowKeymapGlobal["S-(28)"]=change_window_keymap_limited_and_disable_ime  #Shift - henkan

            # oneshot Slash -> Slash
            for any in ("", "S-", "C-", "C-S-", "A-", "A-S-", "A-C-", "A-C-S-", "W-", "W-S-", "W-C-", "W-C-S-", "W-A-", "W-A-S-", "W-A-C-", "W-A-C-S-"):
                windowKeymapGlobal[any+"O-Slash"]=any+"Slash"
            
        
        if 1:   # define `windowKeymapLimited`
            
            # set `windowKeymapLimited` as WindowKeymap which is active when KeymapMode is "limited".
            windowKeymapLimited = keymap.defineWindowKeymap(check_func=cls.KeymapMode.isLimited)

            # shortcuts for typing with smaller movements
            windowKeymapLimited["A-z"]="A-Tab"
            windowKeymapLimited["A-S-z"]="A-S-Tab"
            windowKeymapLimited["RC-j"]="Enter"
            windowKeymapLimited["RC-h"]="Back"
            windowKeymapLimited["RC-d"]="Delete"

            for any in ("", "S-", "C-", "C-S-", "A-", "A-S-", "A-C-", "A-C-S-", "W-", "W-S-", "W-C-", "W-C-S-", "W-A-", "W-A-S-", "W-A-C-", "W-A-C-S-"):
                # arrow-like behavior with ijkl and uoh;
                windowKeymapLimited[any+"U1-i"]=any+"Up"
                windowKeymapLimited[any+"U1-j"]=any+"Left"
                windowKeymapLimited[any+"U1-k"]=any+"Down"
                windowKeymapLimited[any+"U1-l"]=any+"Right"
                windowKeymapLimited[any+"U1-u"]=any+"PageUp"
                windowKeymapLimited[any+"U1-h"]=any+"Home"
                windowKeymapLimited[any+"U1-o"]=any+"PageDown"
                windowKeymapLimited[any+"U1-Semicolon"]=any+"End"
                windowKeymapLimited[any+"U1-n"]=any+"Enter"
                windowKeymapLimited[any+"U1-m"]=any+"Tab"

                # F-N -> FN
                for i in range(1,12+1):
                    windowKeymapLimited[any+"U1-"+str(i)]=any+"F"+str(i)


        if 1:   # define `windowKeymapCursor`

            # set `windowKeymapCursor` as WindowKeymap which is active when KeymapMode is "cursor".
            windowKeymapCursor = keymap.defineWindowKeymap(check_func=cls.KeymapMode.isCursor)

            # shortcuts for typing with smaller movements
            windowKeymapCursor["A-z"]="A-Tab"
            windowKeymapCursor["A-S-z"]="A-S-Tab"
            windowKeymapCursor["RC-j"]="Enter"
            windowKeymapCursor["RC-h"]="Back"
            windowKeymapCursor["RC-d"]="Delete"            

            # additional shortcuts for typing with smaller movements
            windowKeymapCursor["x"]="Delete"
            windowKeymapCursor["S-x"]="Back"
            windowKeymapCursor["w"]="C-Tab"
            windowKeymapCursor["q"]="C-S-Tab"
            windowKeymapCursor["O-f"]="LButton"
            windowKeymapCursor["O-g"]="RButton"
            
            for any in ("", "S-", "C-", "C-S-", "A-", "A-S-", "A-C-", "A-C-S-", "W-", "W-S-", "W-C-", "W-C-S-", "W-A-", "W-A-S-", "W-A-C-", "W-A-C-S-"):
                # arrow-like behavior with ijkl and uoh;
                windowKeymapCursor[any+"i"]=any+"Up"
                windowKeymapCursor[any+"j"]=any+"Left"
                windowKeymapCursor[any+"k"]=any+"Down"
                windowKeymapCursor[any+"l"]=any+"Right"
                windowKeymapCursor[any+"u"]=any+"PageUp"
                windowKeymapCursor[any+"h"]=any+"Home"
                windowKeymapCursor[any+"o"]=any+"PageDown"
                windowKeymapCursor[any+"Semicolon"]=any+"End"
                
                # enter and tab 
                windowKeymapCursor[any+"n"]=any+"Enter"
                windowKeymapCursor[any+"m"]=any+"Tab"


        if 1:   # define `windowKeymapCeleste`
            
            # set `windowKeymapCeleste` as WindowKeymap which is active when KeymapMode is "celeste".
            windowKeymapCeleste = keymap.defineWindowKeymap(check_func=cls.KeymapMode.isCeleste)
            
            # Celeste mode is the mode to play Celeste, where almost all keymaps are in inactive to avoid mistyping
            pass


        if 1:   # define `windowKeymapTest` 実験中のスクリプト

            # set `windowKeymapTest` as WindowKeymap which is active when KeymapMode is "test".
            windowKeymapTest = keymap.defineWindowKeymap(check_func=cls.KeymapMode.isTest)
            
            
            # マクロテスト
            if 1:         
                
                """
                keymap を通して "abcde" と 0.5 sec おきに入力する関数
                この関数を直接キー入力に割り当てると意図したように動作しない

                現象としては実行中にキー入力が割り込む
                おそらく本関数のように実行に時間のかかる関数をキーに割り当てた場合、
                実行の終了以前にキー入力がなされる
                """
                def abcde_raw():
                    keymap.InputKeyCommand("a")()
                    time.sleep(0.5)
                    keymap.InputKeyCommand("b")()
                    time.sleep(0.5)
                    keymap.InputKeyCommand("c")()
                    time.sleep(0.5)
                    keymap.InputKeyCommand("d")()
                    time.sleep(0.5)
                    keymap.InputKeyCommand("e")()


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
                    keymap.delayedCall(abcde_raw,0)


                
                windowKeymapTest["U1-q"]=abcde_delay  # 意図したとおり動くが time stamp inversion のメッセージが出る
                # window_keymap["U1-p"]=abcde_raw  # 意図したとおり動かない

            # デフォルト定義されているコマンドの置き換え
            if 1:
                # USER0-Up/Down/Left/Right : Move active window by 10 pixel unit
                windowKeymapTest[ "U1-Left"  ] = keymap.MoveWindowCommand( -10, 0 )
                windowKeymapTest[ "U1-Right" ] = keymap.MoveWindowCommand( +10, 0 )
                windowKeymapTest[ "U1-Up"    ] = keymap.MoveWindowCommand( 0, -10 )
                windowKeymapTest[ "U1-Down"  ] = keymap.MoveWindowCommand( 0, +10 )

                # USER0-Shift-Up/Down/Left/Right : Move active window by 1 pixel unit
                windowKeymapTest[ "U1-S-Left"  ] = keymap.MoveWindowCommand( -1, 0 )
                windowKeymapTest[ "U1-S-Right" ] = keymap.MoveWindowCommand( +1, 0 )
                windowKeymapTest[ "U1-S-Up"    ] = keymap.MoveWindowCommand( 0, -1 )
                windowKeymapTest[ "U1-S-Down"  ] = keymap.MoveWindowCommand( 0, +1 )

                # USER0-Ctrl-Up/Down/Left/Right : Move active window to screen edges
                windowKeymapTest[ "U1-C-Left"  ] = keymap.MoveWindowToMonitorEdgeCommand(0)
                windowKeymapTest[ "U1-C-Right" ] = keymap.MoveWindowToMonitorEdgeCommand(2)
                windowKeymapTest[ "U1-C-Up"    ] = keymap.MoveWindowToMonitorEdgeCommand(1)
                windowKeymapTest[ "U1-C-Down"  ] = keymap.MoveWindowToMonitorEdgeCommand(3)

                # Clipboard history related
                windowKeymapTest[ "C-S-Z"   ] = keymap.command_ClipboardList     # Open the clipboard history list
                windowKeymapTest[ "C-S-X"   ] = keymap.command_ClipboardRotate   # Move the most recent history to tail
                windowKeymapTest[ "C-S-A-X" ] = keymap.command_ClipboardRemove   # Remove the most recent history
                keymap.quote_mark = "> "                                    # Mark for quote pasting

                # Keyboard macro
                windowKeymapTest[ "U1-0" ] = keymap.command_RecordToggle
                windowKeymapTest[ "U1-1" ] = keymap.command_RecordStart
                windowKeymapTest[ "U1-2" ] = keymap.command_RecordStop
                windowKeymapTest[ "U1-3" ] = keymap.command_RecordPlay
                windowKeymapTest[ "U1-4" ] = keymap.command_RecordClear




def configure(keymap):
    """Function called to set settings for keymap. 
    """

    # My definition
    if 1:   # limited mode and cursor mode (vim-like), move with IJKL
        #KeymapConfig.setKeymap(keymap)
        KeymapConfig.configureKeymap(keymap)


    # Original definitions (skipped)
    if 0:
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

