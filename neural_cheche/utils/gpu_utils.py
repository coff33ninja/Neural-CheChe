"""
gpu_utils.py

Universal GPU detection and configuration for Python 3.11 and PyTorch.
Supports: NVIDIA (CUDA), AMD (ROCm), Apple Silicon (MPS), Intel/AMD/others (DirectML, OpenCL), CPU fallback.
"""


import torch
import warnings
try:
    import torch_directml
except ImportError:
    torch_directml = None

def safe_device():
    """
    Returns a torch.device that is guaranteed to work (falls back to CPU if the selected device is unavailable).
    Use this everywhere instead of direct device access for robust fallback.
    """
    device, backend = detect_gpu_backend()
    # Try to allocate a tensor on the device to check if it works
    try:
        if backend in ("cuda", "mps"):
            test_tensor = torch.zeros(1).to(device)
            del test_tensor  # Clean up immediately
            if backend == "cuda":
                torch.cuda.empty_cache()  # Clear GPU cache
        elif backend == "directml" and torch_directml is not None:
            test_tensor = torch.zeros(1, device=device)
            del test_tensor
    except Exception as e:
        print(f"[safe_device] {backend} unavailable ({e}), falling back to CPU.")
        return torch.device("cpu")
    return device

def detect_gpu_backend():
    """Detects the best available GPU backend and returns a torch.device and backend name."""
    # CUDA (NVIDIA)
    if hasattr(torch, "cuda") and torch.cuda.is_available():
        return torch.device("cuda"), "cuda"
    # ROCm (AMD) - No public API for detection in mainline PyTorch.
    # If you are using ROCm, install the ROCm build of PyTorch and set device manually.
    # See: https://pytorch.org/get-started/locally/ for ROCm install instructions.
    # Apple Silicon (MPS)
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return torch.device("mps"), "mps"
    # DirectML (Windows, Intel/AMD/NVIDIA)
    if torch_directml is not None:
        dml_device = torch_directml.device()
        return dml_device, "directml"
    # OpenCL (via pyopencl, not natively supported by torch)
    try:
        import pyopencl
        platforms = pyopencl.get_platforms()
        if platforms:
            return None, "opencl"
    except ImportError:
        pass
    # CPU fallback
    return torch.device("cpu"), "cpu"
def recommend_torch_install(backend):
    """Returns a pip install command for the correct torch version for the detected backend."""
    if backend == "cuda":
        return "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121"
    if backend == "rocm":
        return "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm5.7"
    if backend == "mps":
        return "pip install torch torchvision torchaudio"
    if backend == "directml":
        return "pip install torch-directml"
    if backend == "opencl":
        return "pip install pyopencl"
    return "pip install torch torchvision torchaudio"

def get_gpu_info():
    """Returns a string describing the detected GPU or CPU device."""
    device, backend = detect_gpu_backend()
    info = f"Backend: {backend}"
    if backend == "cuda":
        info += f", Name: {torch.cuda.get_device_name(0)}"
    elif backend == "mps":
        info += ", Apple Silicon (MPS)"
    elif backend == "rocm":
        info += ", AMD ROCm"
    elif backend == "directml":
        info += ", DirectML (Windows, Intel/AMD/NVIDIA)"
    elif backend == "opencl":
        info += ", OpenCL (experimental)"
    else:
        info += ", CPU only"
    return info

def set_torch_device():
    """Returns the best torch.device for use in your models."""
    device, backend = detect_gpu_backend()
    if backend == "opencl":
        warnings.warn("OpenCL is not natively supported by PyTorch. Falling back to CPU.")
        return torch.device("cpu")
    return device

def clear_gpu_memory():
    """Clear GPU memory cache to prevent memory issues"""
    try:
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
    except Exception as e:
        print(f"[clear_gpu_memory] Warning: {e}")

def get_gpu_memory_info():
    """Get GPU memory usage information"""
    if torch.cuda.is_available():
        try:
            allocated = torch.cuda.memory_allocated() / 1024**3  # GB
            cached = torch.cuda.memory_reserved() / 1024**3  # GB
            return f"GPU Memory - Allocated: {allocated:.2f}GB, Cached: {cached:.2f}GB"
        except Exception:
            return "GPU Memory info unavailable"
    return "No CUDA GPU available"

if __name__ == "__main__":
    print("[GPU Detection]")
    info = get_gpu_info()
    print(info)
    device, backend = detect_gpu_backend()
    print(f"torch.device: {set_torch_device()}")
    print("Recommended install command:")
    print(recommend_torch_install(backend))
    print(get_gpu_memory_info())