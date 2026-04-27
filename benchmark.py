# ============================================================
# Benchmark ONNX — Evaluación local en CPU
# ============================================================
# Requisitos:
#   pip install onnxruntime numpy torch
# Archivos esperados:
#   - ../data/test_data.pt
#   - ../models/baseline.onnx
#   - ../models/int8_static_model.onnx
#   - ../models/int8_static_pruned_model.onnx
#   - ../models/ablation.onnx
# ============================================================

import os
import time
import numpy as np
import onnxruntime as ort
import torch
from data_utils import get_loaders

# Rutas relativas al script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "..", "data")
MODELS_DIR = os.path.join(SCRIPT_DIR, "..", "models")

# Validar que existen los directorios
if not os.path.isdir(DATA_DIR):
    raise FileNotFoundError(f"Directorio de datos no encontrado: {DATA_DIR}")
if not os.path.isdir(MODELS_DIR):
    raise FileNotFoundError(f"Directorio de modelos no encontrado: {MODELS_DIR}")

# ============================================================
# 1. Cargar test set desde directorio
# ============================================================
test_dir = os.path.join(DATA_DIR, "test")
if not os.path.isdir(test_dir):
    raise FileNotFoundError(f"Directorio de test no encontrado: {test_dir}")

print("=" * 70)
print("BASELINE DE REFERENCIA — FP32 GPU (CUDA)")
print("=" * 70)
print(f"{'Métrica':<35} {'Valor':>20}")
print("-" * 70)
print(f"{'Accuracy (validación)':<35} {79.32:>19.2f}%")
print(f"{'Loss (validación)':<35} {0.9008:>20.4f}")
print(f"{'Accuracy (test)':<35} {79.09:>19.2f}%")
print(f"{'Loss (test)':<35} {0.8517:>20.4f}")
print(f"{'Tamaño en disco':<35} {9.52:>18.2f} MB")
print(f"{'Latencia GPU (CUDA)':<35} {0.99:>18.2f} ms")
print(f"{'FPS GPU':<35} {1012.0:>20.1f}")
print(f"{'Latencia CPU (ref)':<35} {7.27:>18.2f} ms")
print(f"{'FPS CPU (ref)':<35} {137.6:>20.1f}")
print(f"{'Peak Memory GPU':<35} {71.10:>18.2f} MB")
print("=" * 70)
print("\nEvaluando optimizaciones ONNX en CPU:\n")

print("Cargando datasets...")
test_loader, val_loader, num_classes, class_names = get_loaders(
    DATA_DIR,
    batch_size=1,
    num_workers=0,
    img_size=64
)

# Contar imágenes
val_images = len(val_loader.dataset)
test_images = len(test_loader.dataset)
print(f"Validation set: {val_images} imágenes, {num_classes} clases")
print(f"Test set: {test_images} imágenes, {num_classes} clases")
print(f"Clases: {', '.join(class_names)}\n")


# ============================================================
# 2. Función auxiliar para evaluar en cualquier loader
# ============================================================
def evaluate_on_loader(sess, input_name, output_name, data_loader):
    """Evalúa accuracy y loss en un loader"""
    correct = 0
    total = 0
    total_loss = 0.0

    for batch_imgs, batch_labels in data_loader:
        batch_imgs_np = batch_imgs.numpy().astype(np.float32)
        batch_labels_np = batch_labels.numpy()

        logits = sess.run([output_name], {input_name: batch_imgs_np})[0]

        # Cross entropy manual (numpy)
        shifted = logits - logits.max(axis=1, keepdims=True)
        exp = np.exp(shifted)
        probs = exp / exp.sum(axis=1, keepdims=True)
        log_probs = np.log(probs[np.arange(len(batch_labels_np)), batch_labels_np] + 1e-12)
        total_loss += -log_probs.sum()

        preds = logits.argmax(axis=1)
        correct += (preds == batch_labels_np).sum()
        total += len(batch_labels_np)

    accuracy = 100.0 * correct / total
    loss = total_loss / total
    return accuracy, loss


# ============================================================
# 3. Función de evaluación por modelo
# ============================================================
def evaluate_onnx(onnx_path, model_name, val_loader, test_loader, n_warmup=25, n_runs=100):
    if not os.path.isfile(onnx_path):
        raise FileNotFoundError(f"Modelo ONNX no encontrado: {onnx_path}")

    print("=" * 65)
    print(f"MÉTRICAS ONNX - {model_name}")
    print("=" * 65)

    # --- Crear sesión ONNX Runtime ---
    sess_options = ort.SessionOptions()
    sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

    sess = ort.InferenceSession(
        onnx_path,
        sess_options=sess_options,
        providers=["CPUExecutionProvider"]
    )
    input_name  = sess.get_inputs()[0].name
    output_name = sess.get_outputs()[0].name

    # --- Tamaño en disco (incluyendo .data si existe) ---
    size_bytes = os.path.getsize(onnx_path)
    data_file = onnx_path.replace('.onnx', '.onnx.data')
    if os.path.isfile(data_file):
        size_bytes += os.path.getsize(data_file)
    size_mb = size_bytes / (1024 ** 2)

    # --- Latencia CPU (single sample) con warmup primero ---
    dummy = np.random.randn(1, 3, 64, 64).astype(np.float32)

    for _ in range(n_warmup):
        sess.run([output_name], {input_name: dummy})

    latencies = []
    for _ in range(n_runs):
        t0 = time.perf_counter()
        sess.run([output_name], {input_name: dummy})
        t1 = time.perf_counter()
        latencies.append((t1 - t0) * 1000)

    avg_latency = np.mean(latencies)
    std_latency = np.std(latencies)
    p50 = np.percentile(latencies, 50)
    p95 = np.percentile(latencies, 95)
    fps = 1000.0 / avg_latency

    # --- Accuracy + Loss en validation ---
    val_acc, val_loss = evaluate_on_loader(sess, input_name, output_name, val_loader)

    # --- Accuracy + Loss + Throughput en test set ---
    t_start = time.perf_counter()
    test_acc, test_loss = evaluate_on_loader(sess, input_name, output_name, test_loader)
    t_end = time.perf_counter()

    # Throughput real del dataset
    dataset_time = t_end - t_start
    throughput_fps = len(test_loader.dataset) / dataset_time

    # --- Print tabla ---
    print(f"{'Métrica':<35} {'Valor':>20}")
    print("-" * 65)
    print(f"{'Accuracy (validación)':<35} {val_acc:>19.2f}%")
    print(f"{'Loss (validación)':<35} {val_loss:>20.4f}")
    print(f"{'Accuracy (test)':<35} {test_acc:>19.2f}%")
    print(f"{'Loss (test)':<35} {test_loss:>20.4f}")
    print(f"{'Tamaño en disco':<35} {size_mb:>18.2f} MB")
    print(f"{'Latencia CPU (avg)':<35} {avg_latency:>18.2f} ms")
    print(f"{'Latencia CPU (std)':<35} {std_latency:>18.2f} ms")
    print(f"{'Latencia CPU (p50)':<35} {p50:>18.2f} ms")
    print(f"{'Latencia CPU (p95)':<35} {p95:>18.2f} ms")
    print(f"{'FPS (single-sample)':<35} {fps:>20.1f}")
    print(f"{'Throughput (dataset)':<35} {throughput_fps:>19.1f} img/s")
    print("=" * 65)
    print()

    return {
        "val_acc":     val_acc,
        "val_loss":    val_loss,
        "test_acc":    test_acc,
        "test_loss":   test_loss,
        "size":        size_mb,
        "latency":     avg_latency,
        "latency_std": std_latency,
        "latency_p50": p50,
        "latency_p95": p95,
        "fps":         fps,
        "throughput":  throughput_fps,
    }


# ============================================================
# 3. Tabla comparativa
# ============================================================
def print_comparison_table(models_dict, metrics=None):
    if metrics is None:
        metrics = [
            ("Val Accuracy (%)",   "val_acc"),
            ("Val Loss",           "val_loss"),
            ("Test Accuracy (%)",  "test_acc"),
            ("Test Loss",          "test_loss"),
            ("Tamaño (MB)",        "size"),
            ("Latencia avg (ms)",  "latency"),
            ("Latencia p95 (ms)",  "latency_p95"),
            ("FPS (single)",       "fps"),
            ("Throughput img/s",   "throughput"),
        ]

    model_names  = list(models_dict.keys())
    col_width    = 18
    total_width  = 25 + col_width * len(model_names)

    print("\n" + "=" * total_width)
    print("COMPARACIÓN FINAL — ONNX en CPU local")
    print("=" * total_width)

    header = f"{'Métrica':<25}"
    for name in model_names:
        header += f"{name:>{col_width}}"
    print(header)
    print("-" * total_width)

    def safe_get(d, key):
        if d is None:
            return "-"
        val = d.get(key, "-")
        return f"{val:.3f}" if isinstance(val, (int, float)) else val

    for metric_name, key in metrics:
        row = f"{metric_name:<25}"
        for name in model_names:
            val = safe_get(models_dict[name], key)
            row += f"{str(val):>{col_width}}"
        print(row)

    print("=" * total_width)


# ============================================================
# 4. Ejecutar benchmark
# ============================================================
results = {
    "Baseline":     evaluate_onnx(os.path.join(MODELS_DIR, "baseline.onnx"),                 "Baseline", val_loader, test_loader),
    "INT8 Static":  evaluate_onnx(os.path.join(MODELS_DIR, "int8_static_model.onnx"),        "INT8 Static", val_loader, test_loader),
    "INT8 Pruned":  evaluate_onnx(os.path.join(MODELS_DIR, "int8_static_pruned_model.onnx"), "INT8 Static Pruned", val_loader, test_loader),
    "Ablation":     evaluate_onnx(os.path.join(MODELS_DIR, "ablation.onnx"),                 "Ablation", val_loader, test_loader),
}


results["FP32 GPU"] = {
    "val_acc":     79.32,
    "val_loss":    0.9008,
    "test_acc":    79.09,
    "test_loss":   0.8517,
    "size":        9.52,
    "latency":     0.99,
    "latency_std": 0.0,      # no lo tenés → podés dejar 0 o "-"
    "latency_p50": 0.99,
    "latency_p95": 0.99,
    "fps":         1012.0,
    "throughput":  1012.0,   # equivalente en este caso
}

results = {
    "Baseline GPU": results["FP32 GPU"],
    "Baseline CPU": results["Baseline"],
    "INT8 Static": results["INT8 Static"],
    "INT8 Pruned": results["INT8 Pruned"],
    "Ablation": results["Ablation"],
}

print_comparison_table(results)


# ============================================================
# 5. Reducciones relativas vs GPU Baseline
# ============================================================
GPU_BASELINE = {
    "size": 9.52,           # MB
    "latency": 0.99,        # ms (GPU)
    "throughput": 1012.0,   # FPS GPU
    "test_acc": 79.09,      # %
}

print("\nComparación vs FP32 GPU Baseline (0.99ms latencia):")
print("-" * 75)
print(f"{'Modelo':<20} {'Tamaño (vs GPU)':>18} {'Latencia CPU':>16} {'Δ Accuracy':>14}")
print("-" * 75)

for name, r in results.items():
    size_red = (1 - r["size"] / GPU_BASELINE["size"]) * 100
    # Latencia: mostrar en ms absoluto, no relativo (CPU es más lento)
    lat_cpu = r["latency"]
    lat_vs_gpu = (r["latency"] / GPU_BASELINE["latency"] - 1) * 100
    acc_diff = r["test_acc"] - GPU_BASELINE["test_acc"]

    print(f"{name:<20} {size_red:>+17.1f}% {lat_cpu:>12.2f}ms ({lat_vs_gpu:+6.1f}%) {acc_diff:>+13.2f}%")

print("-" * 75)
print(f"\nNota: GPU Baseline (referencia) = 0.99ms latencia, 1012 FPS, 71.10 MB Peak Memory")