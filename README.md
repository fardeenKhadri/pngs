# Astral Watermarker (Invisible Signal Embedding)

![Status](https://img.shields.io/badge/Status-Prototype-blue) ![Python](https://img.shields.io/badge/Python-3.11+-yellow) ![Flask](https://img.shields.io/badge/Backend-Flask-green)

A robust, invisible watermarking application designed to embed imperceptible signals (SynthID-like) directly into the frequency domain of images. This tool allows creators to protect their content by verifying its origin through a hidden digital signature.

##  Features

*   **Invisible Embedding**: Uses Discrete Wavelet Transform (DWT) to modify image frequencies without affecting visual quality.
*   **Secure Decoding**: reliably extracts the hidden 4-character ID from watermarked images.
*   **Premium Web Interface**: A modern, glassmorphism-styled drag-and-drop UI for easy interaction.
*   **Real-time Processing**: Fast embedding and detection powered by a local Flask server.
*   **Lightweight Core**: Built with `OpenCV` and `PyWavelets`, removing heavy dependencies like PyTorch for this version.

##  Tech Stack

*   **Backend**: Flask (Python)
*   **Processing**: OpenCV, NumPy, PyWavelets
*   **Frontend**: HTML5, CSS3 (Glassmorphism design)
*   **Package Management**: `uv` (Astral)

##  Getting Started

### Prerequisites

*   Python 3.11+
*   [`uv`](https://github.com/astral-sh/uv) (Recommended) or `pip`

### Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/fardeenKhadri/pngs.git
    cd pngs
    ```

2.  **Install Dependencies**
    Using `uv`:
    ```bash
    uv sync
    ```
    Or using standard `pip`:
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: You may need to generate requirements.txt first if not present: `uv pip compile pyproject.toml -o requirements.txt`)*

### Running the App

Start the local server:

```powershell
uv run app.py
```

Open your browser and navigate to:
**http://127.0.0.1:5000**

## 📖 Usage Guide

### Embedding a Watermark
1.  Navigate to the **Embed** tab.
2.  Drag and drop your target image.
3.  Enter a secret 4-character ID (e.g., `TEST`, `USER`).
4.  Click **Embed Signal**.
5.  Preview the result and confirm visually that no artifacts are seen.
6.  Click **Download Image** to save the protected file.

### Decoding a Signal
1.  Navigate to the **Decode** tab.
2.  Upload a watermarked image.
3.  Click **Decode Signal**.
4.  The system will extract and display the hidden ID.

## 🔮 Roadmap

*   [x] **Phase 1**: Core DWT Algorithm & Web UI (Completed)
*   [ ] **Phase 2**: Robustness Testing (JPEG survival, Cropping resistance)
*   [ ] **Phase 3**: Integration of Deep Learning models (RivaGAN) for "SynthID-level" resilience.
*   [ ] **Phase 4**: API deployment ready.

##  License

This project is open-source and available under the standard MIT License.
