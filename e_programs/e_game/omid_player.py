from wx import *
from wx.lib.ogl import *
from waiting_room import WaitingRoom
from omid_player_emitted import OmidPlayer
from gui_string import GUI_String_Ext
import threading
from gui_node import GUI_Node
from gui_arc import GUI_Arc
import time, sys, os
sys.path.append(os.path.join('../../'))
from waldo.lib import Waldo
HOSTNAME = '127.0.0.1'
OMID_PORT = 6770
CIRCLE_DIAMETER = 50
WINDOW_WIDTH = 500
WINDOW_HEIGHT = 500
BUTTON_WIDTH = 50
TEXT_BOX_HEIGHT = 30
NUMBER_INPUT_WIDTH = 50
ANSWER_INPUT_WIDTH = 300
LABEL_WIDTH = 50
BUFFER = 10

class OmidGamePlayer(Frame):

    def __init__(self, name):
        self.name = name
        self.waiting = WaitingRoom(name + "'s Omid Game Waiting Room")
        self.waiting.bind_functs(self.read_waiting_room_message)
        self.app = App(False)
        Frame.__init__(self, None, title = name + "'s Omid Game", size = (WINDOW_WIDTH, WINDOW_HEIGHT))
        OGLInitialize() 
        sizer = BoxSizer(VERTICAL)
        self.canvas = ShapeCanvas(self)
        sizer.Add(self.canvas, 1, GROW)
        self.canvas.SetBackgroundColour("WHITE")
        self.diagram = Diagram()
        self.canvas.SetDiagram(self.diagram)
        self.SetSizer(sizer)
        self.SetAutoLayout(1)
        self.Centre()
        num_label = StaticText(self.canvas, label = "#", pos = (BUFFER, WINDOW_HEIGHT - TEXT_BOX_HEIGHT))
        answer_label = StaticText(self.canvas, label = "answer", pos = (num_label.GetSize().x + BUFFER+ NUMBER_INPUT_WIDTH, WINDOW_HEIGHT - TEXT_BOX_HEIGHT))
        self.number_input = TextCtrl(self, style = TE_PROCESS_ENTER, pos = (num_label.GetSize().x + BUFFER, WINDOW_HEIGHT - (TEXT_BOX_HEIGHT + BUFFER)), size = (NUMBER_INPUT_WIDTH, TEXT_BOX_HEIGHT))
        self.answer_input = TextCtrl(self, style = TE_PROCESS_ENTER, pos = (answer_label.GetPosition().x + answer_label.GetSize().x + BUFFER, WINDOW_HEIGHT - (TEXT_BOX_HEIGHT + BUFFER)), size = (ANSWER_INPUT_WIDTH, TEXT_BOX_HEIGHT))
        self.number_input.Bind(EVT_TEXT_ENTER, self.read_answer)
        self.answer_input.Bind(EVT_TEXT_ENTER, self.read_answer)
        self.score = StaticText(self.canvas, pos = (WINDOW_WIDTH - 30, BUFFER)) 
        self.player = Waldo.tcp_connect(OmidPlayer, HOSTNAME, OMID_PORT, name, GUI_String_Ext(
self.waiting.get_gui_screen()), GUI_Node(self.draw_circle), GUI_Arc(self.draw_arc), self.clear_map, self.refresh_window)       
        self.waiting.mainloop()

    def check_signal(self):
        while True:
            self.player.service_signal()
            time.sleep(0.1)

    def clear_map(self, endpoint):
        self.diagram.DeleteAllShapes()

    def update_score(self, endpoint, number):
        self.score.SetLabel(str(number).replace(".0", ""))
        
    def draw_arc(self, endpt, arc):
        line = LineShape()
        line.SetEnds(arc[0], arc[1], arc[2], arc[3])
        line.SetBrush(Brush('BLACK', style = SOLID))
        self.canvas.AddShape(line)
        line.Show(True)
    

    def draw_circle(self, node):
        self.circle = CircleShape(CIRCLE_DIAMETER)
        if node['found']:
            self.circle.SetBrush(Brush('BLACK', style = SOLID))
            self.circle.SetTextColour('WHITE')
            self.circle.AddText(node['answer'])
        else:
            self.circle.SetBrush(Brush('WHITE', style = SOLID))
            self.circle.SetTextColour('BLACK')
            self.circle.AddText(node['node_num'])
        self.circle.SetX(node['x'])
        self.circle.SetY(node['y'])
        self.canvas.AddShape(self.circle)
        self.circle.Show(True)

    def refresh_window(self, endpt):
        self.Show(False)
        self.Show(True)

    def display_game_window(self):
        self.Show()
        self.app.MainLoop()

    def read_answer(self, event):
        number = str(self.number_input.GetValue())
        self.number_input.Clear()
        answer = str(self.answer_input.GetValue())
        self.answer_input.Clear()
        self.player.send_answer(number, answer)

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
            self.player.send_to_waiting(self.name + ": " + message)
