# ChessCV
ChessCV transforms your physical chessboard into a fully functional virtual eBoard using computer vision. By tracking moves via camera, it allows you to play directly against online opponents on Lichess or perform real-time engine analysis using your physical pieces.

## Demo

## Features
As of now, ChessCV has two main features:

1. **Play on Lichess:**
Once enabled in-app, ChessCV will automatically send your moves to lichess' servers provided your laptop has internet connectivity.

2. **Analyse Games:**
Once enabled in-app, you will be able to see a live evaluation-bar of the position on board that works based on the Stockfish Engine v17.1.

## How it Works

## Requirements
- Windows 10 or greater
- Python version 3.10 or greater
- A decent GPU (RTX 3050 recommended)
- A camera (smartphone-camera connection recommended)

## Installation

Clone this repository:
```
git clone https://github.com/ppl-call-me-tima/chess-cv-2.git
cd chess-cv-2
```

Initialize a Python virtual environment:
```
python -m venv .venv
.venv\Scripts\activate
```

If you don't have a CUDA installation, install PyTorch+CUDA or a relevant version: [Get Command for Required Version](https://pytorch.org/get-started/locally/) 
```
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128
```

Install other required dependencies:
```
pip install -r requirements.txt
```

Download the board/pieces models: https://drive.google.com/uc?export=download&id=1TndP5wkQlDqAePJ1gC0dQ9-Us6M3ef_X

Place the downloaded `models` directory after extraction inside the root directory.

Execute the program:
```
python main.py
```
