#TRABAJO FINAL - Carlos Carbajal Jordan
#Se importan la librerias a utilizar
import threading #ejecución varios procesos a la vez: un proceso para recibir y otro para enviar message
import time
import tkinter as tk
import tkinter.ttk as ttk
import serial
import serial.tools.list_ports
from tkinter.scrolledtext import ScrolledText
from tkinter.messagebox import showinfo
from datetime import datetime
from collections import OrderedDict
from cryptography.fernet import Fernet


class SerialChat:
    def __init__(self, master):

        self.master = master #padre de la ventana. Contiene todo.
        self.puerto=0 #Valor inicial de puerto
        self.puerto_conectado=False #Estado de la conexion
        self.master.title("Chat anonimo")
        self.master.geometry("+50+50")
        self.master.resizable(0, 0)
        self.master.iconbitmap('icon_chat_sha.ico') #icono del chat
        #####Insertar el menu de información para cambiar nombre de usuario######
        main_menu = tk.Menu(self.master)

        self.master.config(menu=main_menu,bg="#4c4c4c")
        #mensaje con la key del cifrado (inicia un message box)
        self.inicio=True
        # Se definen los menus (submenus) del menu principal
        info_comandos = tk.Menu(main_menu, tearoff=False)
        #info_comandos.add_command(label="Información para cambiar nombre", command=self.infoNombre)
        main_menu.add_cascade(label="Ayuda", menu=info_comandos)
        info_comandos.add_command(label="decodificar",command=self.decodifica)
        info_comandos.add_command(label="editar_nombre",command=self.cambiar_nombre)

        #############Nombre inicial del boton##########################################

        self.conexion = tk.StringVar() #Texto del boton Conectar
        self.conexion.set("Conectar") #.set, método para cambiar el texto del StringVar()
        self.var_encrip = tk.IntVar() #para los radio button
        # ---------------------- SERIAL PORT --------------------------
        #Se obtiene información de los puertos disponibles
        ports = serial.tools.list_ports.comports()
        print("SE TIENEN LOS SIGUIENTES PUERTOS A UTILIZAR:\n")
        for port in ports: #Puertos disponibles
            print(port)

        self.puertos=[]

        for port in ports:
                p1,p2 = str(port).split('-')
                p1=p1.replace(' ','')
                self.puertos.append(p1)
        self.puertos=list(OrderedDict.fromkeys(self.puertos))



        # ------------------------ FRAMES -----------------------------
        frm1 = tk.LabelFrame(self.master, text="Conexion",bg="#4c4c4c",fg="#ffffff")
        self.frm2 = tk.Frame(self.master,bg="#4c4c4c")
        frm3 = tk.LabelFrame(self.master, text="Enviar mensaje",bg="#4c4c4c",fg="#ffffff")
        frm4 = tk.LabelFrame(self.master, text="Desea codificar",bg="#4c4c4c",fg="#ffffff")
        frm1.pack(padx=5, pady=5, anchor=tk.W)
        self.frm2.pack(padx=5, pady=5, fill='y', expand=True)
        frm3.pack(padx=5, pady=5)
        frm4.pack(padx=5, pady=5)

        # ------------------------ FRAME 1 ----------------------------
        self.lblCOM = tk.Label(frm1, text="Puerto COM:",bg="#4c4c4c",fg="#ffffff")
        #values obtenido en ports = serial.tools.list_ports.comports()
        self.cboPort = ttk.Combobox(frm1, values=self.puertos, state = 'readonly') #readonly para que no se edite el Combobox
        self.lblSpace = tk.Label(frm1, text="",bg="#4c4c4c",fg="#ffffff")
        self.btnConnect = tk.Button(frm1, textvariable=self.conexion,command=self.seleccionando_puertosCOM, width=16,bg="#4c4c4c",fg="#ffffff")

        self.lblCOM.grid(row=0, column=0, padx=5, pady=5)
        self.cboPort.grid(row=0, column=1, padx=5, pady=5)
        self.lblSpace.grid(row=0,column=2, padx=30, pady=5)
        self.btnConnect.grid(row=0, column=3, padx=5, pady=5)

        # ------------------------ FRAME 2 ---------------------------
        self.txtChat = ScrolledText(self.frm2, height=25, width=50, wrap=tk.WORD, state='disable')
        self.txtChat.grid(row=0, column=0, columnspan=3, padx=5, pady=5)

        # ------------------------ FRAME 3 --------------------------
        self.lblText = tk.Label(frm3, text="Texto:",bg="#4c4c4c",fg="#ffffff")
        self.inText = tk.Entry(frm3, width=45, state='disable')


        self.inText.bind("<Return>", self.enviar_mensaje) #Tecla ENTER para enviar mensaje
        self.inText.bind("<Key>", self.actualizandoStatusBar) #detectar caracteres para "Escribiendo mensaje..."

        #command=lambda: self.enviar_mensaje(None) -> Para darle el evento que pide.(en este caso None porque no hay evento)
        self.btnSend = tk.Button(frm3, text="Enviar", width=12, state='disable',command=lambda: self.enviar_mensaje(None),bg="#4c4c4c",fg="#ffffff")
        #-------------------------------------fmr4--------------------------
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

        # --------------------------- StatusBar -----------------------
        self.statusBar = tk.Label(self.master, bd=1, relief=tk.SUNKEN, anchor=tk.W,bg="#4c4c4c",fg="#ffffff")
        self.statusBar.pack(side=tk.BOTTOM, fill=tk.X)
        #----------------------------mensaje de entrada de la  key-----------------------------
        if (self.inicio == True):
            self.KEY = Fernet.generate_key()
            #self.clave = Fernet(self.KEY)
            showinfo(title="key para decodificar", message=f"Tu llave es: {self.KEY}")
            self.cambionombre=False
            self.inicio = False
        print(f"clave: {self.KEY}")

        # ------------- Control del boton "X" de la ventana -----------
        self.master.protocol("WM_DELETE_WINDOW", self.cerrar_puertos)

        #------------- recibe el mensaje del emisor -----------
        self.master.after(1000,self.recibir_mensaje()) #espera que pase 1seg y llama a recibir_mensaje y dentro hay otro after y allí se hace el bucle

    #Cuando se cierra la ventana se cierra las comunicaciones y se cierra la ventana. Solo cuando se clickea en la 'X'
    def cerrar_puertos(self):
        try:
            self.serial.close()
        except:
            pass
        self.master.destroy()
    #El mensaje que aparece en el status cuando se detecta caracteres en el entry del frame3
    def actualizandoStatusBar(self,event):
        self.statusBar.config(text='Escribiendo mensaje...')
        


    ###--Proceso de seleccionar puertos-----
    def seleccionando_puertosCOM(self):
        # Uso get para recibir el valor del combobox
        self.puerto= self.cboPort.get()

        #PARTE DE CONEXION
        #Estado desconectado  (habilitacion de botones e ingreso de info)
        if(self.puerto_conectado==False):# si el puerto está desconectado
            self.puerto_conectado=True #entonces se vuelve conectado
            self.cboPort.config(state='disabled')
            self.conexion.set("Desconectar")
            self.inText.config(state='normal') #La entrada de texto se activa
            self.btnSend.config(state='normal') #El boton de enviar se activa

        #Estado de conexion (deshabilita los botones y borrar  info)
        elif(self.puerto_conectado==True):# si el puerto está conectado. Este elif entra cuando se está desconectando.
            self.conexion.set("Conectar") #el botón de pone en conectar
            self.puerto_conectado=False #puerto desconectado
            self.puerto=0
            self.ser.close() #se cierran las conexiones. 'ser' es el objeto que representa la conexion serial.
            self.inText.delete(0, 'end') #Para borrar los caracteres en el entry del frm3 cuando se desconecta.
            ##
            #Creando uno nuevo scrolledText. Simula la limpieza de chat.
            self.txtChat = ScrolledText(self.frm2, height=25, width=50, wrap=tk.WORD, state='disable')
            self.txtChat.grid(row=0, column=0, columnspan=3, padx=5, pady=5)
            ##

            #Como es para desconectar la entrada de texto y el boton se deshabilitan.
            self.inText.config(state='disabled')
            self.btnSend.config(state='disabled')
            self.cboPort.config(state='readonly') #Con esto se habilita el combobox donde están los puertos COM
            self.statusBar.config(text="") #Para limpiar el StatusBar cuando se desconecta
            return
        #Lo que está debajo es para conectar.

        ##Esto se hace cuando se está conectando######
        try:
            #Estableciendo comunicación con puerto serial {PORT}
            self.statusBar.config(text="Conectado al "+str(self.puerto)+" a 9600")
            self.ser = serial.Serial(port=self.puerto,
                                baudrate=9600,
                                bytesize=8,
                                timeout=2,
                                stopbits=serial.STOPBITS_ONE)

        #Si no se pudo conectar...
        except:
            self.conexion.set("Conectar") #se pone en conectar el botón
            self.puerto_conectado=True #Puerto desconectado

            self.inText.config(state='disabled') #Entrada de texto se deshabilitan
            self.btnSend.config(state='disabled') #El boton de enviarse se deshabilitan
            self.cboPort.config(state='readonly') #El combobox se activa para seleccionar un puerto. No se puede escribir allí.
            #print(self.puerto)
            if self.puerto == '': #Cuando no se ha seleccionado un puerto...
                self.statusBar.config(text="Error: No hay puerto seleccionado")
            else: #Cuando ya esté usado ese puerto...
                self.statusBar.config(text="Error al conectarse a "+str(self.puerto))
            self.puerto=0 #se resetea el puerto, porque no se ha conectado nada. Puerto al que se está conectando, pero no se pudo

    #Método para insertar un texto en el ScrolledText. Tanto los mensajes de los usuarios junto con la hora de envío.
    def insertar_texto(self,mensaje,colormsj): #Argumentos (mensaje, color del mensaje)
        fecha=f"{datetime.strftime(datetime.now(),'%H'+':'+'%M')}"
        #print(fecha)

        hora = int(fecha[:2])
        minutos = int(fecha[-2:])

        if hora>12:
            self.txtChat.insert(tk.INSERT,str(mensaje)+f"\n {hora-12:02d}:{minutos:02d} p.m.\n",colormsj)
        else:
            self.txtChat.insert(tk.INSERT,str(mensaje)+f"\n {hora:02d}:{minutos:02d} a.m.\n",colormsj)
        self.txtChat.yview(tk.END)

    #---------MÉTODO PARA ENVIAR MENSAJE----------
    def enviar_mensaje(self,event): #el evento es NONE. Se envia con click en Enviar o con el ENTER del teclado

        # Texto del mensaje enviado
        texto=self.inText.get()
        #--------------Para  seleccionar el nombre de usuario
        if(self.cambionombre == True):
            self.nombreUsuario = self.nombrenuevo
        elif(self.cambionombre == False):
            self.nombreUsuario = self.cboPort.get()

        if (self.var_encrip.get() == 1):
            fernet = Fernet(self.KEY)
            texto_cod=str(fernet.encrypt(texto.encode()))
            texto_cod=texto_cod[2:]
            texto_cod=texto_cod[:-1]

        elif (self.var_encrip.get() == 0):
            texto_cod=str(texto)

        texto=str(self.nombreUsuario)+": "+ texto_cod
        #Se establece cómo se puede cambiar el nombre del usuario a través de un comando explicado en tk.Menu
        texto_encode=texto.encode("utf-8")
        self.ser.write(texto_encode) #se envia el mensaje hacia el otro COM.
        self.txtChat.config(state='normal') #ScrolledText estado normal (habilitado)

        #Al enviar mensaje, se tendrá texto de color azul
        self.insertar_texto(texto,'azul')

            # Threading
        #En contador para borrar el statusBar.Después de un 1seg borra el mensaje de escribiendo y recibiendo mensaje.
        #Aquí se crea el hilo, que ejecuta el método tiempo_empleado.
        th1sec = threading.Thread(target=self.tiempo_empleado, args=(1,0,), daemon=True) #1,0 enviando mensaje. (tiempoespera,envio)
        th1sec.start() #Aquí comienza el hilo y comienza a contar 1seg, por el método tiempo_empleado.

            # Color de letra a azul en el chat
        self.txtChat.tag_config('azul', foreground='blue')
        self.inText.delete(0, 'end') #Luego de enviarse el mensaje debe de borrarse en el entry.
        self.txtChat.config(state='disabled') #Deshabilita el chat para evitar escribir.
        return

    #---------METODO DE RECIBIR MENSAJE--------------
    def recibir_mensaje(self):

        if(self.puerto in self.puertos): #Si el COM está dentro de los puertos.

            if self.ser.in_waiting > 0: #Cuando hay un mensaje esperando... (datos esperando)

                mensaje= self.ser.readline() #se lee ese mensaje
                mensaje = mensaje.decode('utf-8') #se decodifica
                self.txtChat.config(state='normal')

                # Threading
                #Se crea un hilo para contar 1seg. Luego de ello se va a cambiar el texto del statusBar.
                th2sec = threading.Thread(target=self.tiempo_empleado, args=(1,1,), daemon=True) #1,1 recibiendo mensaje (tiempoespera,recibiendo)
                th2sec.start()

                #Al recibir mensaje, se tendrá texto de color rojo
                self.insertar_texto(mensaje,'rojo')

                self.txtChat.tag_config('rojo', foreground='red')
                self.txtChat.config(state='disabled')

        self.master.after(1000,self.recibir_mensaje)


    def tiempo_empleado(self,delay,i):
        # El tiempo lo cambias en threading
        if(i==0):
            self.statusBar.config(text="Enviando mensaje... ")
            time.sleep(delay)  # Tiempo de 1s
            self.statusBar.config(text="") #Luego de un 1segundo lo borra

        elif(i==1):
            self.statusBar.config(text="Recibiendo mensaje... ")
            time.sleep(delay)  # Tiempo de 1s
            self.statusBar.config(text="") #Luego de un 1segundo lo borra

        return

    def decodifica(self):
        #Abre ventana nueva
        self.codigo = tk.Toplevel(self.master)

        self.codigo.title("Decodificador")
        self.codigo.geometry("500x500+100+100")
        self.codigo.resizable(0, 0)
        self.codigo.iconbitmap('icon_chat_sha.ico')
        self.codigo.config(bg="#4c4c4c")

        #----------subventana frames----------------------------------
        self.frm11=tk.LabelFrame(self.codigo,text= "Ingreso de KEY",bg="#4c4c4c",fg="#ffffff")
        self.frm22 = tk.LabelFrame(self.codigo,text="Mensaje decodificado",bg="#4c4c4c",fg="#ffffff")
        self.frm33 = tk.LabelFrame(self.codigo, text="Enviar mensaje",bg="#4c4c4c",fg="#ffffff")
        self.frm11.pack(padx=5, pady=5,anchor=tk.W)
        self.frm22.pack(padx=5, pady=5, fill='y', expand=True)
        self.frm33.pack(padx=5, pady=5)

        #-------------------frm subventana1------------------------------------
        #-------------------frame 1-----------------------------------------------
        self.lblText1 = tk.Label(self.frm11, text="Ingrese la key:",bg="#4c4c4c",fg="#ffffff")
        self.inText1 = tk.Entry(self.frm11, width=60)
        self.lblText1.grid(row=0, column=0, padx=5, pady=5)
        self.inText1.grid(row=0, column=1, padx=5, pady=5)

        # ------------------------ FRAME 2 ---------------------------
        self.txtChat1 = ScrolledText(self.frm22, height=20, width=40, wrap=tk.WORD)
        self.txtChat1.grid(row=0, column=0, columnspan=3, padx=5, pady=5)
        #--------------------------FRAME 3-------------------------------------------
        self.lblText2 = tk.Label(self.frm33, text="Texto:",bg="#4c4c4c",fg="#ffffff")
        self.inText2 = tk.Entry(self.frm33, width=45)

        self.inText2.bind("<Return>", self.enviar_mensaje_key) #Tecla ENTER para enviar mensaje
        self.inText2.bind("<Key>", self.actualizandoStatusBar) #detectar caracteres para "Escribiendo mensaje..."

        self.btnSend1 = tk.Button(self.frm33, text="Enviar", width=12,command=lambda: self.enviar_mensaje_key(None),bg="#4c4c4c",fg="#ffffff")


        self.lblText2.grid(row=0, column=0, padx=5, pady=5)
        self.inText2.grid(row=0, column=1, padx=5, pady=5)
        self.btnSend1.grid(row=0, column=2, padx=5, pady=5)

    def enviar_mensaje_key(self,event):
        #agarra la llave que se puso en el entry para decodificar

        self.KEY_DEC=self.inText1.get()
        fernet_dec = Fernet(self.KEY_DEC)
        #agarra  el dato a desencriptar
        mensaje_cifrar=self.inText2.get()
        #proceso de desencriptar
        mensaje_dec = fernet_dec.decrypt(mensaje_cifrar).decode()
        #fecha
        fecha=f"{datetime.strftime(datetime.now(),'%H'+':'+'%M')}"
        hora = int(fecha[:2])
        minutos = int(fecha[-2:])
        if hora>12:
            self.txtChat1.insert(tk.INSERT,str(mensaje_dec)+f"\n {hora-12:02d}:{minutos:02d} p.m.\n")

        else:
            self.txtChat1.insert(tk.INSERT,str(mensaje_dec)+f"\n {hora:02d}:{minutos:02d} a.m.\n")
        self.txtChat.yview(tk.END)
        self.inText2.delete(0, 'end')

    def cambiar_nombre(self):
        self.editar_nombre = tk.Toplevel(self.master)

        self.editar_nombre.title("Serial Chat")
        self.editar_nombre.geometry("+100+100")
        self.editar_nombre.resizable(0, 0)
        self.editar_nombre.iconbitmap('icon_chat_sha.ico')
        self.editar_nombre.config(bg="#4c4c4c")
        #-----------------------------Frame----------------------------------------------------
        self.frm21=tk.LabelFrame(self.editar_nombre,text= "Editar nombre",bg="#4c4c4c",fg="#ffffff")
        self.frm21.pack(padx=5, pady=5,anchor=tk.W)

        #--------------------------info---------------------------------------------
        self.lblTextnombre = tk.Label(self.frm21, text="Ingrese el nuevo nombre:",bg="#4c4c4c",fg="#ffffff")
        self.inTextnombre = tk.Entry(self.frm21, width=30)
        self.lblTextnombre.grid(row=0, column=0, padx=5, pady=5)
        self.inTextnombre.grid(row=0, column=1, padx=5, pady=5)
        self.btnSendnombre = tk.Button(self.frm21, text="Cambiar nombre", width=12,command=lambda: self.usuariocambiado(None),bg="#4c4c4c",fg="#ffffff")
        self.btnSendnombre.grid(row=0, column=2, padx=5, pady=5)
        #----------------------------Editar nombre----------------------------
    def usuariocambiado(self,event):
        self.nombrenuevo=self.inTextnombre.get()
        self.cambionombre=True
        showinfo(title="Notificacion",message=f"Nombre cambiado a {self.inTextnombre.get()}")





root = tk.Tk()
app = SerialChat(root)
root.mainloop()