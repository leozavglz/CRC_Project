import socket
import binascii
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle

def calculate_crc(message):
    """
    Calcula el valor CRC del mensaje dado.
    Args:
    - message (str): El mensaje a calcular el CRC.
    
    Returns:
    - int: El valor CRC del mensaje.
    """
    crc = binascii.crc32(message.encode('utf-8'))
    return crc

class ClientApp(App):
    def build(self):
        # Establecer el color de fondo de la ventana
        Window.clearcolor = (0.95, 0.95, 0.95, 1)

        # Layout principal
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Encabezado
        header = BoxLayout(size_hint_y=None, height=60, padding=10, spacing=10)
        with header.canvas.before:
            Color(0.2, 0.6, 0.86, 1)  # Azul
            self.rect = Rectangle(size=header.size, pos=header.pos)
            header.bind(size=self._update_rect, pos=self._update_rect)
        header.add_widget(Image(source=r'C:/Users/leoza/OneDrive/Documentos/me.png', size_hint_x=None, width=40))
        header.add_widget(Label(text='Chat Cliente', font_size=24, color=[1, 1, 1, 1]))
        self.layout.add_widget(header)
        
        # ScrollView para mostrar la respuesta
        self.scroll_view = ScrollView(size_hint=(1, 1))
        self.response_label = Label(size_hint_y=None, text='', markup=True, valign='top', halign='left', color=[0, 0, 0, 1])
        self.response_label.bind(texture_size=self._update_label_height)
        self.scroll_view.add_widget(self.response_label)
        self.layout.add_widget(self.scroll_view)
        
        # Input de mensaje
        self.message_input = TextInput(hint_text='Ingrese el mensaje', multiline=False, size_hint_y=None, height=40, background_color=[1, 1, 1, 1], foreground_color=[0, 0, 0, 1])
        self.layout.add_widget(self.message_input)
        
        # Input de porcentaje de error
        self.error_input = TextInput(hint_text='Ingrese el porcentaje de error', multiline=False, input_filter='int', size_hint_y=None, height=40, background_color=[1, 1, 1, 1], foreground_color=[0, 0, 0, 1])
        self.layout.add_widget(self.error_input)
        
        # Botón de enviar
        self.send_button = Button(text='Enviar', size_hint_y=None, height=50)
        with self.send_button.canvas.before:
            self.button_color = Color(0.5, 0.5, 0.5, 1)  # Gris inicial
            self.button_rect = Rectangle(size=self.send_button.size, pos=self.send_button.pos)
            self.send_button.bind(size=self._update_button_rect, pos=self._update_button_rect)
        self.send_button.color = [1, 1, 1, 1]  # Texto blanco
        self.send_button.bind(on_press=self.send_message)
        self.layout.add_widget(self.send_button)
        
        # Conectar al servidor al iniciar la aplicación
        self.host = 'localhost'
        self.port = 12345
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((self.host, self.port))
            self.response_label.text += "[b]Conectado al servidor[/b]\n"
            self.button_color.rgb = (0, 1, 0)  # Verde si la conexión es exitosa
        except ConnectionRefusedError:
            self.response_label.text += "[b]Error:[/b] No se pudo conectar al servidor\n"
            self.send_button.disabled = True
        
        return self.layout
    
    def _update_rect(self, instance, value):
        """
        Actualiza la posición y tamaño del rectángulo de fondo del encabezado.
        """
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def _update_button_rect(self, instance, value):
        """
        Actualiza la posición y tamaño del rectángulo de fondo del botón.
        """
        self.button_rect.pos = instance.pos
        self.button_rect.size = instance.size

    def _update_label_height(self, instance, value):
        """
        Ajusta la altura del Label dentro del ScrollView según el tamaño de su contenido.
        """
        instance.height = instance.texture_size[1]
        instance.text_size = (self.scroll_view.width, None)

    def send_message(self, instance):
        """
        Envía el mensaje al servidor y maneja la respuesta.
        """
        if self.send_button.disabled:
            return

        message = self.message_input.text
        error_percentage = self.error_input.text
        
        if message.lower() == "terminar":
            self.response_label.text += "\n[b]Conexión terminada[/b]"
            self.client_socket.sendall(message.encode('utf-8'))
            self.client_socket.close()
            self.send_button.disabled = True
            return
        
        if not error_percentage.isdigit() or int(error_percentage) > 100:
            self.response_label.text += "\n[b]Porcentaje de error debe ser un número entre 0 y 100[/b]"
            return
        
        error_percentage = int(error_percentage)
        
        try:
            # Calcular el CRC del mensaje
            crc_value = calculate_crc(message)
            # Adjuntar el CRC al mensaje
            message_with_crc = f"{message}:{crc_value}"
            data = f"{message_with_crc}|{error_percentage}"
            self.client_socket.sendall(data.encode('utf-8'))
            response = self.client_socket.recv(1024).decode('utf-8')
            self.response_label.text += f"\n[b]Mensaje enviado:[/b] {message}\n[b]Respuesta recibida:[/b] {response}"
            self.scroll_view.scroll_y = 0
        except (socket.timeout, ConnectionRefusedError, BrokenPipeError):
            self.response_label.text += "\n[b]Error:[/b] No se pudo enviar el mensaje. Conexión perdida.\n"
            self.send_button.disabled = True
            self.button_color.rgb = (0.5, 0.5, 0.5)  # Cambia a gris si la conexión se pierde

if __name__ == '__main__':
    ClientApp().run()
