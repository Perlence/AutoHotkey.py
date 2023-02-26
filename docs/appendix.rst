Appendix
========

Python Equivalents of AutoHotkey Keywords
-----------------------------------------

This section lists the relevant AHK keywords (Commands, Function, Directives,
and Variables) and their Python counterparts.

.. list-table::
   :header-rows: 1

   + - AHK Keyword
     - Python Implementation
   + - `#If <https://www.autohotkey.com/docs/commands/_If.htm>`_
     - :class:`ahkpy.HotkeyContext`
   + - `#IfWinActive <https://www.autohotkey.com/docs/commands/_IfWinActive.htm>`_
     - ``ahkpy.windows.filter().active_window_context().hotkey()``
   + - `#IfWinExist <https://www.autohotkey.com/docs/commands/WinExist.htm>`_
     - ``ahkpy.Window.filter().window_context().hotkey()``
   + - `#Include <https://www.autohotkey.com/docs/commands/_Include.htm>`_
     - `The import statement <https://docs.python.org/3/reference/simple_stmts.html#the-import-statement>`_
   + - `1, 2, 3, etc <https://www.autohotkey.com/docs/Variables.htm#CommandLine>`_
     - :data:`sys.argv`
   + - `A_AhkPath <https://www.autohotkey.com/docs/Variables.htm#AhkPath>`_
     - :data:`ahk.executable`
   + - `A_AppData <https://www.autohotkey.com/docs/Variables.htm#AppData>`_
     - ``os.getenv("APPDATA")``
   + - `A_AppDataCommon <https://www.autohotkey.com/docs/Variables.htm#AppDataCommon>`_
     - ``os.getenv("ALLUSERSPROFILE")``
   + - `A_ComputerName <https://www.autohotkey.com/docs/Variables.htm#ComputerName>`_
     - ``os.getenv("COMPUTERNAME")``
   + - `A_DD <https://www.autohotkey.com/docs/Variables.htm#DD>`_
     - ``datetime.datetime.now().day``
   + - `A_DDD <https://www.autohotkey.com/docs/Variables.htm#DDD>`_
     - ``datetime.datetime.now().strftime("%a")``
   + - `A_DDDD <https://www.autohotkey.com/docs/Variables.htm#DDDD>`_
     - ``datetime.datetime.now().strftime("%A")``
   + - `A_DefaultMouseSpeed <https://www.autohotkey.com/docs/Variables.htm#DefaultMouseSpeed>`_
     - :attr:`ahkpy.Settings.mouse_speed`
   + - `A_Hour <https://www.autohotkey.com/docs/Variables.htm#Hour>`_
     - ``datetime.datetime.now().hour``
   + - `A_IconFile <https://www.autohotkey.com/docs/Variables.htm#IconFile>`_
     - :attr:`ahkpy.TrayMenu.tray_icon_file`
   + - `A_IconHidden <https://www.autohotkey.com/docs/Variables.htm#IconHidden>`_
     - :attr:`ahkpy.TrayMenu.is_tray_icon_visible`
   + - `A_IconNumber <https://www.autohotkey.com/docs/Variables.htm#IconNumber>`_
     - :attr:`ahkpy.TrayMenu.tray_icon_number`
   + - `A_Is64bitOS <https://www.autohotkey.com/docs/Variables.htm#Is64bitOS>`_
     - :func:`platform.architecture`
   + - `A_MDay <https://www.autohotkey.com/docs/Variables.htm#MDay>`_
     - ``datetime.datetime.now().day``
   + - `A_Min <https://www.autohotkey.com/docs/Variables.htm#Min>`_
     - ``datetime.datetime.now().minute``
   + - `A_MM <https://www.autohotkey.com/docs/Variables.htm#MM>`_
     - ``datetime.datetime.now().month``
   + - `A_MMM <https://www.autohotkey.com/docs/Variables.htm#MMM>`_
     - ``datetime.datetime.now().strftime("%b")``
   + - `A_MMMM <https://www.autohotkey.com/docs/Variables.htm#MMMM>`_
     - ``datetime.datetime.now().strftime("%B")``
   + - `A_Mon <https://www.autohotkey.com/docs/Variables.htm#Mon>`_
     - ``datetime.datetime.now().month``
   + - `A_MouseDelay <https://www.autohotkey.com/docs/Variables.htm#MouseDelay>`_
     - :attr:`ahkpy.Settings.mouse_delay`
   + - `A_MouseDelayPlay <https://www.autohotkey.com/docs/Variables.htm#MouseDelay>`_
     - :attr:`ahkpy.Settings.mouse_delay_play`
   + - `A_MSec <https://www.autohotkey.com/docs/Variables.htm#MSec>`_
     - ``datetime.datetime.now().microsecond / 1000``
   + - `A_Now <https://www.autohotkey.com/docs/Variables.htm#Now>`_
     - :meth:`datetime.datetime.now`
   + - `A_NowUTC <https://www.autohotkey.com/docs/Variables.htm#NowUTC>`_
     - :meth:`datetime.datetime.utcnow`
   + - `A_OSVersion <https://www.autohotkey.com/docs/Variables.htm#OSVersion>`_
     - :func:`platform.win32_ver`
   + - `A_ProgramFiles <https://www.autohotkey.com/docs/Variables.htm#ProgramFiles>`_
     - ``os.getenv("PROGRAMFILES")``
   + - `A_PtrSize <https://www.autohotkey.com/docs/Variables.htm#PtrSize>`_
     - ``struct.calcsize("P") * 8``
   + - `A_ScriptDir <https://www.autohotkey.com/docs/Variables.htm#ScriptDir>`_
     - ``os.path.dirname(__file__)`` or ``pathlib.Path(__file__).parent``
   + - `A_ScriptFullPath <https://www.autohotkey.com/docs/Variables.htm#ScriptFullPath>`_
     - :data:`ahkpy.script_full_path`
   + - `A_ScriptHwnd <https://www.autohotkey.com/docs/Variables.htm#ScriptHwnd>`_
     - ``ahkpy.all_windows.first(pid=os.getpid)``
   + - `A_ScriptName <https://www.autohotkey.com/docs/Variables.htm#ScriptName>`_
     - ``__file__``
   + - `A_Sec <https://www.autohotkey.com/docs/Variables.htm#Sec>`_
     - ``datetime.datetime.now().second``
   + - `A_Space <https://www.autohotkey.com/docs/Variables.htm#Space>`_
     - ``" "``
   + - `A_Tab <https://www.autohotkey.com/docs/Variables.htm#Tab>`_
     - ``"\t"``
   + - `A_Temp <https://www.autohotkey.com/docs/Variables.htm#Temp>`_
     - ``os.getenv("TEMP")``
   + - `A_TickCount <https://www.autohotkey.com/docs/Variables.htm#TickCount>`_
     - :func:`time.perf_counter`
   + - `A_TitleMatchMode <https://www.autohotkey.com/docs/Variables.htm#TitleMatchMode>`_
     - :attr:`ahkpy.Windows.title_mode`
   + - `A_UserName <https://www.autohotkey.com/docs/Variables.htm#UserName>`_
     - ``os.getenv("USERNAME")``
   + - `A_WDay <https://www.autohotkey.com/docs/Variables.htm#WDay>`_
     - ``(datetime.datetime.now().weekday() + 2) % 7``
   + - `A_WinDir <https://www.autohotkey.com/docs/Variables.htm#WinDir>`_
     - ``os.getenv("WINDIR")``
   + - `A_WorkingDir <https://www.autohotkey.com/docs/Variables.htm#WorkingDir>`_
     - :func:`os.getcwd`
   + - `A_YDay <https://www.autohotkey.com/docs/Variables.htm#YDay>`_
     - ``datetime.datetime.now().strftime("%j").lstrip("0")``
   + - `A_Year <https://www.autohotkey.com/docs/Variables.htm#Year>`_
     - ``datetime.datetime.now().year``
   + - `A_YWeek <https://www.autohotkey.com/docs/Variables.htm#YWeek>`_
     - ``datetime.datetime.now().strftime("%Y%U")``
   + - `A_YYYY <https://www.autohotkey.com/docs/Variables.htm#YYYY>`_
     - ``datetime.datetime.now().year``
   + - `Abs() <https://www.autohotkey.com/docs/commands/Abs.htm>`_
     - :func:`abs`
   + - `ACos() <https://www.autohotkey.com/docs/commands/ACos.htm>`_
     - :func:`math.acos`
   + - `Asc() <https://www.autohotkey.com/docs/commands/Asc.htm>`_
     - :func:`ord`
   + - `ASin() <https://www.autohotkey.com/docs/commands/ASin.htm>`_
     - :func:`math.asin`
   + - `ATan() <https://www.autohotkey.com/docs/commands/ATan.htm>`_
     - :func:`math.atan`
   + - `BlockInput <https://www.autohotkey.com/docs/commands/BlockInput.htm>`_
     - :func:`ahkpy.block_input`, :func:`ahkpy.block_input_while_sending`, :func:`ahkpy.block_mouse_move` context
       managers
   + - `Ceil() <https://www.autohotkey.com/docs/commands/Ceil.htm>`_
     - :func:`math.ceil`
   + - `Chr() <https://www.autohotkey.com/docs/commands/Chr.htm>`_
     - :func:`chr`
   + - `Click <https://www.autohotkey.com/docs/commands/Click.htm>`_
     - :func:`ahkpy.click`, also :func:`~ahkpy.right_click`, :func:`~ahkpy.double_click`, :func:`~ahkpy.mouse_press`,
       :func:`~ahkpy.mouse_release`, :func:`~ahkpy.mouse_scroll`, :func:`~ahkpy.mouse_move`
   + - `Clipboard <https://www.autohotkey.com/docs/commands/Clipboard.htm>`_
     - :func:`ahkpy.get_clipboard` and :func:`ahkpy.set_clipboard`
   + - `ClipWait <https://www.autohotkey.com/docs/commands/ClipWait.htm>`_
     - :func:`ahkpy.wait_clipboard`
   + - `ComSpec <https://www.autohotkey.com/docs/commands/ComSpec.htm>`_
     - ``os.getenv("COMSPEC")``
   + - `Control, Check <https://www.autohotkey.com/docs/commands/Control.htm#Check>`_
     - :meth:`ahkpy.Control.check`, also try setting :attr:`ahkpy.Control.is_checked` property
   + - `Control, Choose <https://www.autohotkey.com/docs/commands/Control.htm#Choose>`_
     - :meth:`ahkpy.Control.choose_item_index`
   + - `Control, ChooseString <https://www.autohotkey.com/docs/commands/Control.htm#ChooseString>`_
     - :meth:`ahkpy.Control.choose_item`
   + - `Control, Disable <https://www.autohotkey.com/docs/commands/Control.htm#Disable>`_
     - :meth:`ahkpy.Control.disable() <ahkpy.window.BaseWindow.disable>`, also try setting
       :attr:`ahkpy.Control.is_enabled<ahkpy.window.BaseWindow.is_enabled>` property
   + - `Control, EditPaste <https://www.autohotkey.com/docs/commands/Control.htm#EditPaste>`_
     - :meth:`ahkpy.Control.paste`
   + - `Control, Enable <https://www.autohotkey.com/docs/commands/Control.htm#Enable>`_
     - :meth:`ahkpy.Control.enable() <ahkpy.window.BaseWindow.enable>`, also try setting
       :attr:`ahkpy.Control.is_enabled <ahkpy.window.BaseWindow.is_enabled>` property
   + - `Control, ExStyle <https://www.autohotkey.com/docs/commands/Control.htm#ExStyle>`_
     - :attr:`ahkpy.Control.ex_style <ahkpy.window.BaseWindow.ex_style>`
   + - `Control, Hide <https://www.autohotkey.com/docs/commands/Control.htm#Hide>`_
     - :meth:`ahkpy.Control.hide() <ahkpy.window.BaseWindow.hide>`, also try setting
       :attr:`ahkpy.Control.is_visible <ahkpy.window.BaseWindow.is_visible>` property
   + - `Control, Show <https://www.autohotkey.com/docs/commands/Control.htm#Show>`_
     - :meth:`ahkpy.Control.show() <ahkpy.window.BaseWindow.show>`, also try setting
       :attr:`ahkpy.Control.is_visible <ahkpy.window.BaseWindow.is_visible>` property
   + - `Control, Style <https://www.autohotkey.com/docs/commands/Control.htm#Style>`_
     - :attr:`ahkpy.Control.style <ahkpy.window.BaseWindow.style>`
   + - `Control, Uncheck <https://www.autohotkey.com/docs/commands/Control.htm#Uncheck>`_
     - :meth:`ahkpy.Control.uncheck`, also try setting :attr:`ahkpy.Control.is_checked` property
   + - `ControlFocus <https://www.autohotkey.com/docs/commands/ControlFocus.htm>`_
     - :meth:`ahkpy.Control.focus`
   + - `ControlGet, Checked <https://www.autohotkey.com/docs/commands/ControlGet.htm#Checked>`_
     - :attr:`ahkpy.Control.is_checked`
   + - `ControlGet, Choice <https://www.autohotkey.com/docs/commands/ControlGet.htm#Choice>`_
     - :attr:`ahkpy.Control.list_choice`, also :attr:`ahkpy.Control.list_choice_index`
   + - `ControlGet, CurrentCol <https://www.autohotkey.com/docs/commands/ControlGet.htm#CurrentCol>`_
     - :attr:`ahkpy.Control.current_column`
   + - `ControlGet, CurrentLine <https://www.autohotkey.com/docs/commands/ControlGet.htm#CurrentLine>`_
     - :attr:`ahkpy.Control.current_line_number`
   + - `ControlGet, Enabled <https://www.autohotkey.com/docs/commands/ControlGet.htm#Enabled>`_
     - :attr:`ahkpy.Control.is_enabled <ahkpy.window.BaseWindow.is_enabled>`
   + - `ControlGet, ExStyle <https://www.autohotkey.com/docs/commands/ControlGet.htm#ExStyle>`_
     - :attr:`ahkpy.Control.ex_style <ahkpy.window.BaseWindow.ex_style>`
   + - `ControlGet, FindString <https://www.autohotkey.com/docs/commands/ControlGet.htm#FindString>`_
     - :meth:`ahkpy.Control.list_item_index`
   + - `ControlGet, Hwnd <https://www.autohotkey.com/docs/commands/ControlGet.htm#Hwnd>`_
     - :attr:`ahkpy.Control.id`
   + - `ControlGet, Line <https://www.autohotkey.com/docs/commands/ControlGet.htm#Line>`_
     - :meth:`ahkpy.Control.get_line`
   + - `ControlGet, LineCount <https://www.autohotkey.com/docs/commands/ControlGet.htm#LineCount>`_
     - :attr:`ahkpy.Control.line_count`
   + - `ControlGet, List <https://www.autohotkey.com/docs/commands/ControlGet.htm#List>`_
     - :attr:`ahkpy.Control.list_items`, also see :attr:`ahkpy.Control.selected_list_items`,
       :attr:`ahkpy.Control.focused_list_item`, :meth:`ahkpy.Control.get_list_items`,
       :attr:`ahkpy.Control.list_item_count`, :attr:`ahkpy.Control.selected_list_item_count`,
       :attr:`ahkpy.Control.focused_list_item_index`, :attr:`ahkpy.Control.list_view_column_count`
   + - `ControlGet, Selected <https://www.autohotkey.com/docs/commands/ControlGet.htm#Selected>`_
     - :meth:`ahkpy.Control.selected_text`
   + - `ControlGet, Style <https://www.autohotkey.com/docs/commands/ControlGet.htm#Style>`_
     - :attr:`ahkpy.Control.style <ahkpy.window.BaseWindow.style>`
   + - `ControlGet, Visible <https://www.autohotkey.com/docs/commands/ControlGet.htm#Visible>`_
     - :attr:`ahkpy.Control.is_visible <ahkpy.window.BaseWindow.is_visible>`
   + - `ControlGetFocus <https://www.autohotkey.com/docs/commands/ControlGetFocus.htm>`_
     - :meth:`ahkpy.Window.get_focused_control`
   + - `ControlGetPos <https://www.autohotkey.com/docs/commands/ControlGetPos.htm>`_
     - :attr:`ahkpy.Control.rect <ahkpy.window.BaseWindow.rect>`, also
       :attr:`position <ahkpy.window.BaseWindow.position>`, :attr:`size <ahkpy.window.BaseWindow.size>`,
       :attr:`x <ahkpy.window.BaseWindow.x>`, :attr:`y <ahkpy.window.BaseWindow.y>`,
       :attr:`width <ahkpy.window.BaseWindow.width>`, :attr:`height <ahkpy.window.BaseWindow.height>` properties
   + - `ControlGetText <https://www.autohotkey.com/docs/commands/ControlGetText.htm>`_
     - :attr:`ahkpy.Control.text`
   + - `ControlMove <https://www.autohotkey.com/docs/commands/ControlMove.htm>`_
     - ``Window.get_control(class_name).rect = ...``, also try setting :class:`ahkpy.Control`'s
       :attr:`x <ahkpy.window.BaseWindow.x>`, :attr:`y <ahkpy.window.BaseWindow.y>`,
       :attr:`width <ahkpy.window.BaseWindow.width>`, :attr:`height <ahkpy.window.BaseWindow.height>` properties
   + - `ControlSend <https://www.autohotkey.com/docs/commands/ControlSend.htm>`_
     - :func:`ahkpy.window.BaseWindow.send`
   + - `ControlSendRaw <https://www.autohotkey.com/docs/commands/ControlSendRaw.htm>`_
     - ``ahkpy.Window.get_control(class_name).send("{Raw}...")``
   + - `ControlSetText <https://www.autohotkey.com/docs/commands/ControlSetText.htm>`_
     - :attr:`ahkpy.Control.text`
   + - `Cos() <https://www.autohotkey.com/docs/commands/Cos.htm>`_
     - :func:`math.cos`
   + - `DetectHiddenText <https://www.autohotkey.com/docs/commands/DetectHiddenText.htm>`_
     - :meth:`ahkpy.Windows.exclude_hidden_text`
   + - `DetectHiddenWindows <https://www.autohotkey.com/docs/commands/DetectHiddenWindows.htm>`_
     - :data:`ahkpy.all_windows`
   + - `DllCall() <https://www.autohotkey.com/docs/commands/DllCall.htm>`_
     - :mod:`ctypes`
   + - `EnvGet <https://www.autohotkey.com/docs/commands/EnvGet.htm>`_
     - :data:`os.environ` or :func:`os.getenv`
   + - `EnvSet <https://www.autohotkey.com/docs/commands/EnvSet.htm>`_
     - :data:`os.environ` or :func:`os.putenv`
   + - `ExitApp <https://www.autohotkey.com/docs/commands/ExitApp.htm>`_
     - :func:`sys.exit`
   + - `Exp() <https://www.autohotkey.com/docs/commands/Exp.htm>`_
     - :func:`math.exp`
   + - `FileAppend <https://www.autohotkey.com/docs/commands/FileAppend.htm>`_
     - ``open().write()``
   + - `FileCopy <https://www.autohotkey.com/docs/commands/FileCopy.htm>`_
     - :func:`glob.glob` with :func:`shutil.copy` or :func:`shutil.copytree`
   + - `FileCopyDir <https://www.autohotkey.com/docs/commands/FileCopyDir.htm>`_
     - :func:`glob.glob` with :func:`shutil.copy` or :func:`shutil.copytree`
   + - `FileCreateDir <https://www.autohotkey.com/docs/commands/FileCreateDir.htm>`_
     - :func:`os.mkdir` or :func:`os.makedirs`
   + - `FileDelete <https://www.autohotkey.com/docs/commands/FileDelete.htm>`_
     - :func:`os.remove`
   + - `FileEncoding <https://www.autohotkey.com/docs/commands/FileEncoding.htm>`_
     - ``open(encoding="...")``
   + - `FileGetSize <https://www.autohotkey.com/docs/commands/FileGetSize.htm>`_
     - :func:`os.path.getsize`
   + - `FileGetTime <https://www.autohotkey.com/docs/commands/FileGetTime.htm>`_
     - :func:`os.path.getatime`, :func:`os.path.getmtime`, or :func:`os.path.getctime`
   + - `FileMove <https://www.autohotkey.com/docs/commands/FileMove.htm>`_
     - :func:`shutil.move`
   + - `FileMoveDir <https://www.autohotkey.com/docs/commands/FileMoveDir.htm>`_
     - :func:`shutil.move`
   + - `FileOpen() <https://www.autohotkey.com/docs/commands/FileOpen.htm>`_
     - :func:`open`
   + - `FileRead <https://www.autohotkey.com/docs/commands/FileRead.htm>`_
     - ``open().read()``
   + - `FileReadLine <https://www.autohotkey.com/docs/commands/FileReadLine.htm>`_
     - ``open().readline()``
   + - `FileRemoveDir <https://www.autohotkey.com/docs/commands/FileRemoveDir.htm>`_
     - :func:`shutil.rmtree`
   + - `FileSetTime <https://www.autohotkey.com/docs/commands/FileSetTime.htm>`_
     - Can set *atime* and *mtime* with :func:`os.utime`, cannot set *ctime*
   + - `Floor() <https://www.autohotkey.com/docs/commands/Floor.htm>`_
     - :func:`math.floor`
   + - `Format() <https://www.autohotkey.com/docs/commands/Format.htm>`_
     - `f-strings <https://docs.python.org/3/reference/lexical_analysis.html#f-strings>`_ or :meth:`str.format`
   + - `FormatTime <https://www.autohotkey.com/docs/commands/FormatTime.htm>`_
     - :func:`format` or :meth:`datetime.datetime.strftime`
   + - `GetKeyName() <https://www.autohotkey.com/docs/commands/GetKeyName.htm>`_
     - :func:`ahkpy.get_key_name`
   + - `GetKeySC() <https://www.autohotkey.com/docs/commands/GetKeySC.htm>`_
     - :func:`ahkpy.get_key_sc`
   + - `GetKeyState <https://www.autohotkey.com/docs/commands/GetKeyState.htm>`_
     - :func:`ahkpy.is_key_pressed` or :func:`ahkpy.is_key_pressed_logical`
   + - `GetKeyState() <https://www.autohotkey.com/docs/commands/GetKeyState.htm>`_
     - :func:`ahkpy.is_key_pressed` or :func:`ahkpy.is_key_pressed_logical`, :func:`ahkpy.get_caps_lock_state`,
       :func:`ahkpy.get_num_lock_state`, :func:`ahkpy.get_scroll_lock_state`, :func:`ahkpy.get_insert_state`
   + - `GetKeyVK() <https://www.autohotkey.com/docs/commands/GetKeyVK.htm>`_
     - :func:`ahkpy.get_key_vk`
   + - `GroupClose <https://www.autohotkey.com/docs/commands/GroupClose.htm>`_
     - :meth:`ahkpy.Windows.close_all`
   + - `Hotkey <https://www.autohotkey.com/docs/commands/Hotkey.htm>`_
     - :func:`ahkpy.hotkey`
   + - `Hotstring() <https://www.autohotkey.com/docs/commands/Hotstring.htm>`_
     - :func:`ahkpy.hotstring`
   + - `IfMsgBox <https://www.autohotkey.com/docs/commands/IfMsgBox.htm>`_
     - ``if ahkpy.message_box(...) == "...": ...``
   + - `IniDelete <https://www.autohotkey.com/docs/commands/IniDelete.htm>`_
     - :mod:`configparser` module
   + - `IniRead <https://www.autohotkey.com/docs/commands/IniRead.htm>`_
     - :mod:`configparser` module
   + - `IniWrite <https://www.autohotkey.com/docs/commands/IniWrite.htm>`_
     - :mod:`configparser` module
   + - `InStr() <https://www.autohotkey.com/docs/commands/InStr.htm>`_
     - ``"..." in str`` or :meth:`str.find`
   + - `KeyWait <https://www.autohotkey.com/docs/commands/KeyWait.htm>`_
     - :func:`ahkpy.wait_key_pressed` or :func:`ahkpy.wait_key_released`
   + - `Ln() <https://www.autohotkey.com/docs/commands/Ln.htm>`_
     - :func:`math.log`
   + - `Log() <https://www.autohotkey.com/docs/commands/Log.htm>`_
     - :func:`math.log10`
   + - `Loop <https://www.autohotkey.com/docs/commands/Loop.htm>`_
     - `The for statement <https://docs.python.org/3/reference/compound_stmts.html#the-for-statement>`_
   + - `Loop, Files <https://www.autohotkey.com/docs/commands/LoopFile.htm>`_
     - :func:`os.scandir` or :func:`os.listdir`
   + - `Loop, Read <https://www.autohotkey.com/docs/commands/LoopReadFile.htm>`_
     - ``open().read()``
   + - `Loop, Reg <https://www.autohotkey.com/docs/commands/LoopReg.htm>`_
     - :mod:`winreg` module
   + - `LTrim() <https://www.autohotkey.com/docs/commands/LTrim.htm>`_
     - :meth:`str.lstrip`
   + - `Mod() <https://www.autohotkey.com/docs/commands/Mod.htm>`_
     - The ``%`` (modulo) operator
   + - `Menu, $, Add <https://www.autohotkey.com/docs/commands/Menu.html#Add>`_
     - :meth:`ahkpy.Menu.add`
   + - `Menu, $, Insert <https://www.autohotkey.com/docs/commands/Menu.html#Insert>`_
     - :meth:`ahkpy.Menu.insert`
   + - `Menu, $, Delete <https://www.autohotkey.com/docs/commands/Menu.html#Delete>`_
     - :meth:`ahkpy.Menu.delete_item`, :meth:`ahkpy.Menu.delete_menu`
   + - `Menu, $, DeleteAll <https://www.autohotkey.com/docs/commands/Menu.html#DeleteAll>`_
     - :meth:`ahkpy.Menu.delete_all_items`
   + - `Menu, $, Rename <https://www.autohotkey.com/docs/commands/Menu.html#Rename>`_
     - :meth:`ahkpy.Menu.rename`
   + - `Menu, $, Check <https://www.autohotkey.com/docs/commands/Menu.html#Check>`_
     - :meth:`ahkpy.Menu.check`
   + - `Menu, $, Uncheck <https://www.autohotkey.com/docs/commands/Menu.html#Uncheck>`_
     - :meth:`ahkpy.Menu.uncheck`
   + - `Menu, $, ToggleCheck <https://www.autohotkey.com/docs/commands/Menu.html#ToggleCheck>`_
     - :meth:`ahkpy.Menu.toggle_checked`
   + - `Menu, $, Enable <https://www.autohotkey.com/docs/commands/Menu.html#Enable>`_
     - :meth:`ahkpy.Menu.enable`
   + - `Menu, $, Disable <https://www.autohotkey.com/docs/commands/Menu.html#Disable>`_
     - :meth:`ahkpy.Menu.disable`
   + - `Menu, $, ToggleEnable <https://www.autohotkey.com/docs/commands/Menu.html#ToggleEnable>`_
     - :meth:`ahkpy.Menu.toggle_enabled`
   + - `Menu, $, Default <https://www.autohotkey.com/docs/commands/Menu.html#Default>`_
     - :meth:`ahkpy.Menu.set_default`
   + - `Menu, $, NoDefault <https://www.autohotkey.com/docs/commands/Menu.html#NoDefault>`_
     - :meth:`ahkpy.Menu.remove_default`
   + - `Menu, $, Icon <https://www.autohotkey.com/docs/commands/Menu.html#Icon>`_
     - :meth:`ahkpy.Menu.set_icon`
   + - `Menu, $, NoIcon <https://www.autohotkey.com/docs/commands/Menu.html#NoIcon>`_
     - :meth:`ahkpy.Menu.remove_icon`
   + - `Menu, $, Show <https://www.autohotkey.com/docs/commands/Menu.html#Show>`_
     - :meth:`ahkpy.Menu.show`
   + - `Menu, $, Color <https://www.autohotkey.com/docs/commands/Menu.html#Color>`_
     - :meth:`ahkpy.Menu.set_color`
   + - `Menu, Tray, Icon <https://www.autohotkey.com/docs/commands/Menu.html#TrayIcon>`_
     - :meth:`ahkpy.TrayMenu.set_tray_icon`, :meth:`ahkpy.TrayMenu.toggle_tray_icon`, :meth:`ahkpy.TrayMenu.show_tray_icon`
   + - `Menu, Tray, NoIcon <https://www.autohotkey.com/docs/commands/Menu.html#NoIcon>`_
     - :meth:`ahkpy.TrayMenu.hide_tray_icon`
   + - `Menu, Tray, Tip <https://www.autohotkey.com/docs/commands/Menu.html#Tip>`_
     - :attr:`ahkpy.TrayMenu.tip`
   + - `Menu, Tray, Click <https://www.autohotkey.com/docs/commands/Menu.html#Click>`_
     - :meth:`ahkpy.TrayMenu.set_clicks`
   + - `MouseClick <https://www.autohotkey.com/docs/commands/MouseClick.htm>`_
     - :func:`ahkpy.click`, also :func:`~ahkpy.right_click`, :func:`~ahkpy.double_click`, :func:`~ahkpy.mouse_press`,
       :func:`~ahkpy.mouse_release`, :func:`~ahkpy.mouse_scroll`, :func:`~ahkpy.mouse_move`
   + - `MouseClickDrag <https://www.autohotkey.com/docs/commands/MouseClickDrag.htm>`_
     - Use :func:`ahkpy.mouse_press`, :func:`ahkpy.mouse_move`, and :func:`ahkpy.mouse_release`
   + - `MouseGetPos <https://www.autohotkey.com/docs/commands/MouseGetPos.htm>`_
     - :func:`ahkpy.get_mouse_pos`, :func:`~ahkpy.get_window_under_mouse`, :func:`~ahkpy.get_control_under_mouse`
   + - `MouseMove <https://www.autohotkey.com/docs/commands/MouseMove.htm>`_
     - :func:`ahkpy.mouse_move`
   + - `NumGet() <https://www.autohotkey.com/docs/commands/NumGet.htm>`_
     - :func:`struct.unpack`
   + - `NumPut() <https://www.autohotkey.com/docs/commands/NumPut.htm>`_
     - :func:`struct.pack`
   + - `OnClipboardChange <https://www.autohotkey.com/docs/commands/OnClipboardChange.htm>`_
     - :func:`ahkpy.on_clipboard_change`
   + - `OnMessage() <https://www.autohotkey.com/docs/commands/OnMessage.htm>`_
     - :func:`ahkpy.on_message`
   + - `OutputDebug <https://www.autohotkey.com/docs/commands/OutputDebug.htm>`_
     - :func:`ahkpy.output_debug`
   + - `PostMessage <https://www.autohotkey.com/docs/commands/PostMessage.htm>`_
     - :meth:`ahkpy.window.BaseWindow.post_message`
   + - `Process <https://www.autohotkey.com/docs/commands/Process.htm>`_
     - `psutil <https://github.com/giampaolo/psutil>`_ package
   + - `ProgramFiles <https://www.autohotkey.com/docs/commands/ProgramFiles.htm>`_
     - ``os.getenv("PROGRAMFILES")``
   + - `Random <https://www.autohotkey.com/docs/commands/Random.htm>`_
     - :mod:`random` module
   + - `RegDelete <https://www.autohotkey.com/docs/commands/RegDelete.htm>`_
     - :mod:`winreg` module
   + - `RegExMatch() <https://www.autohotkey.com/docs/commands/RegExMatch.htm>`_
     - :func:`re.search`
   + - `RegExReplace() <https://www.autohotkey.com/docs/commands/RegExReplace.htm>`_
     - :func:`re.sub`
   + - `RegisterCallback() <https://www.autohotkey.com/docs/commands/RegisterCallback.htm>`_
     - :func:`ctypes.CFUNCTYPE`
   + - `RegRead <https://www.autohotkey.com/docs/commands/RegRead.htm>`_
     - :mod:`winreg` module
   + - `RegWrite <https://www.autohotkey.com/docs/commands/RegWrite.htm>`_
     - :mod:`winreg` module
   + - `Reload <https://www.autohotkey.com/docs/commands/Reload.htm>`_
     - :func:`ahkpy.restart`
   + - `Round() <https://www.autohotkey.com/docs/commands/Round.htm>`_
     - :func:`round`
   + - `RTrim() <https://www.autohotkey.com/docs/commands/RTrim.htm>`_
     - :meth:`str.rstrip`
   + - `Run <https://www.autohotkey.com/docs/commands/Run.htm>`_
     - :class:`subprocess.Popen`
   + - `RunWait <https://www.autohotkey.com/docs/commands/RunWait.htm>`_
     - :func:`subprocess.run`
   + - `Send <https://www.autohotkey.com/docs/commands/Send.htm>`_
     - :func:`ahkpy.send`
   + - `SendEvent <https://www.autohotkey.com/docs/commands/SendEvent.htm>`_
     - :func:`ahkpy.send_event`
   + - `SendInput <https://www.autohotkey.com/docs/commands/SendInput.htm>`_
     - :func:`ahkpy.send_input`
   + - `SendLevel <https://www.autohotkey.com/docs/commands/SendLevel.htm>`_
     - Set the *level* argument in :func:`ahkpy.send` or via :attr:`ahkpy.Settings.send_level`
   + - `SendMessage <https://www.autohotkey.com/docs/commands/SendMessage.htm>`_
     - :meth:`ahkpy.window.BaseWindow.send_message`
   + - `SendMode <https://www.autohotkey.com/docs/commands/SendMode.htm>`_
     - Set the *mode* argument in :func:`ahkpy.send` or via :attr:`ahkpy.Settings.send_mode`
   + - `SendPlay <https://www.autohotkey.com/docs/commands/SendPlay.htm>`_
     - :func:`ahkpy.send_play`
   + - `SetCapslockState <https://www.autohotkey.com/docs/commands/SetCapslockState.htm>`_
     - :func:`ahkpy.set_caps_lock_state`
   + - `SetControlDelay <https://www.autohotkey.com/docs/commands/SetControlDelay.htm>`_
     - :attr:`ahkpy.Settings.control_delay`
   + - `SetDefaultMouseSpeed <https://www.autohotkey.com/docs/commands/SetDefaultMouseSpeed.htm>`_
     - Set the *speed* argument in :func:`ahkpy.mouse_move` or via :attr:`ahkpy.Settings.mouse_speed`
   + - `SetKeyDelay <https://www.autohotkey.com/docs/commands/SetKeyDelay.htm>`_
     - :attr:`ahkpy.Settings.key_delay`
   + - `SetMouseDelay <https://www.autohotkey.com/docs/commands/SetMouseDelay.htm>`_
     - Set the *delay* argument in :func:`ahkpy.click` or via :attr:`ahkpy.Settings.mouse_delay` and
       :attr:`ahkpy.Settings.mouse_delay_play`
   + - `SetNumLockState <https://www.autohotkey.com/docs/commands/SetNumLockState.htm>`_
     - :func:`ahkpy.set_num_lock_state`
   + - `SetScrollLockState <https://www.autohotkey.com/docs/commands/SetScrollLockState.htm>`_
     - :func:`ahkpy.set_scroll_lock_state`
   + - `SetTimer <https://www.autohotkey.com/docs/commands/SetTimer.htm>`_
     - :func:`ahkpy.set_timer`
   + - `SetTitleMatchMode <https://www.autohotkey.com/docs/commands/SetTitleMatchMode.htm>`_
     - Set the *match* argument in :meth:`ahkpy.Windows.filter`
   + - `SetWinDelay <https://www.autohotkey.com/docs/commands/SetWinDelay.htm>`_
     - :attr:`ahkpy.Settings.win_delay`
   + - `SetWorkingDir <https://www.autohotkey.com/docs/commands/SetWorkingDir.htm>`_
     - :func:`os.chdir`
   + - `Sin() <https://www.autohotkey.com/docs/commands/Sin.htm>`_
     - :func:`math.sin`
   + - `Sleep <https://www.autohotkey.com/docs/commands/Sleep.htm>`_
     - :func:`ahkpy.sleep`
   + - `Sort <https://www.autohotkey.com/docs/commands/Sort.htm>`_
     - :func:`sorted` or :meth:`list.sort`
   + - `SplitPath <https://www.autohotkey.com/docs/commands/SplitPath.htm>`_
     - :func:`os.path.basename`, :func:`os.path.dirname`, :func:`os.path.splitext`, :func:`os.path.splitdrive`
   + - `Sqrt() <https://www.autohotkey.com/docs/commands/Sqrt.htm>`_
     - :func:`math.sqrt`
   + - `StatusBarGetText <https://www.autohotkey.com/docs/commands/StatusBarGetText.htm>`_
     - :meth:`ahkpy.Window.get_status_bar_text`
   + - `StatusBarWait <https://www.autohotkey.com/docs/commands/StatusBarWait.htm>`_
     - :meth:`ahkpy.Window.wait_status_bar`
   + - `StrGet() <https://www.autohotkey.com/docs/commands/StrGet.htm>`_
     - :meth:`bytes.decode` or :mod:`struct` module
   + - `StringGetPos <https://www.autohotkey.com/docs/commands/StringGetPos.htm>`_
     - ``"..." in str`` or :meth:`str.find`
   + - `StringLeft <https://www.autohotkey.com/docs/commands/StringLeft.htm>`_
     - ``str[:count]``
   + - `StringLen <https://www.autohotkey.com/docs/commands/StringLen.htm>`_
     - ``len(str)``
   + - `StringLower <https://www.autohotkey.com/docs/commands/StringLower.htm>`_
     - :meth:`str.lower`
   + - `StringMid <https://www.autohotkey.com/docs/commands/StringMid.htm>`_
     - ``str[left:left+count]``
   + - `StringReplace <https://www.autohotkey.com/docs/commands/StringReplace.htm>`_
     - :meth:`str.replace`
   + - `StringRight <https://www.autohotkey.com/docs/commands/StringRight.htm>`_
     - ``str[-count:]``
   + - `StringSplit() <https://www.autohotkey.com/docs/commands/StringSplit.htm>`_
     - :meth:`str.split`
   + - `StringTrimLeft <https://www.autohotkey.com/docs/commands/StringTrimLeft.htm>`_
     - ``str[count:]``
   + - `StringTrimRight <https://www.autohotkey.com/docs/commands/StringTrimRight.htm>`_
     - ``str[:-count]``
   + - `StringUpper <https://www.autohotkey.com/docs/commands/StringUpper.htm>`_
     - :meth:`str.upper`
   + - `StrLen() <https://www.autohotkey.com/docs/commands/StrLen.htm>`_
     - :func:`len`
   + - `StrPut() <https://www.autohotkey.com/docs/commands/StrPut.htm>`_
     - :meth:`str.encode` or :mod:`struct` module
   + - `StrSplit() <https://www.autohotkey.com/docs/commands/StrSplit.htm>`_
     - :meth:`str.split`
   + - `SubStr() <https://www.autohotkey.com/docs/commands/SubStr.htm>`_
     - ``str[start:start+len]``
   + - `Suspend <https://www.autohotkey.com/docs/commands/Suspend.htm>`_
     - :func:`ahkpy.suspend`, :func:`ahkpy.resume`, :func:`ahkpy.toggle_suspend`
   + - `Tan() <https://www.autohotkey.com/docs/commands/Tan.htm>`_
     - :func:`math.tan`
   + - `ToolTip <https://www.autohotkey.com/docs/commands/ToolTip.htm>`_
     - :class:`ahkpy.ToolTip`
   + - `Transform <https://www.autohotkey.com/docs/commands/Transform.htm>`_
     - :func:`html.escape`
   + - `Trim() <https://www.autohotkey.com/docs/commands/Trim.htm>`_
     - :meth:`str.strip`
   + - `UrlDownloadToFile <https://www.autohotkey.com/docs/commands/UrlDownloadToFile.htm>`_
     - :func:`urllib.request.urlopen` or `requests <https://github.com/psf/requests>`_ package
   + - `WinActivate <https://www.autohotkey.com/docs/commands/WinActivate.htm>`_
     - :meth:`ahkpy.Window.activate`
   + - `WinActivateBottom <https://www.autohotkey.com/docs/commands/WinActivateBottom.htm>`_
     - ``ahkpy.Windows.last().activate()``
   + - `WinActive() <https://www.autohotkey.com/docs/commands/WinActive.htm>`_
     - :meth:`ahkpy.Windows.get_active`
   + - `WinClose <https://www.autohotkey.com/docs/commands/WinClose.htm>`_
     - :func:`ahkpy.Window.close`
   + - `WinExist() <https://www.autohotkey.com/docs/commands/WinExist.htm>`_
     - :meth:`ahkpy.Windows.first`
   + - `WinGet, ControlList <https://www.autohotkey.com/docs/commands/WinGet.htm#ControlList>`_
     - :attr:`ahkpy.Window.control_classes`
   + - `WinGet, ControlListHwnd <https://www.autohotkey.com/docs/commands/WinGet.htm#ControlListHwnd>`_
     - :attr:`ahkpy.Window.controls`
   + - `WinGet, Count <https://www.autohotkey.com/docs/commands/WinGet.htm#Count>`_
     - ``len(ahkpy.windows.filter())``
   + - `WinGet, ExStyle <https://www.autohotkey.com/docs/commands/WinGet.htm#ExStyle>`_
     - :attr:`ahkpy.Window.ex_style <ahkpy.window.BaseWindow.ex_style>`
   + - `WinGet, ID <https://www.autohotkey.com/docs/commands/WinGet.htm#ID>`_
     - :attr:`ahkpy.Window.id`
   + - `WinGet, IDLast <https://www.autohotkey.com/docs/commands/WinGet.htm#IDLast>`_
     - ``ahkpy.windows.last().id``
   + - `WinGet, List <https://www.autohotkey.com/docs/commands/WinGet.htm#List>`_
     - ``list(ahkpy.windows.filter())``
   + - `WinGet, MinMax <https://www.autohotkey.com/docs/commands/WinGet.htm#MinMax>`_
     - :attr:`ahkpy.Window.is_minimized`, :attr:`ahkpy.Window.is_maximized`, :attr:`ahkpy.Window.is_restored`
   + - `WinGet, PID <https://www.autohotkey.com/docs/commands/WinGet.htm#PID>`_
     - :attr:`ahkpy.Window.pid <ahkpy.window.BaseWindow.pid>`
   + - `WinGet, ProcessName <https://www.autohotkey.com/docs/commands/WinGet.htm#ProcessName>`_
     - :attr:`ahkpy.Window.process_name <ahkpy.window.BaseWindow.process_name>`
   + - `WinGet, ProcessPath <https://www.autohotkey.com/docs/commands/WinGet.htm#ProcessPath>`_
     - :attr:`ahkpy.Window.process_path <ahkpy.window.BaseWindow.process_path>`
   + - `WinGet, Style <https://www.autohotkey.com/docs/commands/WinGet.htm#Style>`_
     - :attr:`ahkpy.Window.style <ahkpy.window.BaseWindow.style>`
   + - `WinGet, TransColor <https://www.autohotkey.com/docs/commands/WinGet.htm#TransColor>`_
     - :attr:`ahkpy.Window.transparent_color`
   + - `WinGet, Transparent <https://www.autohotkey.com/docs/commands/WinGet.htm#Transparent>`_
     - :attr:`ahkpy.Window.opacity`
   + - `WinGetClass <https://www.autohotkey.com/docs/commands/WinGetClass.htm>`_
     - :attr:`ahkpy.Window.class_name <ahkpy.window.BaseWindow.class_name>`
   + - `WinGetPos <https://www.autohotkey.com/docs/commands/WinGetPos.htm>`_
     - :attr:`ahkpy.Window.rect <ahkpy.window.BaseWindow.rect>`, also
       :attr:`position <ahkpy.window.BaseWindow.position>`, :attr:`size <ahkpy.window.BaseWindow.size>`,
       :attr:`x <ahkpy.window.BaseWindow.x>`, :attr:`y <ahkpy.window.BaseWindow.y>`,
       :attr:`width <ahkpy.window.BaseWindow.width>`, :attr:`height <ahkpy.window.BaseWindow.height>` properties
   + - `WinGetText <https://www.autohotkey.com/docs/commands/WinGetText.htm>`_
     - :attr:`ahkpy.Window.text`
   + - `WinGetTitle <https://www.autohotkey.com/docs/commands/WinGetTitle.htm>`_
     - :attr:`ahkpy.Window.title`
   + - `WinHide <https://www.autohotkey.com/docs/commands/WinHide.htm>`_
     - :meth:`ahkpy.Window.hide() <ahkpy.window.BaseWindow.hide>`
   + - `WinKill <https://www.autohotkey.com/docs/commands/WinKill.htm>`_
     - :meth:`ahkpy.Window.kill`
   + - `WinMaximize <https://www.autohotkey.com/docs/commands/WinMaximize.htm>`_
     - :meth:`ahkpy.Window.maximize`
   + - `WinMinimize <https://www.autohotkey.com/docs/commands/WinMinimize.htm>`_
     - :meth:`ahkpy.Window.minimize`
   + - `WinMinimizeAll <https://www.autohotkey.com/docs/commands/WinMinimizeAll.htm>`_
     - :meth:`ahkpy.Windows.minimize_all`
   + - `WinMove <https://www.autohotkey.com/docs/commands/WinMove.htm>`_
     - :meth:`ahkpy.Window.move() <ahkpy.window.BaseWindow.move>`
   + - `WinRestore <https://www.autohotkey.com/docs/commands/WinRestore.htm>`_
     - :meth:`ahkpy.Window.restore`
   + - `WinSetTitle <https://www.autohotkey.com/docs/commands/WinSetTitle.htm>`_
     - :attr:`ahkpy.Window.title`
   + - `WinShow <https://www.autohotkey.com/docs/commands/WinShow.htm>`_
     - :meth:`ahkpy.Window.show() <ahkpy.window.BaseWindow.show>`
   + - `WinWait <https://www.autohotkey.com/docs/commands/WinWait.htm>`_
     - :meth:`ahkpy.Windows.wait`
   + - `WinWaitActive <https://www.autohotkey.com/docs/commands/WinWaitActive.htm>`_
     - :meth:`ahkpy.Windows.wait_active`
   + - `WinWaitClose <https://www.autohotkey.com/docs/commands/WinWaitClose.htm>`_
     - :meth:`ahkpy.Windows.wait_close`
   + - `WinWaitNotActive <https://www.autohotkey.com/docs/commands/WinWaitNotActive.htm>`_
     - :meth:`ahkpy.Window.wait_inactive`
