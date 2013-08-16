from wx import *
import wx.richtext as rt
import time

BUTTON_WIDTH = 55
REGISTER_BUTTON_WIDTH = 70
BUTTON_BUFFER = 10
TEXT_BOX_HEIGHT = 30
LABEL_BUFFER = 100
BORDER = 10
TEXT_BOX_BUFFER = 10
LOGIN_WINDOW_WIDTH = 375
LOGIN_WINDOW_HEIGHT = 155

X_INDEX = 0
Y_INDEX = 1



class LoginWindow(Frame):

    def __init__(self):
        self.app = App(False)
        Frame.__init__(self, None, title = "Log In", size = (LOGIN_WINDOW_WIDTH, LOGIN_WINDOW_HEIGHT))

        self.username_input = TextCtrl(self, style = TE_PROCESS_ENTER, pos = (LABEL_BUFFER + BORDER, TEXT_BOX_BUFFER), size = (self.GetSizeTuple()[X_INDEX] - LABEL_BUFFER - BORDER * 2, TEXT_BOX_HEIGHT))
        self.password_input = TextCtrl(self, style = TE_PROCESS_ENTER | TE_PASSWORD, pos = (LABEL_BUFFER + BORDER,self.username_input.GetPositionTuple()[Y_INDEX] + TEXT_BOX_HEIGHT + TEXT_BOX_BUFFER), size = (self.GetSizeTuple()[X_INDEX] - LABEL_BUFFER - BORDER * 2,TEXT_BOX_HEIGHT))
        self.password_input_2 =  TextCtrl(self, style = TE_PROCESS_ENTER | TE_PASSWORD, pos = (LABEL_BUFFER + BORDER,self.password_input.GetPositionTuple()[Y_INDEX] + TEXT_BOX_HEIGHT + TEXT_BOX_BUFFER), size = (LOGIN_WINDOW_WIDTH - LABEL_BUFFER - BORDER * 2,TEXT_BOX_HEIGHT))
        self.password_input_2.Hide()

        StaticText(self, label = "Username", pos = (BORDER, self.username_input.GetPositionTuple()[Y_INDEX]))
        StaticText(self, label = "Password", pos = (BORDER, self.password_input.GetPositionTuple()[Y_INDEX]))
        self.register_text = HyperlinkCtrl(self, id = ID_ANY, url = "", pos = (LABEL_BUFFER + BORDER, self.password_input.GetPositionTuple()[Y_INDEX] + TEXT_BOX_HEIGHT), label = "New here? Register here")
        self.register_text.Bind(EVT_HYPERLINK, self.register_mode)
        self.register_text.Hide()
        self.login_button = Button(self, label = "Login", size = (BUTTON_WIDTH,TEXT_BOX_HEIGHT), pos = ((self.GetSizeTuple()[X_INDEX] - BUTTON_WIDTH) / 2, self.register_text.GetPositionTuple()[Y_INDEX] + self.register_text.GetSizeTuple()[Y_INDEX] + BORDER))

        self.register_button =  Button(self, label = "Register", size = (REGISTER_BUTTON_WIDTH,TEXT_BOX_HEIGHT))
        self.register_button.Hide()
        self.message = StaticText(self, pos = (BORDER, self.GetSizeTuple()[Y_INDEX] - BORDER * 2))
        self.Show(True)
        
    def close(self):
        self.Destroy()

    def register_mode(self, event):
        self.SetSize(Size(LOGIN_WINDOW_WIDTH, LOGIN_WINDOW_HEIGHT + TEXT_BOX_BUFFER + TEXT_BOX_HEIGHT))
        self.username_input.Clear()
        self.password_input.Clear()
        self.register_button.SetPosition(((self.GetSizeTuple()[X_INDEX] - BUTTON_WIDTH * 2) /2, self.GetSizeTuple()[Y_INDEX] - TEXT_BOX_HEIGHT * 2))
        self.login_button.Hide()
        self.register_text.Hide()
        self.retype_label = StaticText(self, label = "Retype\nPassword", pos = (BORDER, self.password_input_2.GetPositionTuple()[Y_INDEX]))
        self.password_input_2.Show()
        self.register_button.Show()
        self.cancel_button =  Button(self, label = "Cancel", size = (BUTTON_WIDTH,TEXT_BOX_HEIGHT), pos = ((self.register_button.GetPositionTuple()[X_INDEX] + self.register_button.GetSizeTuple()[X_INDEX]), self.register_button.GetPositionTuple()[Y_INDEX]))
        self.cancel_button.Bind(EVT_BUTTON, self.login_mode)
        self.message.SetPosition((BORDER, self.GetSizeTuple()[Y_INDEX] - BORDER * 2))
        if self.message.GetLabel() != "": 
            self.message.SetLabel("")

    def login_mode(self, event = None):
        self.SetSize((LOGIN_WINDOW_WIDTH, LOGIN_WINDOW_HEIGHT))
        self.register_button.Hide()
        self.login_button.Show()
        self.register_text.Show()
        self.password_input_2.Hide()
        self.retype_label.Destroy()
        self.cancel_button.Destroy()
        self.message.SetPosition((BORDER, self.GetSizeTuple()[Y_INDEX] - BORDER * 2))
        if self.message.GetLabel() != "": 
            self.message.SetLabel("")


    def bind_functions(self, on_register, on_login):
        self.login_button.Bind(EVT_BUTTON, on_login)
        self.register_button.Bind(EVT_BUTTON, on_register)

    def mainloop(self):
        self.app.MainLoop()

    def get_login_info(self):
        return str(self.username_input.GetValue()), str(self.password_input.GetValue())

    def get_register_info(self):
        register_info = str(self.username_input.GetValue()), str(self.password_input.GetValue()), str(self.password_input_2.GetValue())
        self.password_input.Clear()
        self.password_input_2.Clear()
        return register_info
     
    def set_message(self, text):
        self.message.SetLabel(text)


MENU_WINDOW_WIDTH = 400
MENU_WINDOW_HEIGHT = 200
MENU_BUTTON_WIDTH = 150
MENU_BUTTON_HEIGHT = 60

class MenuWindow(Frame):

    def __init__(self):
        self.app = App(False)
        Frame.__init__(self, None, title = "Menu Window", size = (MENU_WINDOW_WIDTH, MENU_WINDOW_HEIGHT))
        self.enter_game = Button(self, label = "Enter Game Lobby", size = (MENU_BUTTON_WIDTH, MENU_BUTTON_HEIGHT), pos = ((self.GetSizeTuple()[X_INDEX] - (MENU_BUTTON_WIDTH * 2 + 30))/2, (self.GetSizeTuple()[Y_INDEX] - MENU_BUTTON_HEIGHT)/2))
        self.change_password_button = Button(self, label = "Change Password", size = (MENU_BUTTON_WIDTH, MENU_BUTTON_HEIGHT), pos = ((self.GetSizeTuple()[X_INDEX] + 30)/2, self.enter_game.GetPositionTuple()[Y_INDEX]))
        self.change_password_button.Bind(EVT_BUTTON, self.change_password_mode)
        self.change_button = Button(self, label = "Change", size = (BUTTON_WIDTH * 2,TEXT_BOX_HEIGHT))
        self.change_button.Hide()
        self.Show(True)


    def close_window(self, event, start_chat):
        self.Close()
        start_chat()

    def mainloop(self):
        self.app.MainLoop()

    def change_password_mode(self, event):
        self.enter_game.Hide()
        self.change_password_button.Hide()
        self.password_input = TextCtrl(self, style = TE_PROCESS_ENTER | TE_PASSWORD, pos = (LABEL_BUFFER + BORDER, TEXT_BOX_BUFFER), size = (self.GetSizeTuple()[X_INDEX] - LABEL_BUFFER - BORDER * 2, TEXT_BOX_HEIGHT))
        self.new_password_input = TextCtrl(self, style = TE_PROCESS_ENTER | TE_PASSWORD, pos = (LABEL_BUFFER + BORDER,self.password_input.GetPositionTuple()[Y_INDEX] + TEXT_BOX_HEIGHT + TEXT_BOX_BUFFER), size = (self.GetSizeTuple()[X_INDEX] - LABEL_BUFFER - BORDER * 2,TEXT_BOX_HEIGHT))
        self.new_password_input_2 =  TextCtrl(self, style = TE_PROCESS_ENTER | TE_PASSWORD, pos = (LABEL_BUFFER + BORDER,self.new_password_input.GetPositionTuple()[Y_INDEX] + TEXT_BOX_HEIGHT + TEXT_BOX_BUFFER), size = (MENU_WINDOW_WIDTH - LABEL_BUFFER - BORDER * 2,TEXT_BOX_HEIGHT))
        self.new_2_label = StaticText(self, label = "Confirm New\nPassword", pos = (BORDER, self.new_password_input_2.GetPositionTuple()[Y_INDEX]))
        self.current = StaticText(self, label = "Current\nPassword", pos = (BORDER, self.password_input.GetPositionTuple()[Y_INDEX]))
        self.new_label = StaticText(self, label = "New Password", pos = (BORDER, self.new_password_input.GetPositionTuple()[Y_INDEX]))
        self.change_button.SetPosition(((self.GetSizeTuple()[X_INDEX] - BUTTON_WIDTH * 3) / 2, self.new_password_input_2.GetPositionTuple()[Y_INDEX] + TEXT_BOX_HEIGHT + BORDER))
        self.change_button.Show()
        self.back_button =  Button(self, label = "Go Back", size = (BUTTON_WIDTH * 2,TEXT_BOX_HEIGHT), pos = (self.change_button.GetPositionTuple()[X_INDEX] + BUTTON_WIDTH * 2, self.change_button.GetPositionTuple()[Y_INDEX]))
        self.back_button.Bind(EVT_BUTTON, self.menu_mode)
        self.message = StaticText(self, pos = (0, self.GetSizeTuple()[Y_INDEX] - TEXT_BOX_HEIGHT))

    def get_password_info(self):
        return str(self.password_input.GetValue()), str(self.new_password_input.GetValue()), str(self.new_password_input_2.GetValue())

    def set_message(self, text):
        self.message.SetLabel(text)

    def bind_options(self, connect_fn, change_fn):
        self.change_button.Bind(EVT_BUTTON, change_fn)
        self.enter_game.Bind(EVT_BUTTON, lambda event, start_chat = connect_fn: self.close_window(event, start_chat))

    def menu_mode(self, event):
        self.new_label.Hide()
        self.current.Hide()
        self.change_button.Hide()
        self.back_button.Hide()
        self.password_input.Hide()
        self.new_password_input_2.Hide()
        self.new_password_input.Hide()
        self.new_2_label.Hide()
        self.enter_game.Show()
        self.change_password_button.Show()
        self.message.SetLabel("")
