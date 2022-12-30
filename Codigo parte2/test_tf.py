#TRABAJO FINAL - Carlos Carbajal Jordan

#Se importan la librerias a utilizar
import threading #ejecución varios procesos a la vez: un proceso para recibir y otro para enviar message
from threading import Event
import sys
import socket
import time
import tkinter as tk
import tkinter.ttk as ttk
import serial
import serial.tools.list_ports
from tkinter.scrolledtext import ScrolledText
from tkinter.messagebox import showinfo, askokcancel
from datetime import datetime
from collections import OrderedDict
from cryptography.fernet import Fernet



HEADER = 10

class Servidor:
    HOST = "127.0.0.1"
    PORT = 5000

    def __init__(self):
        print("Creando socket...", end="")
        self.conexiones = []
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((Servidor.HOST, Servidor.PORT))
        self.socket.listen()
        print("OK")
        
        print("\n==================================")
        hora = int(datetime.strftime(datetime.now(),'%H'))
        minutos = int(datetime.strftime(datetime.now(),'%M'))
        if hora>12:
            print(f"Server anonimo iniciado\nTime:[{hora-12:02d}:{minutos:02d} p.m.]")
        else:
            print(f"Server anonimo iniciado\nTime:[{hora:02d}:{minutos:02d} a.m.]")
        print("==================================\n")

    def run(self):
        th = threading.Thread(target=self.run_hilo,args=(self.socket,),daemon=True)
        th.start()
        try:
            while True:
                pass
        except KeyboardInterrupt:
            self.socket.close()

    def run_hilo(self,s):
        print("Esperando conexiones")
        try:
            while True:
                conn, addr = s.accept()                 #Esperar peticiones de conexion
                th = threading.Thread(target=self.handler, args=(conn,addr), daemon=True)   #Crear hilo que maneja la nueva conexion
                th.start()                                          #Comenzar hilo
                print(str(addr[0])+":"+str(addr[1]),"conectado")    #Informar sobre la nueva conexion
                self.conexiones.append(conn)                        #Agregar la nueva conexion a la lista
        except Exception as e:
            print(e)
            print("Servidor cerrado")

    def handler(self,conn,addr):
        while True:
            try:
                data_header = conn.recv(HEADER)             #Recivir cantidad de bytes
                data = conn.recv(int(data_header))          #Recivir mensaje
                for conexion in self.conexiones:            #Para todas las conexiones
                    if conexion != conn:                    #Excepto el emisor
                        conexion.send(data_header+data)     #Mandar el mismo mensaje
            except:
                print(str(addr[0])+":"+str(addr[1]),"desconectado") #Informar sobre la desconexion
                self.conexiones.remove(conn)                #Quitar de la lista
                conn.close()                                #Cerrar conexion (liberar socket)
                break                                       #Salir del bucle y terminar metodo

class ClienteGUI:
    def __init__(self,name):
        
        #-------PARTE DE INTERFAZ-------

        self.master = tk.Tk()
        self.master.title("Usuario anonimo")
        self.master.geometry("+50+50")
        self.master.resizable(0, 0)
        self.master.iconbitmap('icon_chat_sha.ico') #icono de wsp
        self.lineas_archivo = []
        #mensaje con la key del cifrado (inicia un message box)
        self.inicio=True
        #genero la key
        self.KEY = Fernet.generate_key()

        #Menu pricipal (toda la barra)
        main_menu = tk.Menu(self.master)
        #Agregar menu principal a la ventana
        self.master.config(menu=main_menu,bg="#4c4c4c")
        #Crear una lista de opciones (submenu sin nombre)
        info_comandos = tk.Menu(main_menu, tearoff=False)
        #Agregar opciones al submenu. Cada opcion ejecuta una funcion
        info_comandos.add_command(label="decodificar",command=self.decodifica)
        #Agregar submenu al menu principal con un nombre
        main_menu.add_cascade(label="Ayuda", menu=info_comandos)
        

        self.var_encrip = tk.IntVar() #para los radio button
        self.var_color=tk.IntVar()
        # ------------------------ FRAMES -----------------------------
        frm1 = tk.LabelFrame(self.master, text="Conexion",bg="#4c4c4c",fg="#ffffff")
        self.frm2 = tk.Frame(self.master,bg="#4c4c4c")
        frm3 = tk.LabelFrame(self.master, text="Enviar mensaje",bg="#4c4c4c",fg="#ffffff")
        frm4 = tk.LabelFrame(self.master, text="Desea codificar",bg="#4c4c4c",fg="#ffffff")
        frm5 = tk.LabelFrame(self.master, text="Cambio de color",bg="#4c4c4c",fg="#ffffff")
        
        frm1.pack(padx=5, pady=5, anchor=tk.W)
        self.frm2.pack(padx=5, pady=5, fill='y', expand=True)
        frm3.pack(padx=5, pady=5)
        frm4.pack(padx=5, pady=5)
        frm5.pack(padx=5, pady=5)

        # ------------------------ FRAME 1 ----------------------------
        
        #Textos de widgets
        self.conexionVar = tk.StringVar(value="Conectar")
        self.ipVar = tk.StringVar(value="127.0.0.1")
        self.nombreVar = tk.StringVar(value="5000")
        self.name_antes = tk.StringVar(value=sys.argv[1])
        self.code=tk.StringVar(value=self.KEY)
        
        #Label, Entry y Button
        self.lblIP = tk.Label(frm1, text="Direccion IP:",bg="#4c4c4c",fg="#ffffff")
        self.entryIP = ttk.Entry(frm1,textvariable=self.ipVar)
        self.lblPuerto = tk.Label(frm1, text="Puerto:",bg="#4c4c4c",fg="#ffffff")
        self.entryPuerto = tk.Entry(frm1,textvariable=self.nombreVar)
        self.btnConnect = tk.Button(frm1, textvariable=self.conexionVar,command=self.conectar_con_servidor, width=16,bg="#4c4c4c",fg="#ffffff")
        
        #Colocar nombre
        self.nombre_antes_conectado = tk.Label(frm1, text="Nombre de usuario: ",bg="#4c4c4c",fg="#ffffff")
        self.nombre_antes_conectar = ttk.Entry(frm1,textvariable=self.name_antes)
        #KEY generada
        self.nombre_key = tk.Label(frm1, text="code: ",bg="#4c4c4c",fg="#ffffff")
        self.keygenerado = ttk.Entry(frm1,textvariable=self.code)
        
        self.lblIP.grid(row=0, column=0, padx=5, pady=5)
        self.entryIP.grid(row=0,column=1,padx=5,pady=5)
        self.lblPuerto.grid(row=0,column=2, padx=30, pady=5)
        self.entryPuerto.grid(row=0,column=3,padx=5,pady=5)
        self.btnConnect.grid(row=0, column=4, padx=5, pady=5)
        
        
        self.nombre_antes_conectado.grid(row=1, column=0, padx=5, pady=5)
        self.nombre_antes_conectar.grid(row=1,column=1,padx=5,pady=5)
        self.nombre_key .grid(row=1, column=2, padx=5, pady=5)
        self.keygenerado.grid(row=1,column=3,padx=5,pady=5)
        # ------------------------ FRAME 2 ---------------------------
        self.crearTxtChat()
        self.normas()
            
        # ------------------------ FRAME 3 --------------------------
        #Texto de widget
        self.msgVar = tk.StringVar()
        
        #Label, Entry y Button
        self.lblText = tk.Label(frm3, text="Mensaje:",bg="#4c4c4c",fg="#ffffff")
        self.inText = tk.Entry(frm3, textvariable=self.msgVar,width=45, state='disable')
        #command=lambda: self.enviar_mensaje(None) -> Para darle el evento que pide.(en este caso None porque no hay evento)
        self.btnSend = tk.Button(frm3, text="Enviar", width=12, state='disable',command=lambda: self.enviar_mensaje(None),bg="#4c4c4c",fg="#ffffff")
        
        self.inText.bind("<Return>", self.enviar_mensaje) #Tecla ENTER para enviar mensaje
        self.inText.bind("<Key>", self.actualizandoStatusBar) #detectar caracteres para "Escribiendo mensaje..."
        self.lblText.grid(row=0, column=0, padx=5, pady=5)
        self.inText.grid(row=0, column=1, padx=5, pady=5)
        self.btnSend.grid(row=0, column=2, padx=5, pady=5)
        #-------------------------------fmr4----------------------------------------
        #----------------------------Selecion  de encriptacion (si o no)
        self.sinconversion = tk.Radiobutton(frm4, text="Sin encriptar",bg="#4c4c4c", variable=self.var_encrip, value=0,
                                            fg='white', activebackground='#4c4c4c',selectcolor='red',activeforeground='white')
        self.conconversion = tk.Radiobutton(frm4, text="Encriptado",bg="#4c4c4c", variable=self.var_encrip, value=1,
                                            fg='white' ,activebackground='#4c4c4c',selectcolor='red',activeforeground='white')
        
        self.lblText.grid(row=0, column=0, padx=5, pady=5)
        self.inText.grid(row=0, column=1, padx=5, pady=5)
        self.btnSend.grid(row=0, column=2, padx=5, pady=5)
        self.sinconversion.grid(row=0, column=0, padx=5, pady=5,sticky=tk.W)
        self.conconversion.grid(row=0, column=1, padx=5, pady=5,sticky=tk.W)

        #----------------------------Selecion  de  color  (si o no)
        self.colorVar = tk.StringVar()
        self.sinccambiocolor = tk.Radiobutton(frm5, text="Default",bg="#4c4c4c", variable=self.var_color, value=0,
                                            fg='white', activebackground='#4c4c4c',selectcolor='red',activeforeground='white')
        self.coloramarillo = tk.Radiobutton(frm5, text="Amarillo",bg="#4c4c4c", variable=self.var_color, value=1,
                                            fg='white' ,activebackground='#4c4c4c',selectcolor='red',activeforeground='white')
        self.colorblanco = tk.Radiobutton(frm5, text="Blanco",bg="#4c4c4c", variable=self.var_color, value=2,
                                            fg='white' ,activebackground='#4c4c4c',selectcolor='red',activeforeground='white')
        self.colormorado = tk.Radiobutton(frm5, text="Morado",bg="#4c4c4c", variable=self.var_color, value=3,
                                            fg='white' ,activebackground='#4c4c4c',selectcolor='red',activeforeground='white')

        self.sinccambiocolor.grid(row=0, column=0, padx=5, pady=5,sticky=tk.W)
        self.coloramarillo.grid(row=0, column=1, padx=5, pady=5,sticky=tk.W)
        self.colorblanco.grid(row=0, column=2, padx=5, pady=5,sticky=tk.W)
        self.colormorado.grid(row=0, column=3, padx=5, pady=5,sticky=tk.W)
        
        # --------------------------- StatusBar -----------------------
        self.statusBar = tk.Label(self.master, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.statusBar.pack(side=tk.BOTTOM, fill=tk.X)

        # ------------- Control del boton "X" de la ventana -----------
        self.master.protocol("WM_DELETE_WINDOW", self.cerrar_ventana)
        #----------------------------mensaje de entrada de la  key-----------------------------
        if (self.inicio == True):
            #self.clave = Fernet(self.KEY)
            showinfo(title="key para decodificar", message=f"Tu llave es: {self.KEY}")
            self.cambionombre=False
            self.inicio = False
        print(f"clave: {str(self.KEY)}")
        


        #------PARTE DE CONEXION--------

        self.conectado = False
        self.nombreUsuario = name
        self.evento = Event()

    def boton_guardar(self):
        self.statusBar.config(text=f"Decodificado de {self.nombreUsuario} guardado")
        archivo=open(f"{self.nombreUsuario}_ChatGuardado.txt","w")
        archivo.writelines(self.lineas_archivo)
        archivo.close()

    def crearTxtChat(self):
        self.txtChat = ScrolledText(self.frm2, height=25, width=50, wrap=tk.WORD, state='disable')
        self.txtChat.grid(row=0, column=0, columnspan=3, padx=5, pady=5)
        self.txtChat.config(bg = '#000000')

        self.txtChat.tag_config('azul', foreground='#53b1f1')
        self.txtChat.tag_config('rojo', foreground='red')
        self.txtChat.tag_config('verde', foreground='#75bf6a')
        #adicionales
        self.txtChat.tag_config('amarillo', foreground='#ffdf3d')
        self.txtChat.tag_config('blanco', foreground='#ffffff')
        self.txtChat.tag_config('morado', foreground='#a970ff')
        


    #Conectar con servidor
    def conectar_con_servidor(self):
        # Uso get para recibir el valor de los entry
        self.ip = self.entryIP.get()
        self.puerto = int(self.entryPuerto.get())
        
        #PARTE PARA CONECTAR
        if self.conectado==False:# si el puerto está desconectado
            try:
                self.nombreUsuario = self.name_antes.get()
                
                self.statusBar.config(text=f"Conectando a IP: {self.ip} | Puerto: {self.puerto} como '{self.nombreUsuario}'")
                #Estableciendo comunicación con servidor
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((self.ip, self.puerto))
                #Configurar widgets
                self.entryPuerto.config(state='disabled')
                self.entryIP.config(state='disabled')
                self.conexionVar.set("Desconectar")
                self.inText.config(state='normal') #La entrada de texto se activa
                self.btnSend.config(state='normal') #El boton de enviar se activa
                #self.codecolor.config(state='normal')#activo ingreso de color
                #self.escogecolores=self.codecolor.get()
                self.conectado=True #entonces se vuelve conectado
                self.statusBar.config(text=f"Conectado a IP:{self.ip} | Puerto: {self.puerto} como '{self.nombreUsuario}'")
                self.hilo_recibir = threading.Thread(target=self.recibir_mensaje,daemon=True)
                self.hilo_recibir.start()
                self.txtChat.delete(0, 'end')
                msg = f"     ----{self.nombreUsuario} se ha unido---"
                msg_encode = msg.encode("utf-8")
                msg_encode = (f"{len(msg_encode):<{HEADER}}{msg}").encode("utf-8")           
                self.socket.send(msg_encode) 
                
                self.master.title(f"Cliente de chat: {self.nombreUsuario}")
                
                self.nombre_antes_conectar.config(state = 'disabled')
            #Si no se pudo conectar...
            except Exception as e:
                print(e)
                self.statusBar.config(text=f"Error al conectarse con IP:{self.ip} | Puerto:{self.puerto}")
        #PARTE PARA DESCONECTAR
        else:# si el puerto está conectado. Este elsef entra cuando se está desconectando.
            
            if askokcancel(title="Borrar chat", message="Se eliminarán los mensajes: ¿Estás seguro que desea borrar?"):
                msg = f"     ----{self.nombreUsuario} se ha desconectado---"
                msg_encode = msg.encode("utf-8")
                msg_encode = (f"{len(msg_encode):<{HEADER}}{msg}").encode("utf-8")           
                self.socket.send(msg_encode) 
                time.sleep(0.5)
            
                self.socket.close()
                self.conexionVar.set("Conectar") #el botón de pone en conectar
                self.inText.delete(0, 'end') #Para borrar los caracteres en el entry del frm3 cuando se desconecta.
                #Creando uno nuevo scrolledText. Simula la limpieza de chat.
                self.crearTxtChat()
                #Como es para desconectar la entrada de texto y el boton se deshabilitan.
                self.normas()
                
                self.inText.config(state='disabled')
                self.btnSend.config(state='disabled')
                #self.codecolor.config(state='disabled')
                self.entryPuerto.config(state='normal')
                self.entryIP.config(state='normal')
                self.evento.set()
                self.conectado=False #puerto desconectado
                self.master.title("Cliente de Chat")
                self.nombreUsuario = sys.argv[1]
                self.nombre_antes_conectar.config(state = 'normal')
    #Cierra ventana y conexiones
    def cerrar_ventana(self):
        try:
           self.socket.close()
        except:
            pass
        self.master.destroy()
    
    #Abre informacion sobre el servidor
    def infoServidor(self):
        showinfo(title="Información Servidor", message=f"IP:{Servidor.HOST}\n Puerto:{Servidor.PORT}")

    
    def enviar_mensaje(self,event): #el evento es NONE. Se envia con click en Enviar o con el ENTER del teclado
        # Texto del mensaje enviado
        texto_entry = self.inText.get()


        if (self.var_encrip.get() == 1):
            fernet = Fernet(self.KEY)
            texto_cod=str(fernet.encrypt(texto_entry.encode()))
            texto_cod=texto_cod[2:]
            texto_cod=texto_cod[:-1]

        elif (self.var_encrip.get() == 0):
            texto_cod=str(texto_entry)

        texto = self.nombreUsuario + ": " + texto_cod
        texto_serial = texto.encode("utf-8")

        
        if (texto_entry != ''):
            texto_encode = f"{len(texto_serial):<{HEADER}}".encode("utf-8")+texto_serial # se crea el mensaje
            self.socket.send(texto_encode) #se envia el mensaje hacia el servidor.
            self.txtChat.config(state='normal') #ScrolledText estado normal (habilitado)
        
            #Al enviar mensaje, se tendrá texto de color azul
            if(self.var_color.get()==0):
                self.insertar_texto(texto,'azul')
            if(self.var_color.get()==1):
                self.insertar_texto(texto,'amarillo')
            if(self.var_color.get()==2):
                self.insertar_texto(texto,'blanco')
            if(self.var_color.get()==3):
                self.insertar_texto(texto,'morado')
        
            # Threading
            #El contador para borrar el statusBar.Después de un 1seg borra el mensaje de escribiendo y recibiendo mensaje.
            #Aquí se crea el hilo, que ejecuta el método tiempo.
            th1sec = threading.Thread(target=self.tiempo, args=(1,0,), daemon=True) #1,0 enviando mensaje. (tiempoespera,envio)
            th1sec.start() #Aquí comienza el hilo y comienza a contar 1seg, por el método tiempo.
        
            #Borrar entrada de texto
            self.inText.delete(0, 'end') #Luego de enviarse el mensaje debe de borrarse en el entry.
            self.txtChat.config(state='disabled') #Deshabilita el chat para evitar escribir.
    
        
    
    def recibir_mensaje(self):
        while True:
            try:
                data_header = self.socket.recv(HEADER)
                if data_header:
                    data = self.socket.recv(int(data_header))
                    mensaje = data.decode('utf-8') #se decodifica
                    self.txtChat.config(state='normal')

                    # Threading
                    #Se crea un hilo para contar 1seg. Luego de ello se va a cambiar el texto del statusBar.
                    th2sec = threading.Thread(target=self.tiempo, args=(1,1,), daemon=True) #1,1 recibiendo mensaje (tiempoespera,recibiendo)
                    th2sec.start()
                    #Al recibir mensaje, se tendrá texto de color rojo
                    self.insertar_texto(mensaje,'rojo')
                    self.txtChat.config(state='disabled')
            except:
                break
        print("Conexion cerrada")
        self.statusBar.config(text="Desconectado") #Para limpiar el StatusBar cuando se desconecta

    #El mensaje que aparece en el status cuando se detecta caracteres en el entry del frame3    
    def actualizandoStatusBar(self,event):
        self.statusBar.config(text='Escribiendo mensaje...')
    
    #Método para insertar un texto en el ScrolledText. Tanto los mensajes de los usuarios junto con la hora de envío.
    def insertar_texto(self,mensaje,colormsj): #Argumentos (mensaje, color del mensaje)
        hora = int(datetime.strftime(datetime.now(),'%H'))
        minutos = int(datetime.strftime(datetime.now(),'%M'))
        linea = ""
        
        if hora>12:
            linea =str(mensaje)+f"\n[{hora-12:02d}:{minutos:02d} p.m.]\n"
            
        else:
            linea =str(mensaje)+f"\n[{hora:02d}:{minutos:02d} a.m.]\n"
        self.txtChat.insert(tk.INSERT,linea,colormsj) 
        
        
        self.txtChat.yview(tk.END)
        

    def tiempo(self,delay,i):
        # El tiempo lo cambias en threading
        if i==0:
            self.statusBar.config(text="Enviando mensaje... ")
            time.sleep(delay)               #Tiempo de 1s
            self.statusBar.config(text="")  #Luego de un 1 segundo lo borra
        elif i==1:
            self.statusBar.config(text="Recibiendo mensaje... ")
            time.sleep(delay)               #Tiempo de 1s
            self.statusBar.config(text="")  #Luego de un 1segundo lo borra

    def decodifica(self):
        #Abre ventana nueva
        self.codigo = tk.Toplevel(self.master)

        self.codigo.title("Decodificador")
        self.codigo.geometry("+100+100")
        self.codigo.resizable(0, 0)
        self.codigo.iconbitmap('icon_chat_sha.ico')
        self.codigo.config(bg="#4c4c4c")
        self.lineas_archivo = []

        #----------subventana frames----------------------------------
        self.frm11=tk.LabelFrame(self.codigo,text= "Ingreso de KEY",bg="#4c4c4c",fg="#ffffff")
        self.frm22 = tk.LabelFrame(self.codigo,text="Mensaje decodificado",bg="#4c4c4c",fg="#ffffff")
        self.frm33 = tk.LabelFrame(self.codigo, text="Enviar mensaje",bg="#4c4c4c",fg="#ffffff")
        self.frm11.pack(padx=5, pady=5,anchor=tk.W)
        self.frm22.pack(padx=5, pady=5, fill='y', expand=True)
        self.frm33.pack(padx=5, pady=5,anchor=tk.W)


        #-------------------frm subventana1------------------------------------
        #-------------------frame 1-----------------------------------------------
        self.lblText1 = tk.Label(self.frm11, text="Ingrese la key:",bg="#4c4c4c",fg="#ffffff")
        self.inText1 = tk.Entry(self.frm11, width=60)
        self.lblText1.grid(row=0, column=0, padx=5, pady=5)
        self.inText1.grid(row=0, column=1, padx=5, pady=5)

        # ------------------------ FRAME 2 ---------------------------
        self.txtChat1 = ScrolledText(self.frm22, height=20, width=40, wrap=tk.WORD)
        self.txtChat1.config(state='disabled')
        self.txtChat1.grid(row=0, column=0, columnspan=3, padx=5, pady=5)

        #--------------------------FRAME 3-------------------------------------------
        self.lblText2 = tk.Label(self.frm33, text="Texto:",bg="#4c4c4c",fg="#ffffff")
        self.inText2 = tk.Entry(self.frm33, width=45)
        self.btn_guardar = tk.Button(self.frm33, text="Guardar", width=16, command=self.boton_guardar,bg="#4c4c4c",fg="#ffffff")

        self.inText2.bind("<Return>", self.enviar_mensaje_key) #Tecla ENTER para enviar mensaje
        self.inText2.bind("<Key>", self.actualizandoStatusBar) #detectar caracteres para "Escribiendo mensaje..."

        self.btnSend1 = tk.Button(self.frm33, text="Enviar", width=12,command=lambda: self.enviar_mensaje_key(None),bg="#4c4c4c",fg="#ffffff")


        self.lblText2.grid(row=0, column=0, padx=5, pady=5)
        self.inText2.grid(row=0, column=1, padx=5, pady=5)
        self.btnSend1.grid(row=0, column=2, padx=5, pady=5)
        self.btn_guardar.grid(row=1, column=2, padx=5, pady=5)

    def enviar_mensaje_key(self,event):
        #agarra la llave que se puso en el entry para decodificar

        self.KEY_DEC=self.inText1.get()
        fernet_dec = Fernet(self.KEY_DEC)
        #agarra  el dato a desencriptar
        mensaje_cifrar=self.inText2.get()
        self.txtChat1.config(state='normal', foreground='#53b1f1')
        #proceso de desencriptar
        mensaje_dec = fernet_dec.decrypt(mensaje_cifrar).decode()
        #fecha
        fecha=f"{datetime.strftime(datetime.now(),'%H'+':'+'%M')}"
        hora = int(fecha[:2])
        minutos = int(fecha[-2:])
        if hora>12:
            codificado=str(mensaje_dec)+f"\n {hora-12:02d}:{minutos:02d} p.m.\n"

        else:
            codificado=str(mensaje_dec)+f"\n {hora:02d}:{minutos:02d} a.m.\n"

        self.txtChat1.insert(tk.INSERT,codificado)

        self.txtChat1.yview(tk.END)
        self.lineas_archivo.append(codificado)
        self.txtChat1.config(state='disabled')
        self.inText2.delete(0, 'end')
        
    def normas(self):
        fileObject = open("logo.txt", "r")
        data = fileObject.read()
        print(data)
        linea=data
        self.txtChat.config(state='normal')
        self.txtChat.insert(tk.INSERT,linea,'verde') 
        fileObject = open("mensaje.txt", "r")
        data = fileObject.read()
        linea=data
        self.txtChat.insert(tk.INSERT,linea,'verde') 
        self.txtChat.yview(tk.END)
        self.txtChat.config(state='disabled')


def main():
    #Crear servidor
    if len(sys.argv)==1:
        Servidor().run()
    #Crear cliente
    if len(sys.argv)==2:
        cliente = ClienteGUI(sys.argv[1])
        cliente.master.mainloop()

if __name__=="__main__":
    main()