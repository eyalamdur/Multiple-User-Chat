PORT = 1732
IP = '0.0.0.0'

import socket
import select
import datetime
import re

def open_client(server_sock, open_sockets, name_and_sock, messages_to_send):
    """
    the function gets the server socket, list of messages, dictionary of names and sockets and the server socket list.
    the function add a new socket to the list and send message to all client that connected that a new connection has
    been made.
    """
    (new_socket, address) = server_sock.accept()
    open_sockets.append(new_socket)
    name_and_sock[new_socket] = new_socket.recv(1024)  # add client name to my name list
    for sock in open_sockets:
        if sock is not new_socket:
            time = datetime.datetime.time(datetime.datetime.now())
            messages_to_send.append((sock, str(time)[:5] + " " + name_and_sock[new_socket]
                                                       + " has joind the"" chat!"))
    print name_and_sock[new_socket] + " has been connected"
    return open_sockets


def close_client(delete_sock,open_sockets, names_and_sock, messages_to_send):
    """
    the function gets a socket, list of messages, dictionary of names and sockets and server socket list. the function
    delete the socket from the list and send message to all client that is still connected that the connection with the
    given sock is closed.
    """
    for sock in open_sockets:
        if sock is not delete_sock:
            time = datetime.datetime.time(datetime.datetime.now())
            messages_to_send.append((sock, str(time)[:5] + " " + names_and_sock[delete_sock] + " has left the chat!"))

    print ("The connection with '" + names_and_sock[delete_sock] + "' has been closed")
    del names_and_sock[delete_sock]
    open_sockets.remove(delete_sock)
    return open_sockets


def kick_client(delete_sock,open_sockets,names_and_sock, messages_to_send, wlist):
    """
    the function gets socket to delete, list of messages, dictionary of names and sockets and the server sockets list.
    and kick client from the chat.
    """
    for sock in open_sockets:
        if sock is not delete_sock:
            time = datetime.datetime.time(datetime.datetime.now())
            messages_to_send.append((sock, str(time)[:5] + " " + names_and_sock[delete_sock] + " was kicked out!"))
        else:
            time = datetime.datetime.time(datetime.datetime.now())
            messages_to_send.append((delete_sock, str(time)[:5] + " you were kicked out!"))
            send_waiting_messages(wlist, messages_to_send)
    print ("The connection with '" + names_and_sock[delete_sock] + "' has been closed (kicked out)")
    del names_and_sock[delete_sock]
    open_sockets.remove(delete_sock)


def add_manager(sock, names_and_sock,messages_to_send,open_sockets,data):
    """
    the function gets socket, list of messages, dictionary of names and sockets , the server sockets list and data.
    and make client from the chat to manager if he exist.
    """
    if names_and_sock[sock][0] == "@":
        to_add = is_name_exsist(data[4:], names_and_sock)
        if names_and_sock[to_add][0:1] != "@@":
            if to_add != False:
                names_and_sock[to_add] = "@" + names_and_sock[to_add]
                for sock in open_sockets:
                    if sock is not to_add:
                        time = datetime.datetime.time(datetime.datetime.now())
                        messages_to_send.append((sock, str(time)[:5] + " " + names_and_sock[to_add] + " is now manager!"))
                    else:
                        time = datetime.datetime.time(datetime.datetime.now())
                        messages_to_send.append((to_add, str(time)[:5] + " you've become a manager!"))
            else:
                time = datetime.datetime.time(datetime.datetime.now())
                messages_to_send.append((sock, str(time)[:5] + " The name you seek is not exist!"))
        else:
            time = datetime.datetime.time(datetime.datetime.now())
            messages_to_send.append((sock, str(time)[:5] + " The name you seek is already manager!"))
    else:
        time = datetime.datetime.time(datetime.datetime.now())
        messages_to_send.append((sock, str(time)[:5] + " You are not Manager!"))


def mute_client(delete_sock, open_sockets, messages_to_send, muted):
    """
    the function gets socket to mute, list of messages ,the server open sockets list and a muted clients list.
    and mute client if he is not already muted.
    """
    for sock in open_sockets:
        if (sock is delete_sock) and (delete_sock not in muted):
            time = datetime.datetime.time(datetime.datetime.now())
            messages_to_send.append((sock, str(time)[:5] + " you are now muted!"))
            muted.append(sock)
    return muted


def is_unmute(current_socket,names_and_sock,messages_to_send,data,muted):
    """
    the function gets socket to mute, list of messages and a muted clients list.
    and unmuted a client if he is muted.
    """
    if names_and_sock[current_socket][0] == "@":
        exsist = is_name_exsist(data[7:], names_and_sock)
        if (exsist != False):
            if exsist in muted:
                muted.remove(exsist)
                time = datetime.datetime.time(datetime.datetime.now())
                messages_to_send.append((exsist, str(time)[:5] + " You are not muted anymore!!"))
            else:
                time = datetime.datetime.time(datetime.datetime.now())
                messages_to_send.append((current_socket, str(time)[:5] + " This member is not muted!"))
        else:
            time = datetime.datetime.time(datetime.datetime.now())
            messages_to_send.append((current_socket, str(time)[:5] + " The name you seek is not exist!"))
    else:
        time = datetime.datetime.time(datetime.datetime.now())
        messages_to_send.append((current_socket, str(time)[:5] + " You are not Manager!"))
    return muted


def is_kick(sock, open_sockets, names_and_sock, messages_to_send, data, wlist):
    """
    the function gets socket, list of messages, list of names and sockets, the server open sockets list and a string.
    and check if client has been kicked by manager.
    """
    if names_and_sock[sock][0] == "@":
        to_kick = is_name_exsist(data[5:], names_and_sock)
        if to_kick != False:
            kick_client(to_kick, open_sockets, names_and_sock, messages_to_send, wlist)
        else:
                time = datetime.datetime.time(datetime.datetime.now())
                messages_to_send.append((sock, str(time)[:5] + " The name you seek not is exist!"))
    else:
        time = datetime.datetime.time(datetime.datetime.now())
        messages_to_send.append((sock, str(time)[:5] + " You are not Manager!"))


def is_mute(sock, open_sockets, names_and_sock, messages_to_send, data, muted):
    """
    the function gets socket, list of messages, list of names and sockets, the server open sockets list and a string.
    and check if client has been muted by manager.
    """
    if names_and_sock[sock][0] == "@":
        to_mute = is_name_exsist(data[5:], names_and_sock)
        if (to_mute != False):
            if to_mute in muted:
                time = datetime.datetime.time(datetime.datetime.now())
                messages_to_send.append((sock, str(time)[:5] + " This member is already muted!"))
            else:
                muted = mute_client(to_mute, open_sockets, messages_to_send, muted)
        if (to_mute == False):
            time = datetime.datetime.time(datetime.datetime.now())
            messages_to_send.append((sock, str(time)[:5] + " The name you seek is not exist!"))
    else:
        time = datetime.datetime.time(datetime.datetime.now())
        messages_to_send.append((sock, str(time)[:5] + " You are not Manager!"))
    return muted


def is_private(sock, names_and_sock, messages_to_send, data):
    """
    the function gets socket, list of messages, dictionary of names and sockets and data.
    and send private message from 'sock' to the client in the data if he exist.
    """
    name = get_name(data[7:])
    if name != None:
        private = is_name_exsist(name, names_and_sock)
        if private is sock:
            time = datetime.datetime.time(datetime.datetime.now())
            messages_to_send.append((private, str(time)[:5] + " You can't send messages to yourself!"))
            return True

        if (private != False):
            time = datetime.datetime.time(datetime.datetime.now())
            message = data
            for char in data:
                if char != ":":
                    message = message[1:]
                else:
                    break
            message = message[1:]
            messages_to_send.append((private, str(time)[:5] + " !"+names_and_sock[sock] + ":" + message))
            return True

        else:
            time = datetime.datetime.time(datetime.datetime.now())
            messages_to_send.append((sock, str(time)[:5] + " The name you seek is not exist!"))
            return True
    return False


def get_name(data):
    """
    the function gets a string with 'XXX: XXX' and returns the first group of letters.
    """
    match = re.search("(\S+)\:", data)
    try:
        return match.group(1)
    except:
        return None


def is_name_exsist(data, name_and_socket):
    """
    the function gets string and list of names and socket, and checks if the name exist in the list.
    """
    for sock in name_and_socket:
        if data == name_and_socket[sock] or "@" + data == name_and_socket[sock]:
            return sock
    return False


def send_waiting_messages(wlist, messages_to_send):
    """
    the function gets a list of messages and send the messages to all client that in her list.
    """
    for message in messages_to_send:
        (client_socket, data) = message
        if client_socket in wlist:
            client_socket.send(data)
            messages_to_send.remove(message)

"""---------------------------------------------------Main-----------------------------------------------------------"""
def Main():
    print "Server is on..."
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((IP, PORT))
    server_socket.listen(5)
    open_client_sockets = []
    messages_to_send = []
    name_and_socket = {}
    muted = []

    while (True):
        rlist, wlist, xlist = select.select([server_socket] + open_client_sockets, open_client_sockets, [])
        for current_socket in rlist:
            if current_socket is server_socket:
                open_client_sockets = open_client(current_socket, open_client_sockets, name_and_socket,messages_to_send)
            else:
                try:
                    data = current_socket.recv(1024)
                except:
                    data = ""
                if not data:
                    open_client_sockets = close_client(current_socket, open_client_sockets, name_and_socket,
                                                       messages_to_send)
                else:
                    if data[0:4] == "Kick":
                        is_kick(current_socket, open_client_sockets, name_and_socket, messages_to_send, data, wlist)
                        break

                    if data[0:4] == "Mute":
                        muted = is_mute(current_socket, open_client_sockets,name_and_socket,messages_to_send,data,muted)
                        break

                    if data[0:3] == "Add":
                        add_manager(current_socket, name_and_socket, messages_to_send, open_client_sockets,data)
                        break

                    if data[0:6] == "UnMute":
                        muted = is_unmute(current_socket,name_and_socket,messages_to_send,data,muted)
                        break

                    if current_socket in muted:
                        time = datetime.datetime.time(datetime.datetime.now())
                        messages_to_send.append((current_socket, str(time)[:5] + " You can't send messages!"))
                        break

                    if data[0:7] == "Private":
                        private = is_private(current_socket, name_and_socket, messages_to_send, data)
                        if private:
                            break

                    if data == "Manager list":
                        managers = ""
                        for sock in name_and_socket:
                            if name_and_socket[sock][0] == "@":
                                managers += name_and_socket[sock]+ ", "
                        time = datetime.datetime.time(datetime.datetime.now())
                        messages_to_send.append((current_socket, str(time)[:5] + " " + managers[:-2]))
                        break

                    print "Client send: " + data
                    for sock in open_client_sockets:
                        if sock is not current_socket:
                            time = datetime.datetime.time(datetime.datetime.now())
                            messages_to_send.append((sock, str(time)[:5]+" "+name_and_socket[current_socket]+": "+data))

        send_waiting_messages(wlist, messages_to_send)

if __name__ == '__main__':
    Main()