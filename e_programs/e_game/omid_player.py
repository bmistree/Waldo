from wx import *
from wx.lib.ogl import *
from waiting_room import WaitingRoom
from omid_player_emitted import OmidPlayer
from gui_string import GUI_String_Ext
import time, sys, os
sys.path.append(os.path.join('../../'))
from waldo.lib import Waldo
HOSTNAME = '127.0.0.1'
OMID_PORT = 6768
CIRCLE_DIAMETER = 50
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 500
BUTTON_WIDTH = 50
TEXT_BOX_HEIGHT = 30
NUMBER_INPUT_WIDTH = 100


class OmidPlayer(Frame):

    def __init__(self, name):
        self.waiting = WaitingRoom(name + "'s Omid Game Waiting Room")
        self.waiting.bind_functs(self.read_waiting_room_message)
        self.player = Waldo.tcp_connect(OmidPlayer, HOSTNAME, OMID_PORT, name, GUI_String_Ext(self.waiting.get_gui_screen()), self.draw_circle, self.clear_map)

        self.app = App(False)
        Frame.__init__(self, None, title = name + "'s Omid Game", size = (WINDOW_WIDTH, WINDOW_HEIGHT))
        OGLInitialize() 
        sizer = BoxSizer(VERTICAL)
        self.canvas = ShapeCanvas(self)
        sizer.Add(self.canvas, 1, GROW)

        self.canvas.SetBackgroundColour("WHITE")
        self.diagram = Diagram()
        self.canvas.SetDiagram(self.diagram)
        self.diagram.SetCanvas(self.canvas)
        self.SetSizer(sizer)
        self.SetAutoLayout(1)
        self.Centre()
        self.answer_input = TextCtrl(self, style = TE_PROCESS_ENTER, pos = (0, WINDOW_HEIGHT - TEXT_BOX_HEIGHT), size = (WINDOW_WIDTH - BUTTON_WIDTH - NUMBER_INPUT_WIDTH, TEXT_BOX_HEIGHT))
        self.number_input = TextCtrl(self, style = TE_PROCESS_ENTER, pos = (0, WINDOW_HEIGHT - TEXT_BOX_HEIGHT), size = (NUMBER_INPUT_WIDTH, TEXT_BOX_HEIGHT))


    def clear_map(self, endpoint):
        self.diagram.DeleteAllShapes()
#Make draw arc function
    
    def draw_arc(self, endpoint, x1, y1, x2, y2):
        line = LineShape()
        line.SetEnds(x1, y1, x2, y2)
        line.SetBrush(Brush('BLACK', style = SOLID))

    def draw_circle(self, endpoint, x_pos, y_pos, found, num, text):
        circle = CircleShape(CIRCLE_DIAMETER)
        if found:
            circle.SetBrush(Brush('BLACK', style = SOLID))
            circle.SetTextColour('WHITE')
            circle.AddText(text)
        else:
            circle.SetBrush(Brush('WHITE', style = SOLID))
            circle.SetTextColour('BLACK')
            circle.AddText(str(num))
        circle.SetX(x_pos)
        circle.SetY(y_pos)
        self.canvas.AddShape(circle)
        circle.Show(True)

    def display_game_window(self):
        self.Show()
        self.app.MainLoop()

    def read_waiting_room_message(self, event):
        message = self.waiting.get_input()
        if len(message) > 0 and message[0] is "/":
            message = message[1:]
            if message == "ready\n":
                if self.player.game_in_session():
                    self.waiting.display_message("Cannot enter game room. Game is in session.\n")
                else:
                    self.player.add_to_game()
                    time.sleep(1)
                    self.display_game_window()
            elif message == "leave\n":
                self.leave_waiting()
            else:
                self.waiting.display_message('Cannot read command.  Below are valid commands.\n\t"/ready" to try to enter the game room.\n\t"/leave" to leave the waiting room.\n')
        else:
            self.player.send_to_waiting(message)
