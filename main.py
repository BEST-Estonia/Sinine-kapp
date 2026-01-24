from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivy.uix.camera import Camera
from kivy.core.window import Window
import sys

# Set the window to full screen for kiosk mode
Window.fullscreen = 'auto'

class SinineKapp(MDApp):
    def build(self):
        # Set the color theme to Blue (matches "Sinine Kapp")
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"

        # Create the main layout (Vertical box)
        layout = MDBoxLayout(orientation='vertical', padding=20, spacing=20)

        # 1. Header Text
        header = MDLabel(
            text="Sinine Kapp",
            halign="center",
            theme_text_color="Primary",
            font_style="H3"  # Large modern font
        )

        # 2. The Camera View
        # play=True turns it on immediately
        # resolution=(640, 480) is standard for Pi cameras to ensure speed
        self.camera = Camera(play=True, resolution=(640, 480))

        # 3. The Close Button
        close_button = MDRaisedButton(
            text="SULGE PROGRAMM",
            size_hint=(1, 0.1), # Width fills screen, height is 10%
            font_size=24,
            md_bg_color=(1, 0, 0, 1) # Red color for "Close"
        )
        # Link the button press to the close function
        close_button.bind(on_release=self.close_app)

        # Add all items to the layout
        layout.add_widget(header)
        layout.add_widget(self.camera)
        layout.add_widget(close_button)

        return layout

    def close_app(self, instance):
        # Stop the app and close the window
        sys.exit()

if __name__ == '__main__':
    SinineKapp().run()
