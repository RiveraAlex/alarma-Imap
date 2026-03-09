import threading
from imap_tools import MailBox,MailMessageFlags
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, 
    QVBoxLayout, QHBoxLayout,QPushButton, 
    QScrollArea,QStackedWidget,QLabel
)
from PySide6.QtCore import Qt, QThread, Signal,QTimer
from PySide6.QtGui import QIcon,QPixmap
from PySide6.QtCore import QSize

import notificationItem
import mailWindow

import os

RUTA_PROYECTO = os.path.dirname(os.path.abspath(__file__))
    
RUTA_REFRESHIMAGE = os.path.join(RUTA_PROYECTO,'images','iconRefreshButton.png')
RUTA_ICON = os.path.join(RUTA_PROYECTO,'images','icon.ico')
content_lock = threading.Lock()
# Función para verificar si se ha recibido un correo

def check_email():
    global content
    MAIL_PASSWORD ="XXXXXX"
    MAIL_USER = "XXXXXXXXX"

    container = []
    with MailBox("mail.XXXXXXXXXX.com.ar").login(MAIL_USER, MAIL_PASSWORD) as mb:
        for msg in mb.fetch(criteria='UNSEEN',mark_seen=False):
            if(msg.from_ == "XXXXXXXXXX"):
                container.append({
                    "subject": msg.subject,
                    "text": msg.text,
                    "uid" : msg.uid,
                    "time": msg.date.strftime("%y/%m/%d %H:%M")
                })
    return container

class Open_window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Alarma")
        self.resize(400, 600)
        app_icon = QIcon(QPixmap(RUTA_ICON))
        self.setWindowIcon(app_icon)

        #Widget principal--------------------------------------------------------------------------
        self.main_widget = QWidget()
        self.layout_Main = QVBoxLayout(self.main_widget)
        self.main_widget.setStyleSheet("background-color: #999999;")

        #Hilo principal--------------------------------------------------------------------------

        self.threadMain = EmailWorker()
        self.threadMain.new_email.connect(self.agregar_Noti)
        self.threadMain.start()

        #Area de scroll----------------------------------------------------------------------------
        """Refresh Button"""
        self.refreshWidget = QWidget()
        self.layoutRefresh = QHBoxLayout(self.refreshWidget)
        self.refreshButton = QPushButton()
        self.iconRefreshButton = QIcon(rf"{RUTA_REFRESHIMAGE}")
        self.refreshButton.setIcon(self.iconRefreshButton)
        self.refreshButton.clicked.connect(self.actionRefresh)
        self.refreshButton.setFixedSize(120, 50)
        self.refreshButton.setIconSize(QSize(64, 64))
        self.layoutRefresh.addWidget(self.refreshButton)
        
        """Cascada de notificaciones"""
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)    
        self.content_widget = QWidget()
        self.scroll.setWidget(self.content_widget)
        self.layout_cascada = QVBoxLayout(self.content_widget)
        self.layout_cascada.setDirection(QVBoxLayout.Direction.BottomToTop)
        self.layout_cascada.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.content_widget.setStyleSheet("background-color: #FFFFFF;")

        #self.layout_Main.addWidget(self.scroll)
            
        #Stack de pantallas-----------------------------------------------------------------------
        self.stack = QStackedWidget()
        self.first_Scroll_Refresh = QWidget()
        self.layoutFirst_Scroll_Refresh = QVBoxLayout(self.first_Scroll_Refresh)
        self.layoutFirst_Scroll_Refresh.addWidget(self.refreshWidget)
        self.layoutFirst_Scroll_Refresh.addWidget(self.scroll)

        self.setCentralWidget(self.stack)

        self.stack.addWidget(self.first_Scroll_Refresh)

        self.pantalladeMail = None

    def agregar_Noti(self, conteiner):
        """
        Esta funcion instancia un objeto de la clase NotificationItem la cual es un widget que funciona como notificacion.
        Esta despues es agregada al layout de cascada
        """
        self.clear_Noti()        
        if not conteiner:
            # Creamos un label estilizado para el estado vacío
            self.label_vacio = QLabel("Sin mensajes nuevos")
            self.label_vacio.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.label_vacio.setStyleSheet("""
                color: #cb3234; 
                font-size: 16px; 
                font-weight: bold;
                margin-top: 50px;
            """)
        # Lo agregamos al layout
            self.layout_cascada.addWidget(self.label_vacio)
        else:
            self.layout_cascada.setEnabled(False)
            for email_data in conteiner:
                newMail = create_Mail(email_data)
                newMail.clicked.connect(self.abrir_detalle)
                self.layout_cascada.addWidget(newMail)
            self.layout_cascada.setEnabled(True)
    
    def clear_Noti(self):
        """
        Borra todas las notificaciones guardadas para hacer una limpieza al recargar con nuevas notificaciones
        """
        while self.layout_cascada.count():
            firtsPos = self.layout_cascada.takeAt(0)
            widgetFirstPos = firtsPos.widget()
            widgetFirstPos.deleteLater()

    def abrir_detalle(self,data):
        """
        Dirige todo el trafico de la main window hacia una pantalla de mail mas completa particular para la que es clickeada
        Tambien permite volver a la pantalla principal de cascada o marcar como visto distintos Mails
        """
        self.vista_Detallada = mailWindow.mailWindow(data)
        if self.stack.count() > 1:
            widget_viejo = self.stack.widget(1)
            self.stack.removeWidget(widget_viejo)
            widget_viejo.deleteLater()
        self.stack.addWidget(self.vista_Detallada)  
        self.stack.setCurrentWidget(self.vista_Detallada) 

        self.vista_Detallada.btn_Visto.clicked.connect(lambda: marcarVisto(data['uid']))

        self.vista_Detallada.btn_Volver.clicked.connect(lambda: self.regresar_y_actualizar())
    
    def actionRefresh (self):
        self.threadMain.request_check.emit()
        #print(RUTA_REFRESHIMAGE)
        
    def regresar_y_actualizar(self):
        self.stack.setCurrentIndex(0)
    
        self.threadMain.ejecutar_chequeo()



def create_Mail(email_data):
    """
    Patron de diseño factory
    """
    mail = notificationItem.NotificationItem({
        "asunto": email_data['subject'],
        "cuerpo": email_data['text'],
        "uid" : email_data['uid'],
        "time": email_data['time']
    })
    return mail

def marcarVisto(uid):
    """
    Funcion global que ejecuta por si mismo la entrada al mail para marcar como visto al mail correspondiente
    """
    MAIL_PASSWORD = "XXXXXXXXXXX"
    MAIL_USER = "XXXXXXXXXXXXXXXX"
    try:
        with MailBox("mail.XXXXXXXXXXXXX.com.ar").login(MAIL_USER, MAIL_PASSWORD) as mb:
            mb.flag(uid, MailMessageFlags.SEEN, True)
    except Exception as e:
        print(f"Error de red al marcar como visto: {e}")

class EmailWorker(QThread): 
    """
    Clase principal del hilo principal
    """
    new_email = Signal(list)
    request_check = Signal()

    def run(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.ejecutar_chequeo)
        self.request_check.connect(self.ejecutar_chequeo)
        self.ejecutar_chequeo()
        self.timer.start(60000)
        self.exec()

    def ejecutar_chequeo(self):
        array = check_email()
        self.new_email.emit(array)



if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    ventana = Open_window()
    ventana.show()
    sys.exit(app.exec())
    