PORT = 1732
IP = "127.0.0.1"
MAX_CHR = 78
MANAGAR_CODE = "3299"


from Graphics import GraphWin, Text, Point, Rectangle, Entry, Image
import socket
import select
import datetime
import threading
import re


def login_window(window):
    """
     open the login window and gets from the user his nickname
    """

    "define my variables"
    enter_name = Text(Point(130,150), "Enter your Nickname:")
    backround_Login = Image(Point(130,130),r'Login_Backround.gif')
    max_chr = Text(Point(130,110), "Maximum character!")
    name = Text(Point(130,130),"")
    illegal_name = Text(Point(130,110),"Illegal Name!")
    """make my setting"""
    window.setCoords(0, 0, 256, 256)#sets the window coordinates ;bottom left is (0, 0) and top right is (256, 256)
    window.setBackground("White")
    max_chr.setTextColor("Red")
    illegal_name.setTextColor("Red")

    backround_Login.draw(window)
    enter_name.draw(window)

    while not window.isClosed():
        new_chr = window.getKey()
        max_chr.undraw()
        illegal_name.undraw()
        if new_chr == "Return":
            if len(name.getText()) < 1:
                illegal_name.draw(window)
            else:
                break
        if new_chr == "space":
            name.setText(name.getText() + " ")
            continue
        if new_chr == "BackSpace":
            name.setText(name.getText() + new_chr)
            name = delete_chr(name)
        else:
            if len(new_chr)>1:
                continue
            if (ord(new_chr) > 126 or ord(new_chr) < 33):
              continue
            else:
                name.setText(name.getText() + new_chr)
                if len(name.getText()) < 11:
                    name.undraw()
                    name.draw(window)
                else:
                    max_chr.draw(window)
                    name.setText(name.getText()[:-1])
                    name.undraw()
                    name.draw(window)
    enter_name.undraw()
    name.undraw()
    return name.getText()


def is_managar(window):
    """
    gets if the user is manager or not.
    """
    enter_code = Text(Point(130,150), "Enter Manager Code(0 if no managar):")
    code = Text(Point(130,130),"")
    max_chr = Text(Point(130,110), "Maximum character!")
    illegal_code = Text(Point(130,110),"Illegal Code!")
    wrong_code = Text(Point(130,110),"Wrong Code!")

    wrong_code.setTextColor("red")
    illegal_code.setTextColor("red")
    max_chr.setTextColor("red")

    enter_code.draw(window)
    code.draw(window)
    while (True):
        new_chr = window.getKey()
        max_chr.undraw()
        wrong_code.undraw()
        illegal_code.undraw()
        if new_chr == "Return":
            if len(code.getText()) > 4:
                max_chr.draw(window)
                wrong_code.undraw()
            if len(code.getText()) < 1:
                illegal_code.draw(window)
                wrong_code.undraw()
            if code.getText() == MANAGAR_CODE:
                return True
            if code.getText() == "0":
                return False
            if code.getText() != MANAGAR_CODE and len(code.getText()) > 0:
                wrong_code.draw(window)

        if new_chr == "Space":
            code.setText(code + " ")
        if new_chr == "BackSpace":
            code.setText(code.getText() + new_chr)
            code = delete_chr(code)
        else:
            if len(new_chr)> 1:
                continue
            if (ord(new_chr) > 126 or ord(new_chr) < 33):
              continue
            else:
                code.setText(code.getText() + new_chr)
                if len(code.getText()) < 5:
                    code.undraw()
                    code.draw(window)
                else:
                    max_chr.draw(window)
                    code.setText(code.getText()[:-1])


def delete_chr(text):
    """
    the function gets a msg and delete one character
    """
    """ if the user try to delete an empty line it will not allowed him:)"""
    if len(text.getText())<1:
        text.setText("")
        return text
    else:
        text.setText(text.getText()[:-10])       # 10 is the length of the word "Backspace" + 1 letter i delete
        return text


def chat_window(window, chat_lines, write_box):
    """
    open the chat window
    """
    for i in xrange(25):
        chat_lines[i] = Entry(Point(130,245-(i*9)),80)
        chat_lines[i].draw(window)
        chat_lines[i].setFill("white")
    write_box.draw(window) # draw it to the window
    help(chat_lines)


def reset_lines(chat_lines):
    """
    when the chat is full with messages,it will raise every message one line above and clear one line for a new message
    """
    for line in xrange(24):
        chat_lines[line].setText(chat_lines[line+1].getText())
        chat_lines[line].setTextColor(chat_lines[line+1].getTextColor())
    chat_lines[24].setText("")


def help(chat_lines):
    """
    print the order list.
    """
    for line in xrange(9):
        chat_lines[line].setTextColor("Blue")
    chat_lines[0].setText("------------------------------------------Welcome to the online chat - Amdur's Chat!--------"
                          "----------------------------------")
    chat_lines[1].setText("You can use the following commands:")
    chat_lines[2].setText("# 'Kick (Member)' - to kick a member (Only for Managers)")
    chat_lines[3].setText("# 'Mute/UnMute (Member)' - to mute or cancel a mute of member (Only for Managers)")
    chat_lines[4].setText("# 'Private (Member):' - to send message to a specific member ")
    chat_lines[5].setText("# 'Add (Member)' - to become a member to manager (Only for Managers)")
    chat_lines[6].setText("# 'Manager list' - for getting the manager list")
    chat_lines[7].setText("# 'Quit' - to leave chat ")
    chat_lines[8].setText("--------------------------------------------------------------------------------------------"
                          "----------------------------------------------------")


def send_waiting_messages(wlist, messages_to_send):
    """
    the function gets messages list and list of sockets to write and send the messages in the list to the right socket.
    """
    for message in messages_to_send:
        if wlist != []:
            wlist[0].send(message)
            messages_to_send.remove(message)

"""---------------------------------------------------Main-----------------------------------------------------------"""
def Main():
    """Declaration of variables"""
    window = GraphWin(width = 800, height = 600)          #creates the window
    chat_lines = {0:Entry(Point(130,250),70)}
    write_box = Entry(Point(130, 13),80)                  # create a entry box from (50, 10) to (250, 30)
    illegal_msg = Text(Point(130,4),"Invalid message!")
    messages_to_send = []

    """Setting the variables """
    illegal_msg.setTextColor("Red")


    #open the login window and returns the client nickname & if he is manager
    client_name = login_window(window)
    if is_managar(window):
        client_name = "@" + client_name

    #open the chat window
    chat_window(window, chat_lines, write_box)

    #open socket with server
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.connect((IP, PORT))

    """Send my name to the server """
    rlist, wlist, xlist = select.select([my_socket],[my_socket],[])
    messages_to_send.append(client_name)
    send_waiting_messages(wlist, messages_to_send)

    """ MAIN LOOP """
    while not(window.isClosed()):
        rlist, wlist, xlist = select.select([my_socket],[my_socket],[])

        if rlist != []:
            for curret_socket in rlist:
                data = curret_socket.recv(1024)
                if chat_lines[24].getText() != "":
                    reset_lines(chat_lines)

                for line in chat_lines:
                    if chat_lines[line].getText() == "":
                        chat_lines[line].setTextColor("Red")
                        chat_lines[line].setText(data)
                        break

        """Gets key press from the client """
        last_chr = window.checkKey()

        """ If pressed 'Enter' """
        if last_chr == "Return":
            illegal_msg.undraw()
            if (len(write_box.getText()) <1):
                illegal_msg.draw(window)
            else:
                time = datetime.datetime.time(datetime.datetime.now())
                messages_to_send.append(write_box.getText())
                if chat_lines[24].getText() != "":
                    reset_lines(chat_lines)
                for line in chat_lines:
                    if chat_lines[line].getText() == "":
                        if write_box.getText()[:7] == "Private":
                            chat_lines[line].setText(str(time)[:5] + " Me: !" +write_box.getText()[8:])
                        else:
                            chat_lines[line].setText(str(time)[:5] + " Me: " + write_box.getText())
                        chat_lines[line].setTextColor("Green")
                        break

            "check if i need to close the window"
            if write_box.getText() == "Quit":
                break
            else:
                write_box.setText("")

        send_waiting_messages(wlist, messages_to_send)

    my_socket.close()
    window.close()

if __name__ == '__main__':
  Main()