"""
Demo script para controlar tira LED WS2812 via Art-Net
Muestra diferentes efectos y capacidades del sistema
"""

import time
import socket
import struct
import math

class ArtNetController:
    def __init__(self, target_ip='192.168.1.100', universe=0):
        self.target_ip = target_ip
        self.universe = universe
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sequence = 0
        
    def send_dmx(self, dmx_data, universe=None):
        """Envía un paquete Art-Net DMX"""
        if universe is None:
            universe = self.universe
            
        # Art-Net header
        packet = bytearray()
        packet.extend(b'Art-Net\x00')  # ID
        packet.extend(struct.pack('<H', 0x5000))  # OpCode (DMX)
        packet.extend(struct.pack('>H', 14))  # Protocol version
        packet.append(self.sequence)  # Sequence
        packet.append(0)  # Physical
        packet.extend(struct.pack('<H', universe))  # Universe
        packet.extend(struct.pack('>H', len(dmx_data)))  # Length
        packet.extend(dmx_data)  # DMX data
        
        self.sock.sendto(packet, (self.target_ip, 6454))
        self.sequence = (self.sequence + 1) % 256
        
    def set_brightness(self, brightness):
        """Establece el brillo global (universo 15)"""
        dmx_data = bytearray([brightness])
        self.send_dmx(dmx_data, universe=15)
        
    def set_led(self, led_index, r, g, b, dmx_data):
        """Establece el color de un LED específico en el buffer DMX"""
        start = led_index * 3
        dmx_data[start] = r
        dmx_data[start + 1] = g
        dmx_data[start + 2] = b

class LEDDemo:
    def __init__(self, controller, num_leds=30):
        self.controller = controller
        self.num_leds = num_leds
        self.dmx_data = bytearray(num_leds * 3)
        
    def clear(self):
        """Apaga todos los LEDs"""
        self.dmx_data = bytearray(self.num_leds * 3)
        self.controller.send_dmx(self.dmx_data)
        
    def solid_color(self, r, g, b, duration=2):
        """Muestra un color sólido"""
        print(f" Color sólido: RGB({r}, {g}, {b})")
        for i in range(self.num_leds):
            self.controller.set_led(i, r, g, b, self.dmx_data)
        self.controller.send_dmx(self.dmx_data)
        time.sleep(duration)
        
    def rainbow_static(self, duration=3):
        """Arcoíris estático"""
        print(" Arcoíris estático")
        for i in range(self.num_leds):
            hue = int((i / self.num_leds) * 255)
            r, g, b = self.hsv_to_rgb(hue, 255, 255)
            self.controller.set_led(i, r, g, b, self.dmx_data)
        self.controller.send_dmx(self.dmx_data)
        time.sleep(duration)
        
    def rainbow_cycle(self, cycles=3, speed=0.05):
        """Arcoíris que se mueve"""
        print(" Arcoíris en movimiento")
        for cycle in range(int(cycles * 255)):
            for i in range(self.num_leds):
                hue = int((i / self.num_leds * 255 + cycle) % 255)
                r, g, b = self.hsv_to_rgb(hue, 255, 255)
                self.controller.set_led(i, r, g, b, self.dmx_data)
            self.controller.send_dmx(self.dmx_data)
            time.sleep(speed)
            
    def theater_chase(self, r, g, b, cycles=10, speed=0.1):
        """Efecto de luces de teatro"""
        print(f" Theater chase: RGB({r}, {g}, {b})")
        for cycle in range(cycles):
            for offset in range(3):
                self.clear()
                for i in range(offset, self.num_leds, 3):
                    self.controller.set_led(i, r, g, b, self.dmx_data)
                self.controller.send_dmx(self.dmx_data)
                time.sleep(speed)
                
    def breathing(self, r, g, b, cycles=2, speed=0.02):
        """Efecto de respiración"""
        print(f"💨 Breathing: RGB({r}, {g}, {b})")
        for cycle in range(cycles):
            # Fade in
            for brightness in range(0, 256, 5):
                for i in range(self.num_leds):
                    scaled_r = int(r * brightness / 255)
                    scaled_g = int(g * brightness / 255)
                    scaled_b = int(b * brightness / 255)
                    self.controller.set_led(i, scaled_r, scaled_g, scaled_b, self.dmx_data)
                self.controller.send_dmx(self.dmx_data)
                time.sleep(speed)
            # Fade out
            for brightness in range(255, -1, -5):
                for i in range(self.num_leds):
                    scaled_r = int(r * brightness / 255)
                    scaled_g = int(g * brightness / 255)
                    scaled_b = int(b * brightness / 255)
                    self.controller.set_led(i, scaled_r, scaled_g, scaled_b, self.dmx_data)
                self.controller.send_dmx(self.dmx_data)
                time.sleep(speed)
                
    def brightness_demo(self, r, g, b):
        """Demuestra control de brillo global"""
        print(" Demo de brillo global")
        for i in range(self.num_leds):
            self.controller.set_led(i, r, g, b, self.dmx_data)
        
        # Brillo máximo
        print("   → Brillo 100%")
        self.controller.set_brightness(255)
        self.controller.send_dmx(self.dmx_data)
        time.sleep(1)
        
        # Brillo medio
        print("   → Brillo 50%")
        self.controller.set_brightness(128)
        time.sleep(1)
        
        # Brillo bajo
        print("   → Brillo 25%")
        self.controller.set_brightness(64)
        time.sleep(1)
        
        # Restaurar
        print("   → Brillo 100%")
        self.controller.set_brightness(255)
        time.sleep(1)
        
    def fire_effect(self, duration=5, speed=0.05):
        """Efecto de fuego"""
        print(" Efecto de fuego")
        import random
        end_time = time.time() + duration
        while time.time() < end_time:
            for i in range(self.num_leds):
                r = random.randint(180, 255)
                g = random.randint(0, int(r * 0.4))
                b = 0
                self.controller.set_led(i, r, g, b, self.dmx_data)
            self.controller.send_dmx(self.dmx_data)
            time.sleep(speed)
            
    def wave_effect(self, cycles=2, speed=0.03):
        """Onda de color"""
        print(" Efecto de onda")
        for cycle in range(int(cycles * self.num_leds)):
            for i in range(self.num_leds):
                brightness = int((math.sin((i + cycle) * 0.2) + 1) * 127)
                self.controller.set_led(i, 0, brightness, 255 - brightness, self.dmx_data)
            self.controller.send_dmx(self.dmx_data)
            time.sleep(speed)
    
    @staticmethod
    def hsv_to_rgb(h, s, v):
        """Convierte HSV a RGB"""
        if s == 0:
            return v, v, v
        
        h = h / 255.0 * 6.0
        s = s / 255.0
        v = v / 255.0
        
        i = int(h)
        f = h - i
        p = v * (1.0 - s)
        q = v * (1.0 - s * f)
        t = v * (1.0 - s * (1.0 - f))
        
        i = i % 6
        if i == 0:
            r, g, b = v, t, p
        elif i == 1:
            r, g, b = q, v, p
        elif i == 2:
            r, g, b = p, v, t
        elif i == 3:
            r, g, b = p, q, v
        elif i == 4:
            r, g, b = t, p, v
        else:
            r, g, b = v, p, q
            
        return int(r * 255), int(g * 255), int(b * 255)

def main():
    print("=" * 60)
    print(" DEMO DE CONTROL LED WS2812 VÍA ART-NET ")
    print("=" * 60)
    print()
    
    # Configuración
    ESP_IP = input("IP del ESP8266 (default: 192.168.1.100): ").strip()
    if not ESP_IP:
        ESP_IP = "192.168.1.100"
    
    NUM_LEDS = input("Número de LEDs (default: 30): ").strip()
    NUM_LEDS = int(NUM_LEDS) if NUM_LEDS else 30
    
    print(f"\n Conectando a {ESP_IP} con {NUM_LEDS} LEDs...")
    print()
    
    # Crear controlador y demo
    controller = ArtNetController(ESP_IP)
    demo = LEDDemo(controller, NUM_LEDS)
    
    try:
        # Secuencia de demostración
        demo.clear()
        time.sleep(0.5)
        
        print("\n--- COLORES BÁSICOS ---\n")
        demo.solid_color(255, 0, 0, 1.5)    # Rojo
        demo.solid_color(0, 255, 0, 1.5)    # Verde
        demo.solid_color(0, 0, 255, 1.5)    # Azul
        demo.solid_color(255, 255, 255, 1.5)  # Blanco
        
        print("\n--- EFECTOS ARCOÍRIS ---\n")
        demo.rainbow_static(2)
        demo.rainbow_cycle(cycles=2, speed=0.03)
        
        print("\n--- EFECTOS DINÁMICOS ---\n")
        demo.theater_chase(255, 0, 0, cycles=8, speed=0.08)
        demo.wave_effect(cycles=2)
        demo.breathing(0, 100, 255, cycles=2)
        
        print("\n--- EFECTOS ESPECIALES ---\n")
        demo.fire_effect(duration=4)
        
        print("\n--- CONTROL DE BRILLO ---\n")
        demo.brightness_demo(255, 100, 0)
        
        print("\n--- FINAL ---\n")
        demo.rainbow_cycle(cycles=1, speed=0.02)
        demo.clear()
        
        print("\n Demo completada exitosamente!")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n  Demo interrumpida por el usuario")
        demo.clear()
    except Exception as e:
        print(f"\n Error: {e}")
        demo.clear()

if __name__ == "__main__":
    main()
