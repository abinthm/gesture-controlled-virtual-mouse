# Gesture Mouse Control

A computer vision-based application that allows you to control your mouse cursor using hand gestures captured through your webcam.

## Features

- 👆 Control mouse movement using your index finger
- 🖱️ Perform left clicks by pinching index finger and thumb
- 💫 Smooth cursor movement with position averaging
- 📜 Scroll mode for vertical and horizontal scrolling
- ✌️ Mode switching using fist gesture
- ⌨️ Keyboard shortcuts for mode switching
- 🔄 Double-click support

##Requirements

conda create -n gesture-mouse python=3.8
conda activate gesture-mouse
conda install -c conda-forge opencv numpy
pip install mediapipe pyautogui

## Usage

1. Run the script:

2. Position your hand in front of the webcam.

3. Control schemes:
   - Move your index finger to control the cursor
   - Pinch index finger and thumb together for left click
   - Make a fist to switch between move and scroll modes
   - In scroll mode, move your hand up/down to scroll

### Keyboard Controls

- `m` - Switch to move mode
- `s` - Switch to scroll mode
- `ESC` - Exit the application

## Configuration

The following parameters can be adjusted in the code:

- `click_threshold`: Distance threshold for click detection (default: 30)
- `scroll_threshold`: Movement threshold for scroll detection (default: 20)
- `history_length`: Number of positions to average for smooth movement (default: 5)
- `click_cooldown`: Time between clicks (default: 0.3 seconds)
- `double_click_interval`: Time window for double-click detection (default: 0.5 seconds)
- `mode_switch_cooldown`: Time between mode switches (default: 1 second)

## Visual Feedback

The application window shows:
- Live webcam feed with hand landmark overlay
- Current mode (MOVE/SCROLL)
- Click and mode switch indicators
- Hand tracking visualization

## Notes

- The application uses MediaPipe's hand tracking to detect hand landmarks
- Only one hand is tracked at a time
- The webcam view is mirrored for more intuitive control
- Position smoothing is implemented to reduce cursor jitter


## Troubleshooting

1. If the cursor movement is too sensitive:
   - Adjust the interpolation ranges in the mouse movement calculation
   - Increase the `history_length` for more smoothing

2. If click detection is unreliable:
   - Adjust the `click_threshold` value
   - Ensure good lighting conditions

3. If hand detection is poor:
   - Check your webcam's positioning and lighting
   - Adjust the `min_detection_confidence` in the MediaPipe Hands initialization

