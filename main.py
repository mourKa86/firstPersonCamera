import pyqtgraph.opengl as gl
import pyqtgraph as pg
import numpy as np
from PyQt5 import Qt, QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QApplication
import sys

# Generate random point cloud
num_points = 1000
positions = np.random.normal(size=(num_points, 3))


# Create the application
app = QApplication([])
w = gl.GLViewWidget()

# Add points to the GLViewWidget
points = gl.GLScatterPlotItem(pos=positions)
w.addItem(points)

# Set initial camera parameters
pos = w.cameraPosition()
pos.setX(0)
pos.setY(0)
pos.setZ(0)
distance = 10
elevation = 0
azimuth = 0

# Set camera parameters
w.setCameraPosition(distance=distance, elevation=elevation, azimuth=azimuth)

# Global variables to track mouse movement
last_pos = None
oldMouseMoveEvent = w.mouseMoveEvent
oldMousePressEvent = w.mousePressEvent
oldMouseReleaseEvent = w.mouseReleaseEvent
oldMouseWheelEvent = w.wheelEvent
oldKeyPressEvent = w.keyPressEvent

# Define mouse event handlers
def myMousePressEvent(event):
    oldMousePressEvent(event)
    global last_pos
    last_pos = event.pos()

def myMouseReleaseEvent(event):
    oldMouseReleaseEvent(event)
    global  last_pos
    last_pos = None

def myMouseMoveEvent(event):
    oldMouseMoveEvent(event)
    global last_pos, pos, distance, elevation, azimuth

    if last_pos is None:
        last_pos = event.pos()
        return

    sensitivity = 0.2

    if event.buttons() == QtCore.Qt.MiddleButton:
        dx = event.pos().x() - last_pos.x()
        dy = event.pos().y() - last_pos.y()
        pos.setX(pos.x() - dx * sensitivity)
        pos.setY(pos.y() + dy * sensitivity)

    if event.buttons() == QtCore.Qt.LeftButton:
        dx = event.pos().x() - last_pos.x()
        dy = event.pos().y() - last_pos.y()

        azimuth += dx * sensitivity
        elevation += dy * sensitivity
        w.setCameraPosition(elevation=elevation, azimuth=azimuth)

    update_values()

    last_pos = event.pos()

def myWheelEvent(event):
    oldMouseWheelEvent(event)
    global pos, distance

    # Get the distance change
    delta = event.angleDelta().y() / 120

    # Update the distance
    if distance > 0:
        distance -= delta
    else:
        distance = max(delta, 0.01)

    pos.setZ(distance)

    w.setCameraPosition(distance=distance)
    update_values()


def calculate_absolute_pos(relative_pos, azimuth, elevation):
    # Calculate the rotation matrix
    rotation_matrix = np.array([
        [np.cos(np.radians(azimuth)), -np.sin(np.radians(azimuth)), 0],
        [np.sin(np.radians(azimuth)), np.cos(np.radians(azimuth)), 0],
        [0, 0, 1]
    ])

    # Calculate the translation vector
    translation_vector = np.array([
        0.1 * np.cos(np.radians(elevation)) * np.cos(np.radians(azimuth)),
        0.1 * np.cos(np.radians(elevation)) * np.sin(np.radians(azimuth)),
        0.1 * np.sin(np.radians(elevation))
    ])

    # Calculate the absolute position
    absolute_pos = np.dot(rotation_matrix, relative_pos) + translation_vector

    return absolute_pos

def myKeyPressEvent(event):
    oldKeyPressEvent(event)

    global distance, pos, azimuth, elevation

    # Distance step for movement
    distance_step = 0.2


    # Check the key that was pressed
    key = event.key()
    if key == QtCore.Qt.Key_W:
        # Move forward
        pos.setX(pos.x() - distance_step * np.cos(np.radians(azimuth)))
        pos.setY(pos.y() - distance_step * np.sin(np.radians(azimuth)))
        w.setCameraPosition(pos=pos)


    elif key == QtCore.Qt.Key_S:
        # Move backward
        pos.setX(pos.x() + distance_step * np.cos(np.radians(azimuth)))
        pos.setY(pos.y() + distance_step * np.sin(np.radians(azimuth)))
        w.setCameraPosition(pos=pos)

    elif key == QtCore.Qt.Key_A:
        # Move left
        pos.setX(pos.x() + distance_step * np.sin(np.radians(azimuth)))
        pos.setY(pos.y() - distance_step * np.cos(np.radians(azimuth)))
        w.setCameraPosition(pos=pos)

    elif key == QtCore.Qt.Key_D:
        # Move right
        pos.setX(pos.x() - distance_step * np.sin(np.radians(azimuth)))
        pos.setY(pos.y() + distance_step * np.cos(np.radians(azimuth)))
        w.setCameraPosition(pos=pos)

    elif key == QtCore.Qt.Key_Space:
        # Move up
        distance += distance_step
        pos.setZ(distance)
        w.setCameraPosition(pos=pos)

    elif key == QtCore.Qt.Key_C:
        # Move down
        distance -= distance_step
        pos.setZ(distance)
        w.setCameraPosition(pos=pos)

    elif key == QtCore.Qt.Key_Left:
        # Rotate left
        azimuth = w.cameraParams()['azimuth']

    elif key == QtCore.Qt.Key_Right:
        # Rotate right
        azimuth = w.cameraParams()['azimuth']

    elif key == QtCore.Qt.Key_Up:
        # Rotate up
        elevation = w.cameraParams()['elevation']

    elif key == QtCore.Qt.Key_Down:
        # Rotate down
        elevation = w.cameraParams()['elevation']


    # Update displayed values
    update_values()

# connect mouse event handles
w.mouseMoveEvent = myMouseMoveEvent
w.mousePressEvent = myMousePressEvent
w.mouseReleaseEvent = myMouseReleaseEvent
w.wheelEvent = myWheelEvent
w.keyPressEvent = myKeyPressEvent

# create a label to display the values
label = QtWidgets.QLabel()
label.setAlignment(QtCore.Qt.AlignBottom)
label.setStyleSheet("QLabel { font-weight: bold; font-size: 16px; }")

# create a vertical layout for the label
layout = QtWidgets.QVBoxLayout()
layout.addWidget(w)
layout.addWidget(label)
layout.setStretchFactor(w,1)

# create a widget and set the layout
widget = QtWidgets.QWidget()
widget.setLayout(layout)
widget.resize(800, 600)

def update_label():
    label.setText(f"Camera Position: [{pos.x():.2f}, {pos.y():.2f}, {pos.z():.2f}]\n "
                  f"Distance: {distance:.2f}, Elevation: {elevation:.2f}, Azimuth: {azimuth:.2f}")

update_label()

def update_values():
    update_label()

# show the widget
widget.show()

# Run the application
if __name__ == '__main__':
    if sys.flags.interactive != 1 or not hasattr(pg.QtCore, 'PYQT_VERSION'):
        QApplication.instance().exec_()


