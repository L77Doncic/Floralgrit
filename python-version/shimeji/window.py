"""
Mascot Window - Transparent, borderless, always-on-top window for the mascot
"""

from PyQt6.QtWidgets import QMainWindow, QWidget, QApplication, QMenu
from PyQt6.QtCore import Qt, QPoint, QTimer, pyqtSignal
from PyQt6.QtGui import QPainter, QPixmap, QImage, QAction
from PIL import Image
import os


class MascotWindow(QMainWindow):
    """Main window for displaying the mascot"""
    
    # Signals
    mouse_pressed = pyqtSignal(QPoint)
    mouse_moved = pyqtSignal(QPoint)
    mouse_released = pyqtSignal()
    
    def __init__(self, img_dir: str = '../img'):
        super().__init__()
        
        self.img_dir = img_dir
        self.current_pixmap: QPixmap = None
        self.drag_position: QPoint = None
        self.is_dragging = False
        
        # Window settings
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowTransparentForInput if False else Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        
        # Size will be set based on image
        self.resize(128, 128)
        
        # Enable mouse tracking
        self.setMouseTracking(True)
        
    def set_image(self, image_path: str):
        """Set the current image to display"""
        full_path = os.path.join(self.img_dir, image_path.lstrip('/'))
        
        if not os.path.exists(full_path):
            print(f"Image not found: {full_path}")
            return
            
        # Load with PIL and convert to QPixmap
        pil_image = Image.open(full_path)
        
        # Convert to RGBA if necessary
        if pil_image.mode != 'RGBA':
            pil_image = pil_image.convert('RGBA')
            
        # Convert to QImage
        data = pil_image.tobytes("raw", "RGBA")
        qimage = QImage(data, pil_image.width, pil_image.height, QImage.Format.Format_RGBA8888)
        
        self.current_pixmap = QPixmap.fromImage(qimage)
        self.resize(self.current_pixmap.size())
        self.update()
        
    def paintEvent(self, event):
        """Paint the current frame"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        if self.current_pixmap:
            painter.drawPixmap(0, 0, self.current_pixmap)
            
    def mousePressEvent(self, event):
        """Handle mouse press for dragging"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.is_dragging = True
            self.mouse_pressed.emit(event.pos())
            event.accept()
        elif event.button() == Qt.MouseButton.RightButton:
            self.show_context_menu(event.globalPosition().toPoint())
            
    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging"""
        if self.is_dragging and event.buttons() == Qt.MouseButton.LeftButton:
            new_pos = event.globalPosition().toPoint() - self.drag_position
            self.move(new_pos)
            self.mouse_moved.emit(event.pos())
            event.accept()
            
    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False
            self.mouse_released.emit()
            event.accept()
            
    def show_context_menu(self, pos):
        """Show right-click context menu"""
        menu = QMenu(self)
        
        add_action = QAction("Add Another", self)
        add_action.triggered.connect(self.on_add_another)
        menu.addAction(add_action)
        
        close_action = QAction("Close", self)
        close_action.triggered.connect(self.close)
        menu.addAction(close_action)
        
        exit_action = QAction("Exit All", self)
        exit_action.triggered.connect(self.on_exit_all)
        menu.addAction(exit_action)
        
        menu.exec(pos)
        
    def on_add_another(self):
        """Signal to add another mascot instance"""
        pass  # Will be connected to mascot manager
        
    def on_exit_all(self):
        """Exit the application"""
        QApplication.quit()
        
    def get_position(self) -> QPoint:
        """Get current window position (anchor point)"""
        return self.pos()
        
    def set_position(self, x: int, y: int):
        """Set window position"""
        self.move(x, y)
        
    def get_anchor(self) -> QPoint:
        """Get anchor point (bottom center of image)"""
        return QPoint(self.x() + self.width() // 2, self.y() + self.height())
