from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel,QPushButton,QHBoxLayout
from PySide6.QtCore import Signal

class mailWindow(QWidget):
    def __init__(self, mail_data):
        super().__init__()

        self.data = mail_data
        layoutPrincipal = QVBoxLayout(self)
        layoutPrincipal.setContentsMargins(10, 10, 10, 10)
        self.labelMail = QLabel(f"""
            <h1 style='color: #3498db;'>{mail_data['asunto']}</h1>
            <hr>
            <div style='font-size: 14px;'>{mail_data['cuerpo']}</div>
            """
        )
        self.labelMail.setWordWrap(True)
        self.setFixedWidth(400)
        #Buttons
        self.btn_Volver = QPushButton("<")
        self.btn_Volver.setFixedWidth(50)
        self.btn_Volver.setStyleSheet("""
            QPushButton {
                background-color: #3498db; 
                color: white; 
                border-radius: 5px;
            }
        """
        )
        
        self.btn_Visto = QPushButton("Marcar como visto")
        self.btn_Visto.setStyleSheet("""
            QPushButton {
                background-color: #3498db; 
                color: white; 
                border-radius: 5px;
            }
        """
        )
        

        self.btn_Volver.clicked.connect(self.volver_atras)
        self.btn_Visto.clicked.connect(self.marcar_visto)


        layoutHeader = QHBoxLayout() 
        layoutHeader.addWidget(self.btn_Volver)
        layoutHeader.addStretch()
        layoutMailVisto = QVBoxLayout()
        layoutMailVisto.addWidget(self.labelMail,1)
        layoutMailVisto.addWidget(self.btn_Visto,0)

        layoutPrincipal.addLayout(layoutHeader)
        layoutPrincipal.addLayout(layoutMailVisto)
        
    
    def volver_atras(self):
        print("Regresando a la lista...")

    

    def marcar_visto(self):
        print(f"Protocolo {self.data['asunto']} marcado como visto.")
