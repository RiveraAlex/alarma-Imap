from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel,QApplication
from PySide6.QtCore import Signal
from datetime import datetime, timezone, timedelta
import winsound

def play_alarm_sound():
    winsound.Beep(1000, 300)

class NotificationItem(QWidget):
    clicked = Signal(dict)
    
    def __init__(self, mail_data):
        super().__init__()

        self.data = mail_data
        layout = QVBoxLayout(self)
        self.label_titulo = QLabel(f"<b>{mail_data['asunto']} {mail_data['time']}</b>")
        self.label_cuerpo = QLabel(mail_data['cuerpo'][:50]+"...")
        layout.addWidget(self.label_titulo)
        layout.addWidget(self.label_cuerpo)
        print(mail_data['time'])
        self.setStyleSheet(self.isNew(mail_data['time']))

    def mousePressEvent(self, event):
        print("Notificación clickeada:")
        self.clicked.emit(self.data) 
    
    def isNew(self,time):
        tz_ar = timezone(timedelta(hours=-3))
        ahora = datetime.now(tz_ar)
        # 2. Calculamos la diferencia   
        fecha_obj = datetime.strptime(time, "%y/%m/%d %H:%M")
        fecha_obj = fecha_obj.replace(tzinfo=tz_ar)

        diferencia = ahora - fecha_obj
        
        # 3. Determinamos el estilo (Umbral: 30 minutos)
        if diferencia.total_seconds() < 300:
            # ESTILO NUEVO: Fondo ámbar suave con borde naranja
            play_alarm_sound()
            QApplication.alert(None,duration=3000)
            return "border: 3px solid #e67e22; border-radius: 10px; background: #fef5e7;"
        else:
            # ESTILO ESTÁNDAR: El que ya tenías definido
            return "border: 2px solid #3498db; border-radius: 10px; background: #FFFFFF;"
