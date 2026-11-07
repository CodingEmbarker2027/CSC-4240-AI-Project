import os
import sys
import json
import time
import socket
import shutil
import subprocess

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

try:
    import psutil
except ImportError:
    psutil = None

try:
    import ollama
except ImportError:
    ollama = None

try:
    import numpy as np
except ImportError:
    np = None

# Tracks background process instance spawned by this script
_SPAWNED_OLLAMA_PROCESS = None


def safe_print(message):
    try:
        print(message)
    except UnicodeEncodeError:
        print(message.encode("ascii", "replace").decode("ascii"))


def is_ollama_online(host="127.0.0.1", port=11434):
    """Checks if the local port is open and listening before making API calls."""
    try:
        with socket.create_connection((host, port), timeout=1):
            return True
    except OSError:
        return False


def ensure_ollama_server_active():
    """Automatically launches the local Ollama background server if it is offline."""
    global _SPAWNED_OLLAMA_PROCESS

    if is_ollama_online():
        safe_print("OK: Local Ollama server is already awake and listening.")
        safe_print(
            "NOTE: GPU settings only apply when Ollama starts; check `ollama ps` "
            "after inference to confirm GPU use."
        )
        return True

    safe_print("WARNING: Local Ollama server is offline. Attempting an automatic background launch...")

    if shutil.which("ollama") is None:
        safe_print("ERROR: 'ollama' executable was not found in your system PATH.")
        return False

    # Configure the environment keys for Intel Arc GPU / Vulkan acceleration
    env = os.environ.copy()
    env["OLLAMA_VULKAN"] = "1"
    env["OLLAMA_IGPU_ENABLE"] = "1"

    try:
        if sys.platform == "win32":
            creation_flags = getattr(subprocess, "CREATE_NEW_CONSOLE", 0)
            _SPAWNED_OLLAMA_PROCESS = subprocess.Popen(
                ["ollama", "serve"],
                env=env,
                creationflags=creation_flags
            )
        else:
            _SPAWNED_OLLAMA_PROCESS = subprocess.Popen(
                ["ollama", "serve"],
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )

        for _ in range(10):
            time.sleep(1)
            if is_ollama_online():
                safe_print("OK: Successfully launched Ollama automatically in hardware accelerated mode!")
                return True

        safe_print("ERROR: Server process was spawned but failed to open port 11434 in time.")
        return False

    except FileNotFoundError:
        safe_print("ERROR: Could not automate launch: 'ollama' executable was not found in your system PATH.")
        return False


def shutdown_ollama_server(force=False):
    """
    Shuts down Ollama. If force=True, terminates any running Ollama process on the machine.
    Otherwise, cleanly terminates only the instance spawned by this test script.
    """
    global _SPAWNED_OLLAMA_PROCESS

    if _SPAWNED_OLLAMA_PROCESS is not None:
        safe_print("\nTerminating spawned Ollama server process...")
        try:
            _SPAWNED_OLLAMA_PROCESS.terminate()
            _SPAWNED_OLLAMA_PROCESS.wait(timeout=5)
            safe_print("OK: Spawned Ollama server shut down cleanly.")
        except Exception:
            _SPAWNED_OLLAMA_PROCESS.kill()
            safe_print("NOTICE: Force killed spawned Ollama process.")
        _SPAWNED_OLLAMA_PROCESS = None
        return

    if force:
        safe_print("\nForcing system-wide Ollama shutdown...")
        if sys.platform == "win32":
            subprocess.run(["taskkill", "/F", "/IM", "ollama.exe"], capture_output=True, check=False)
            subprocess.run(["taskkill", "/F", "/IM", "ollama_app.exe"], capture_output=True, check=False)
        else:
            subprocess.run(["pkill", "-f", "ollama"], capture_output=True, check=False)
        safe_print("OK: Ollama server shutdown complete.")
    else:
        safe_print("\nNOTICE: Ollama was already running externally prior to this test; leaving service intact.")


def report_model_placement():
    """Reports the device placement Ollama assigned to its currently loaded models."""
    try:
        result = subprocess.run(
            ["ollama", "ps"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as e:
        safe_print(f"WARNING: Could not check Ollama model placement: {e}")
        return

    if result.returncode != 0:
        safe_print(f"WARNING: `ollama ps` failed: {result.stderr.strip()}")
        return

    safe_print("\nOllama model placement (`ollama ps`):")
    safe_print(result.stdout.rstrip())


def configure_hardware_runtime():
    """Dynamically routes workloads based on live system memory allocations."""
    if psutil is None:
        raise RuntimeError("psutil is required for hardware detection. Install it with: python -m pip install psutil")

    vm = psutil.virtual_memory()
    total_ram_gb = round(vm.total / (1024 ** 3))

    # Updated: Uses qwen3:1.7b instead of qwen3:2b for <= 8GB
    if total_ram_gb <= 8:
        model_target, context_len = "qwen3:1.7b", 2048
    elif total_ram_gb <= 16:
        model_target, context_len = "qwen3:4b", 4096
    else:
        model_target, context_len = "qwen3:8b", 8192 if (vm.available / (1024 ** 3)) > 12 else 4096

    return model_target, context_len


def test_local_pipeline():
    if psutil is None:
        safe_print("ERROR: Missing dependency 'psutil'. Install it with: python -m pip install psutil")
        return

    if np is None:
        safe_print("ERROR: Missing dependency 'numpy'. Install it with: python -m pip install numpy")
        return

    if ollama is None:
        safe_print("ERROR: Missing dependency 'ollama'. Install it with: python -m pip install ollama")
        return

    # Enforce background execution before initializing model logic
    if not ensure_ollama_server_active():
        safe_print("STOP: Pipeline execution stopped due to missing background server layers.")
        return

    try:
        LLM_MODEL, context_len = configure_hardware_runtime()
        EMBED_MODEL = "all-minilm"

        print("=" * 60)
        safe_print(f"Starting Pipeline Verification (Target LLM: {LLM_MODEL})")
        print("=" * 60)
        safe_print(f"Extracting vector rows from embedding engine '{EMBED_MODEL}'...")

        jd = "Looking for a Python Developer who knows Flask."
        resume = "Experienced Software Engineer specializing in Python and Flask frameworks."

        # Step A: Get embeddings from local server instance
        res_emb = ollama.embeddings(model=EMBED_MODEL, prompt=resume)['embedding']
        jd_emb = ollama.embeddings(model=EMBED_MODEL, prompt=jd)['embedding']

        # Step B: Calculate vector similarity math
        score = float(np.dot(res_emb, jd_emb) / (np.linalg.norm(res_emb) * np.linalg.norm(jd_emb)))
        safe_print(f"Local Transformer Score calculated: {score:.4f}")

        # Step C: Trigger local model reasoning loop
        safe_print(f"Routing payload to local reasoning model ({LLM_MODEL})...")

        prompt = f"""Analyze this match. Transformer Score: {score:.2f}
        JD: {jd}
        Resume: {resume}
        Output must be strictly a valid JSON object matching this schema exactly: 
        {{"match_rating": 90, "reason": "text narrative explaining the score"}}"""

        response = ollama.generate(
            model=LLM_MODEL,
            prompt=prompt,
            format="json",
            options={"temperature": 0.1, "num_ctx": context_len}
        )

        report_model_placement()
        safe_print("\nConnection Successful! Local Model Response Object:")
        print(json.dumps(json.loads(response['response']), indent=2))
        print("=" * 60)

    except Exception as e:
        safe_print(f"\nError inside pipeline processing loop: {e}")

    finally:
        # Step D: Turn off the Ollama server once done
        # Set force=True if you want it to kill Ollama even if it was running as a system tray app
        shutdown_ollama_server(force=False)


if __name__ == "__main__":
    test_local_pipeline()