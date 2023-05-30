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
elevation = 30
azimuth = 45

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
        print(f"pos1 = [{pos[0]}, {pos[1]}, {pos[2]}]")
        pos2 = w.cameraPosition()
        print(f"pos2 = [{pos2[0]}, {pos2[1]}, {pos2[2]}]")
        w.setCameraPosition(pos=pos)
        pos3 = convert_pos1_to_pos2(pos)
        print(f"pos3 = [{pos3[0]}, {pos3[1]}, {pos3[2]}]")

    if event.buttons() == QtCore.Qt.LeftButton:
        dx = event.pos().x() - last_pos.x()
        dy = event.pos().y() - last_pos.y()

        azimuth += dx * sensitivity
        elevation += dy * sensitivity
        w.setCameraPosition(elevation=elevation, azimuth=azimuth)


    update_values()

    last_pos = event.pos()

def convert_pos1_to_pos2(pos1):
    # Get the camera's transformation matrix
    tr = w.cameraTransform()

    # Convert pos1 to a QVector3D object
    pos1_qvector = QtGui.QVector3D(*pos1)

    # Apply the transformation matrix to pos1
    pos2_qvector = tr.map(pos1_qvector)

    # Convert the result back to a list
    pos2 = [pos2_qvector.x(), pos2_qvector.y(), pos2_qvector.z()]

    return pos2
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

def myKeyPressEvent(event):
    oldKeyPressEvent(event)

    global distance, pos, azimuth, elevation

    # Distance step for movement
    distance_step = 0.2

    # Angle step for rotation
    angle_step = 1

    # Check the key that was pressed
    key = event.key()
    if key == QtCore.Qt.Key_W:
        # Move forward
        # print(f"pos2 = [{pos[0]}, {pos[1]}, {pos[2]}]")
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

    elif key == QtCore.Qt.Key_C:
        # Move down
        distance -= distance_step
        pos.setZ(distance)
        # Update the camera position
        w.setCameraPosition(distance=distance)

    elif key == QtCore.Qt.Key_Left:
        # Rotate left
        azimuth -= angle_step
        azimuth %= 360
        # Update the camera position


    elif key == QtCore.Qt.Key_Right:
        # Rotate right
        azimuth += angle_step
        azimuth %= 360
        # Update the camera position


    elif key == QtCore.Qt.Key_Up:
        # Rotate up
        elevation += angle_step
        elevation = min(elevation, 90)
        # Update the camera position


    elif key == QtCore.Qt.Key_Down:
        # Rotate down
        elevation -= angle_step
        elevation = max(elevation, -90)
        # Update the camera position

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


