#!/usr/bin/python
# -- LCD_Socket: tcp_server.py --

import sys
import socket
import threading as thr

from lcd_display import LCD_Display

class TCP_Server:
    lock_counter = thr.Lock()
    lock_console = thr.Lock()
    lock_display = thr.Lock()
    
    CLOSE_MSG = '!SEQ'
    
    RESPONSE_SEQ = 'SEQ-NEXT'
    RESPONSE_SUCCESS = 'REQ-0'
    RESPONSE_FAILURE = 'REQ-1'
    
    def __init__(self, address : tuple, buffer_size : int, lcd_display : LCD_Display, format : str) -> None:
        self.address = address
        self.buffer_size = buffer_size
        self.connections = 0
        self.format = format
        
        self.lcd = lcd_display
        self.row_range = list(range(0, self.lcd.size['rows']))
    
    
    @staticmethod
    def _thread_print(text : str, err=False):
        with TCP_Server.lock_console:
            if err:
                sys.stderr.write(text)
            else:
                print(text)
    
    def _handle_request(self, request : str, addr : list):
        try:
            seqs = request.split('&', 1)
            
            seq1 = seqs[0].split('=', 1)
            if seq1[0] == 'ROW':
                row = int(seq1[1])
            else:
                TCP_Server._thread_print(f'{addr[0]}:{addr[1]}: Invalid input: {request}', err=True)
                return False
            
            seq2 = seqs[1].split('=', 1)
            if seq2[0] == 'TEXT':
                text = seq2[1]
            else:
                TCP_Server._thread_print(f'{addr[0]}:{addr[1]}: Invalid input: {request}', err=True)
                return False
            
            if not row in self.row_range:
                TCP_Server._thread_print(f'{addr[0]}:{addr[1]}: Invalid input: {request}', err=True)
                return False
            
            TCP_Server._thread_print(f'\tRequest: {addr[0]}:{addr[1]}:\n\t\t{row = }\n\t\t{text = }')
            
            with TCP_Server.lock_display:
                self.lcd.write(row=row, text=text)
                
            return True
            
        except IndexError or ValueError:
            TCP_Server._thread_print('-- Server Thread Error --', err=True)
            TCP_Server._thread_print(f'{type(e)} : {e}', err=True)
            return False
        
        except Exception as e:
            TCP_Server._thread_print('-- Unexpected Server Thread Error --', err=True)
            TCP_Server._thread_print(f'{type(e)} : {e}', err=True)
            return False

    def _handle_connection(self, conn, addr):
        with conn:
            
            with TCP_Server.lock_counter:
                self.connections += 1
            
            request = ""
            while True:
                data = conn.recv(self.buffer_size)
                
                if not data:
                    break
                
                if data.decode(self.format) == TCP_Server.CLOSE_MSG:
                    break
                
                request += data.decode(self.format)
                
                conn.sendall(TCP_Server.RESPONSE_SEQ.encode(self.format))
            
            if self._handle_request(request, addr):        
                conn.sendall(TCP_Server.RESPONSE_SUCCESS.encode(self.format))
            else:
                conn.sendall(TCP_Server.RESPONSE_FAILURE.encode(self.format))
            
            with TCP_Server.lock_counter:
                self.connections -= 1
    
        
    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(self.address)
            s.listen()
            
            print(f'Server is listening at {self.address[0]}:{self.address[1]}\n')
            
            while True:
                conn, addr = s.accept()
                
                connection = thr.Thread(target=self._handle_connection, args=(conn, addr, ), daemon=True)
                connection.name = f'<Thread>Connection[{addr}[1]:{addr[1]}]'
                connection.start()
