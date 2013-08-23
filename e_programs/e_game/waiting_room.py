from wx import *

BUTTON_WIDTH = 50
TEXT_BOX_HEIGHT = 30
WAITING_WINDOW_WIDTH = 500
WAITING_WINDOW_HEIGHT = 500
MESSAGE_BOX_HEIGHT = 450


class WaitingRoom(Frame):

    def __init__(self, window_title):
        self.app = App(False)
        Frame.__init__(self, None, title = window_title, size = (WAITING_WINDOW_WIDTH, WAITING_WINDOW_HEIGHT))
        self.text_display = TextCtrl(self, size = (WAITING_WINDOW_WIDTH, MESSAGE_BOX_HEIGHT), style = TE_READONLY | TE_MULTILINE)
        self.text_input = TextCtrl(self, style = TE_PROCESS_ENTER, pos = (0,WAITING_WINDOW_HEIGHT - TEXT_BOX_HEIGHT), size = (WAITING_WINDOW_WIDTH - BUTTON_WIDTH, TEXT_BOX_HEIGHT))
        self.send_button = Button(self, label = "Send", size = (BUTTON_WIDTH, TEXT_BOX_HEIGHT), pos = (WAITING_WINDOW_WIDTH - BUTTON_WIDTH, WAITING_WINDOW_HEIGHT - TEXT_BOX_HEIGHT))
        self.Show(True)


    def mainloop(self):
        self.app.MainLoop()

    def bind_functs(self, read_message):
        self.text_input.Bind(EVT_TEXT_ENTER, read_message)    
        self.send_button.Bind(EVT_BUTTON, read_message)

    def get_input(self):
        input_text = str(self.text_input.GetValue() + "\n")
        self.text_input.Clear()
        return input_text

    def display_message(self, message):
        self.text_display.AppendText(message)

    def get_gui_screen(self):
        return self.text_display

    def close(self):
        self.Close()
