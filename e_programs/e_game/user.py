from user_emitted import User
from user_login_emitted import UserLogin
from server_emitted import Server
from player_emitted import Player
from anagram_player import AnagramPlayer
from gui_string import GUI_String_Ext
from login import LoginWindow, MenuWindow
from wx import *
import sys, os, time
sys.path.append(os.path.join("../../"))
from waldo.lib import Waldo
import OpenSSL
HOSTNAME = '127.0.0.1'
PORT = 6922
WORD_MIN = 3
WORD_MAX = 7
name = ""
ADMIN_NAME = "Admin"
BUTTON_WIDTH = 50
TEXT_BOX_HEIGHT = 30
CHAT_WINDOW_WIDTH = 400
CHAT_WINDOW_HEIGHT = 500
MESSAGE_BOX_HEIGHT = 450
KEY_TEXT_FILE = "user_key.pem"
CERT_TEXT_FILE = "user_cert.pem"
MIN_PASSWORD_LENGTH = 6
MIN_USERNAME_LENGTH = 3
KEY_MANAGER_HOST = '127.0.0.1'
KEY_MANAGER_PORT = 6974



def create_chat_window():
    app = App(False)
    frame = Frame(None, -1, title = name + "'s Game Lobby Window", size = (CHAT_WINDOW_WIDTH, CHAT_WINDOW_HEIGHT))
    global text_display
    text_display = TextCtrl(frame, size = (CHAT_WINDOW_WIDTH, MESSAGE_BOX_HEIGHT), style = TE_READONLY | TE_MULTILINE)
    global text_input
    text_input = TextCtrl(frame, style = TE_PROCESS_ENTER, pos = (0,CHAT_WINDOW_HEIGHT - TEXT_BOX_HEIGHT), size = (CHAT_WINDOW_WIDTH - BUTTON_WIDTH, TEXT_BOX_HEIGHT))
    send_button = Button(frame, label = "Send", size = (BUTTON_WIDTH,TEXT_BOX_HEIGHT), pos = (CHAT_WINDOW_WIDTH - BUTTON_WIDTH, CHAT_WINDOW_HEIGHT - TEXT_BOX_HEIGHT))
    text_input.Bind(EVT_TEXT_ENTER, send_message)    
    send_button.Bind(EVT_BUTTON, send_message)
    frame.Show(True)
    return app

def on_login (event):
    login_info = login.get_login_info()
    encrypted_key = user_login.get_encrypted_key(login_info[0], login_info[1])
    if encrypted_key != "":
        global name
        name = login_info[0]
        password_hashed = Waldo.hash(login_info[1], user_login.get_salt(name))
        global key
        key = Waldo.decrypt_keytext(encrypted_key, password_hashed)
        global certificate
        certificate = Waldo.get_cert_from_text(user_login.get_certificate(name))
        if name == ADMIN_NAME:
            login.register_mode(None)
        else:
            login.close()
    else:
        login.set_message("Username/password combination was not found.")
        
def on_register (event):
    register_info = login.get_register_info() #contains tuple (username, password, password)
    if register_info[1] != register_info[2]:
        login.set_message("Passwords do not match.")
    elif len(register_info[1]) < MIN_PASSWORD_LENGTH:
        login.set_message("Password length must be at least 6 characters long.")
    elif not register_info[0].isalnum() or len(register_info[0]) < MIN_USERNAME_LENGTH:
        login.set_message("Username must consist of at least 3 alphanumeric characters")
    else:
        name = register_info[0]
        if user_login.unique_username(name):
            key = Waldo.get_key()
            salt = Waldo.salt()
            password = register_info[1]
            password_hashed = Waldo.hash(password, salt)
            user_login.register_user(name, password_hashed, Waldo.encrypt_keytext(key, password_hashed), Waldo.generate_request(name, key), salt)
            login.login_mode()
            login.set_message("Account created! You can now login.")
        else:
            login.set_message("Username is already used.")



def login_user():
    global user_login
    user_login = Waldo.stcp_connect(UserLogin, HOSTNAME, PORT + 1)
    global login
    login = LoginWindow()
    login.bind_functions(on_register, on_login)
    login.mainloop()
    if name == "":
        exit(0)

def menu_window():
    global menu
    menu = MenuWindow()
    menu.bind_options(connect_user, on_change_password)
    menu.mainloop()

def on_change_password(event):
    password_info = menu.get_password_info() #contains tuple (current password, new password, new password)
    cur_password = password_info[0]
    if user_login.get_encrypted_key(name, cur_password) != "":
        if password_info[1] == password_info[2]:
            new_password = password_info[1]
            salt = user_login.get_salt(name)
            new_pw_hash = Waldo.hash(new_password, salt)
            user_login.change_password(name, Waldo.encrypt_keytext(key, new_pw_hash), new_pw_hash)
            menu.set_message("Password has been changed.")
        else:
            menu.set_message("New passwords do not match.")
    else:
        menu.set_message("Username/password combination was not found.")


def connect_user():
    app = create_chat_window()
    gui_string = GUI_String_Ext(text_display)
    global user
    user = Waldo.stcp_connect(User, HOSTNAME, PORT, gui_string, key = key, cert = certificate)
    user.set_name(name)
    text_display.AppendText("You have been added to the chat server.\n")
    user.add_to_server()
    app.MainLoop()

    
def read_command(message):
    if message.startswith('quit'):
        user.quit()
        exit(0)

    elif message.startswith('private'):
       new_start = len('private ')
       new_message = message[new_start:]
       if (new_message == ""):
           text_display.AppendText('Username must be specified.\n')
       else:
           split_message = new_message.partition(' ')#split_message now contains the tuple (username,' ',message) 
           user.private_message(split_message[0], split_message[2]);

    elif message.startswith('users_list'):
       user.print_users()

    elif message.startswith('anagram_game'):
        anagram_player = AnagramPlayer(name)

    elif message.startswith('h'):
        text_display.AppendText('Commands:\n\t/quit - to leave the chatroom.\n\t/private [username] [message] - to send a private message.\n\t/users_list - to see a list of users.\n\t/anagram_game - to enter the anagram game.\n')

    else:
       text_display.AppendText("Invalid command. Type /h for a list of commands.\n")

def send_message(event):
    message = str(text_input.GetValue() + "\n")
    text_input.Clear()
    if len(message) > 0 and message[0] is "/":
        message = message[1:]
        read_command(message)
    else:
        user.send_message(message)

if __name__ == '__main__':
    login_user()
    menu_window()
