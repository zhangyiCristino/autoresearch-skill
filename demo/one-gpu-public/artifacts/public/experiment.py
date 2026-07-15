"""Prepare the frozen, bounded Covertype Gate 2 pilot."""

import argparse
import gzip
import hashlib
import json
import os
import time
from pathlib import Path

import numpy as np

os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")
import torch


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1048576), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_row_ids(row_count, data_sha256):
    return [
        hashlib.sha256(f"{data_sha256}:{index}".encode()).hexdigest()
        for index in range(row_count)
    ]


def _rank(indices, prefix, row_ids):
    return np.asarray(
        sorted(
            (int(index) for index in indices),
            key=lambda index: hashlib.sha256(
                f"{prefix}{row_ids[index]}".encode()
            ).digest(),
        ),
        dtype=np.int64,
    )


def build_partitions(
    rows, data_sha256, pilot_area, random_seed, validation_seed, validation_fraction
):
    labels = rows[:, 54]
    row_ids = stable_row_ids(len(rows), data_sha256)
    area_test = np.flatnonzero(rows[:, 9 + pilot_area] == 1).astype(np.int64)
    test_counts = {label: int(np.sum(labels[area_test] == label)) for label in range(1, 8)}
    random_parts = []
    for label in range(1, 8):
        candidates = np.flatnonzero(labels == label)
        ranked = _rank(candidates, f"test|{random_seed}|", row_ids)
        random_parts.append(ranked[: test_counts[label]])
    random_test = np.sort(np.concatenate(random_parts)).astype(np.int64)
    result = {}
    area_name = f"area{pilot_area}"
    for name, test in ((f"{area_name}-holdout", area_test), (f"{area_name}-random", random_test)):
        available = np.setdiff1d(np.arange(len(rows), dtype=np.int64), test)
        validation_parts = []
        for label in range(1, 8):
            candidates = available[labels[available] == label]
            ranked = _rank(candidates, f"val|{validation_seed}|", row_ids)
            validation_parts.append(ranked[: int(len(candidates) * validation_fraction)])
        validation = np.sort(np.concatenate(validation_parts)).astype(np.int64)
        train = np.setdiff1d(available, validation).astype(np.int64)
        result[name] = {"train": train, "validation": validation, "test": np.sort(test)}
    return result


def training_statistics(rows, train_indices):
    continuous = rows[train_indices, :10].astype(np.float64)
    mean = continuous.mean(axis=0)
    scale = continuous.std(axis=0)
    if not np.all(np.isfinite(mean)) or not np.all(np.isfinite(scale)) or np.any(scale == 0):
        raise ValueError("invalid train-only normalization statistics")
    return {"mean": mean, "scale": scale}


def transform_features(rows, statistics):
    continuous = rows[:, :10].astype(np.float32)
    continuous = (continuous - statistics["mean"]) / statistics["scale"]
    soil = rows[:, 14:54].astype(np.float32)
    return np.concatenate((continuous.astype(np.float32), soil), axis=1)


def build_model():
    return torch.nn.Sequential(
        torch.nn.Linear(50, 128),
        torch.nn.ReLU(),
        torch.nn.Linear(128, 64),
        torch.nn.ReLU(),
        torch.nn.Linear(64, 7),
    )


def _classification_metrics(model, features, labels, indices, device, batch_size):
    dataset = torch.utils.data.TensorDataset(
        torch.from_numpy(features[indices]), torch.from_numpy(labels[indices])
    )
    loader = torch.utils.data.DataLoader(
        dataset, batch_size=batch_size, shuffle=False, num_workers=0
    )
    confusion = np.zeros((7, 7), dtype=np.int64)
    loss_total = 0.0
    loss_function = torch.nn.CrossEntropyLoss(reduction="sum")
    model.eval()
    with torch.no_grad():
        for batch_features, batch_labels in loader:
            batch_features = batch_features.to(device)
            batch_labels = batch_labels.to(device)
            logits = model(batch_features)
            loss_total += float(loss_function(logits, batch_labels))
            predictions = torch.argmax(logits, dim=1)
            encoded = batch_labels * 7 + predictions
            confusion += torch.bincount(encoded, minlength=49).reshape(7, 7).cpu().numpy()
    support = confusion.sum(axis=1)
    predicted = confusion.sum(axis=0)
    true_positive = np.diag(confusion).astype(np.float64)
    recall = np.divide(true_positive, support, out=np.zeros(7), where=support > 0)
    precision = np.divide(true_positive, predicted, out=np.zeros(7), where=predicted > 0)
    f1 = np.divide(
        2 * precision * recall,
        precision + recall,
        out=np.zeros(7),
        where=(precision + recall) > 0,
    )
    present = support > 0
    return {
        "loss": loss_total / int(support.sum()),
        "accuracy": float(true_positive.sum() / support.sum()),
        "macro_f1_present_labels": float(f1[present].mean()),
        "class_coverage": f"{int(present.sum())}/7",
        "per_class_recall": {str(i + 1): float(recall[i]) for i in range(7)},
        "prediction_distribution": {
            str(i + 1): int(predicted[i]) for i in range(7)
        },
        "confusion_matrix": confusion.tolist(),
    }


def train_condition(
    features,
    labels,
    train_indices,
    validation_indices,
    settings,
    device,
    deadline=None,
    test_indices=None,
):
    seed = int(settings["model_seed"])
    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(True)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(seed)
        torch.backends.cudnn.benchmark = False
    model = build_model().to(device=device, dtype=torch.float32)
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=settings["learning_rate"],
        weight_decay=settings["weight_decay"],
        betas=tuple(settings["betas"]),
        eps=settings["epsilon"],
    )
    loss_function = torch.nn.CrossEntropyLoss()
    x_train = torch.from_numpy(features[train_indices])
    y_train = torch.from_numpy(labels[train_indices])
    x_validation = torch.from_numpy(features[validation_indices])
    y_validation = torch.from_numpy(labels[validation_indices])
    generator = torch.Generator().manual_seed(seed)
    loader = torch.utils.data.DataLoader(
        torch.utils.data.TensorDataset(x_train, y_train),
        batch_size=settings["batch_size"],
        shuffle=True,
        generator=generator,
        num_workers=0,
    )
    train_losses = []
    validation_losses = []
    for _epoch in range(settings["epochs"]):
        model.train()
        total = 0.0
        count = 0
        for batch_features, batch_labels in loader:
            if deadline is not None and time.monotonic() >= deadline:
                raise RuntimeError("wall budget exceeded")
            batch_features = batch_features.to(device)
            batch_labels = batch_labels.to(device)
            optimizer.zero_grad(set_to_none=True)
            loss = loss_function(model(batch_features), batch_labels)
            if not torch.isfinite(loss):
                raise RuntimeError("non-finite training loss")
            loss.backward()
            optimizer.step()
            total += float(loss.detach()) * len(batch_labels)
            count += len(batch_labels)
        train_losses.append(total / count)
        model.eval()
        with torch.no_grad():
            validation_loss = loss_function(
                model(x_validation.to(device)), y_validation.to(device)
            )
        if not torch.isfinite(validation_loss):
            raise RuntimeError("non-finite validation loss")
        validation_losses.append(float(validation_loss))
    result = {
        "train_loss": train_losses,
        "validation_loss": validation_losses,
        "epochs": int(settings["epochs"]),
    }
    if test_indices is not None:
        result["test_metrics"] = _classification_metrics(
            model, features, labels, test_indices, device, settings["batch_size"]
        )
    return result


def area_coverage(rows, area):
    test = rows[:, 9 + area] == 1
    test_classes = set(int(value) for value in np.unique(rows[test, 54]))
    train_classes = set(int(value) for value in np.unique(rows[~test, 54]))
    missing = sorted(test_classes - train_classes)
    return {
        "status": "coverage-failure" if missing else "covered",
        "missing_train_classes": missing,
        "train_allowed": not missing,
    }


def _partition_hash(indices, row_ids):
    digest = hashlib.sha256()
    for index in np.sort(indices):
        digest.update(row_ids[int(index)].encode())
        digest.update(b"\n")
    return digest.hexdigest()


def _counts(labels, indices):
    return {str(label): int(np.sum(labels[indices] == label)) for label in range(1, 8)}


def prepare(config_path):
    config = json.loads(config_path.read_text(encoding="utf-8"))
    run_root = Path(__file__).resolve().parents[2]
    data_path = run_root / "source" / "extracted" / "covtype.data.gz"
    if sha256_file(data_path) != config["dataset"]["data_sha256"]:
        raise ValueError("dataset hash drift")
    with gzip.open(data_path, "rt", encoding="ascii") as stream:
        rows = np.loadtxt(stream, delimiter=",", dtype=np.int32)
    if rows.shape != (config["dataset"]["row_count"], config["dataset"]["column_count"]):
        raise ValueError("dataset shape drift")
    if np.any(rows[:, 10:14].sum(axis=1) != 1) or np.any(rows[:, 14:54].sum(axis=1) != 1):
        raise ValueError("one-hot integrity failure")
    split = config["split"]
    partitions = build_partitions(
        rows,
        config["dataset"]["data_sha256"],
        split["pilot_area"],
        split["random_test_seed"],
        split["validation_seed"],
        split["validation_fraction_per_class"],
    )
    labels = rows[:, 54]
    row_ids = stable_row_ids(len(rows), config["dataset"]["data_sha256"])
    arrays = {}
    partition_hashes = {}
    conditions = {}
    for condition, parts in partitions.items():
        conditions[condition] = {
            "row_count": int(len(parts["test"])),
            "class_counts": _counts(labels, parts["test"]),
        }
        for name, indices in parts.items():
            arrays[f"{condition.replace('-', '_')}_{name}"] = indices
            partition_hashes[f"{condition}.{name}"] = _partition_hash(indices, row_ids)
        statistics = training_statistics(rows, parts["train"])
        arrays[f"{condition.replace('-', '_')}_mean"] = statistics["mean"]
        arrays[f"{condition.replace('-', '_')}_scale"] = statistics["scale"]
    local_bundle = run_root / "source" / "frozen-preparation.npz"
    np.savez_compressed(local_bundle, **arrays)
    manifest = {
        "schema_version": "1.0",
        "record_type": "split-manifest",
        "dataset_sha256": config["dataset"]["data_sha256"],
        "algorithm": {
            "row_id_algorithm": split["row_id_algorithm"],
            "random_test_algorithm": split["random_test_algorithm"],
            "validation_algorithm": split["validation_algorithm"],
        },
        "conditions": conditions,
        "aggregate_counts": {
            "row_count": int(len(rows)),
            "class_counts": _counts(labels, np.arange(len(rows))),
        },
        "partition_hashes": partition_hashes,
        "limitations": [
            "Full row IDs and indices remain local and are not public artifacts.",
            "Area 4 is a coverage failure and is not trained or compared.",
        ],
    }
    manifest_path = config_path.parent / "split-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def train_pilot(config_path, expected_config_hash, expected_split_hash):
    split_path = config_path.parent / "split-manifest.json"
    if sha256_file(config_path) != expected_config_hash:
        raise ValueError("config hash drift")
    if sha256_file(split_path) != expected_split_hash:
        raise ValueError("split manifest hash drift")
    config = json.loads(config_path.read_text(encoding="utf-8"))
    manifest = json.loads(split_path.read_text(encoding="utf-8"))
    run_root = Path(__file__).resolve().parents[2]
    data_path = run_root / "source" / "extracted" / "covtype.data.gz"
    if sha256_file(data_path) != config["dataset"]["data_sha256"]:
        raise ValueError("dataset hash drift")
    with gzip.open(data_path, "rt", encoding="ascii") as stream:
        rows = np.loadtxt(stream, delimiter=",", dtype=np.int32)
    frozen = np.load(run_root / "source" / "frozen-preparation.npz", allow_pickle=False)
    row_ids = stable_row_ids(len(rows), config["dataset"]["data_sha256"])
    conditions = ("area3-holdout", "area3-random")
    partitions = {}
    for condition in conditions:
        prefix = condition.replace("-", "_")
        partitions[condition] = {}
        for name in ("train", "validation", "test"):
            indices = frozen[f"{prefix}_{name}"]
            if _partition_hash(indices, row_ids) != manifest["partition_hashes"][f"{condition}.{name}"]:
                raise ValueError("frozen partition hash drift")
            partitions[condition][name] = indices
    if not torch.cuda.is_available() or torch.cuda.device_count() < 1:
        raise RuntimeError("approved CUDA device unavailable")
    device = torch.device("cuda:0")
    device_name = torch.cuda.get_device_name(device)
    if "RTX 4060 Laptop GPU" not in device_name:
        raise RuntimeError("CUDA device class mismatch")
    torch.cuda.reset_peak_memory_stats(device)
    torch.cuda.synchronize(device)
    start_wall = time.monotonic()
    deadline = start_wall + config["pilot"]["gpu_minutes_max"] * 60
    start_event = torch.cuda.Event(enable_timing=True)
    end_event = torch.cuda.Event(enable_timing=True)
    start_event.record()
    settings = dict(config["training"])
    settings["model_seed"] = config["pilot"]["model_seed"]
    labels = rows[:, 54].astype(np.int64) - 1
    results = {}
    for condition in conditions:
        statistics = training_statistics(rows, partitions[condition]["train"])
        features = transform_features(rows, statistics)
        results[condition] = train_condition(
            features,
            labels,
            partitions[condition]["train"],
            partitions[condition]["validation"],
            settings,
            device,
            deadline,
        )
        del features
    end_event.record()
    torch.cuda.synchronize(device)
    wall_seconds = time.monotonic() - start_wall
    gpu_seconds = start_event.elapsed_time(end_event) / 1000.0
    peak_vram_gib = torch.cuda.max_memory_allocated(device) / (1024 ** 3)
    if wall_seconds > config["pilot"]["wall_minutes_max"] * 60:
        raise RuntimeError("wall budget exceeded")
    if gpu_seconds > config["pilot"]["gpu_minutes_max"] * 60 or peak_vram_gib > 7.2:
        raise RuntimeError("GPU budget exceeded")
    aggregate = {
        "schema_version": "1.0",
        "record_type": "pilot-aggregate",
        "status": "trained-no-test-evaluation",
        "code_hash": sha256_file(Path(__file__)),
        "config_hash": expected_config_hash,
        "split_hash": expected_split_hash,
        "data_hash": config["dataset"]["data_sha256"],
        "conditions": results,
        "runtime": {
            "gpu_seconds": gpu_seconds,
            "wall_seconds": wall_seconds,
            "peak_vram_gib": peak_vram_gib,
        },
    }
    result_path = run_root / "source" / "pilot-aggregate.json"
    result_path.write_text(json.dumps(aggregate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"status": aggregate["status"], "result_sha256": sha256_file(result_path)}


def prepare_full(config_path):
    config = json.loads(config_path.read_text(encoding="utf-8"))
    run_root = Path(__file__).resolve().parents[2]
    data_path = run_root / "source" / "extracted" / "covtype.data.gz"
    if sha256_file(data_path) != config["dataset"]["data_sha256"]:
        raise ValueError("dataset hash drift")
    with gzip.open(data_path, "rt", encoding="ascii") as stream:
        rows = np.loadtxt(stream, delimiter=",", dtype=np.int32)
    split = config["split"]
    labels = rows[:, 54]
    row_ids = stable_row_ids(len(rows), config["dataset"]["data_sha256"])
    arrays = {}
    partition_hashes = {}
    conditions = {}
    for area in config["future_full"]["areas"]:
        partitions = build_partitions(
            rows,
            config["dataset"]["data_sha256"],
            area,
            split["random_test_seed"],
            split["validation_seed"],
            split["validation_fraction_per_class"],
        )
        for condition, parts in partitions.items():
            conditions[condition] = {
                "row_count": int(len(parts["test"])),
                "class_counts": _counts(labels, parts["test"]),
            }
            prefix = condition.replace("-", "_")
            for name, indices in parts.items():
                arrays[f"{prefix}_{name}"] = indices
                partition_hashes[f"{condition}.{name}"] = _partition_hash(
                    indices, row_ids
                )
    np.savez_compressed(run_root / "source" / "frozen-full-preparation.npz", **arrays)
    manifest = {
        "schema_version": "1.0",
        "record_type": "split-manifest",
        "dataset_sha256": config["dataset"]["data_sha256"],
        "algorithm": {
            "row_id_algorithm": split["row_id_algorithm"],
            "random_test_algorithm": split["random_test_algorithm"],
            "validation_algorithm": split["validation_algorithm"],
        },
        "conditions": conditions,
        "aggregate_counts": {
            "row_count": int(len(rows)),
            "class_counts": _counts(labels, np.arange(len(rows))),
        },
        "partition_hashes": partition_hashes,
        "area4_coverage": area_coverage(rows, 4),
        "limitations": [
            "Full row IDs and indices remain local.",
            "Area 4 is recorded only as a coverage failure and is not trained.",
        ],
    }
    path = run_root / "source" / "full-split-manifest.json"
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"status": "full-prepared", "split_sha256": sha256_file(path)}


def train_full(config_path, expected_config_hash, expected_full_split_hash):
    if sha256_file(config_path) != expected_config_hash:
        raise ValueError("config hash drift")
    config = json.loads(config_path.read_text(encoding="utf-8"))
    run_root = Path(__file__).resolve().parents[2]
    split_path = run_root / "source" / "full-split-manifest.json"
    if sha256_file(split_path) != expected_full_split_hash:
        raise ValueError("full split manifest hash drift")
    manifest = json.loads(split_path.read_text(encoding="utf-8"))
    data_path = run_root / "source" / "extracted" / "covtype.data.gz"
    if sha256_file(data_path) != config["dataset"]["data_sha256"]:
        raise ValueError("dataset hash drift")
    with gzip.open(data_path, "rt", encoding="ascii") as stream:
        rows = np.loadtxt(stream, delimiter=",", dtype=np.int32)
    frozen = np.load(run_root / "source" / "frozen-full-preparation.npz", allow_pickle=False)
    row_ids = stable_row_ids(len(rows), config["dataset"]["data_sha256"])
    if not torch.cuda.is_available() or torch.cuda.device_count() < 1:
        raise RuntimeError("approved CUDA device unavailable")
    device = torch.device("cuda:0")
    if "RTX 4060 Laptop GPU" not in torch.cuda.get_device_name(device):
        raise RuntimeError("CUDA device class mismatch")
    torch.cuda.reset_peak_memory_stats(device)
    torch.cuda.synchronize(device)
    start_wall = time.monotonic()
    wall_limit = config["future_full"]["cumulative_wall_hours_max_including_pilot"] * 3600 - 120
    deadline = start_wall + wall_limit
    start_event = torch.cuda.Event(enable_timing=True)
    end_event = torch.cuda.Event(enable_timing=True)
    start_event.record()
    labels = rows[:, 54].astype(np.int64) - 1
    settings = dict(config["training"])
    results = {}
    deltas = {}
    for area in config["future_full"]["areas"]:
        area_key = f"area{area}"
        area_results = {}
        prepared = {}
        for suffix in ("holdout", "random"):
            condition = f"{area_key}-{suffix}"
            prefix = condition.replace("-", "_")
            parts = {}
            for name in ("train", "validation", "test"):
                indices = frozen[f"{prefix}_{name}"]
                expected = manifest["partition_hashes"][f"{condition}.{name}"]
                if _partition_hash(indices, row_ids) != expected:
                    raise ValueError("frozen full partition hash drift")
                parts[name] = indices
            statistics = training_statistics(rows, parts["train"])
            prepared[condition] = (transform_features(rows, statistics), parts)
        for seed in config["future_full"]["model_seeds"]:
            seed_key = str(seed)
            area_results[seed_key] = {}
            for suffix in ("holdout", "random"):
                condition = f"{area_key}-{suffix}"
                features, parts = prepared[condition]
                run_settings = dict(settings)
                run_settings["model_seed"] = seed
                area_results[seed_key][suffix] = train_condition(
                    features,
                    labels,
                    parts["train"],
                    parts["validation"],
                    run_settings,
                    device,
                    deadline,
                    test_indices=parts["test"],
                )
            deltas[f"{area_key}.seed{seed}"] = (
                area_results[seed_key]["random"]["test_metrics"]["macro_f1_present_labels"]
                - area_results[seed_key]["holdout"]["test_metrics"]["macro_f1_present_labels"]
            )
        results[area_key] = area_results
        del prepared
    end_event.record()
    torch.cuda.synchronize(device)
    wall_seconds = time.monotonic() - start_wall
    gpu_seconds = start_event.elapsed_time(end_event) / 1000.0
    peak_vram_gib = torch.cuda.max_memory_allocated(device) / (1024 ** 3)
    gpu_limit = config["future_full"]["cumulative_gpu_hours_max_including_pilot"] * 3600 - 120
    if wall_seconds > wall_limit or gpu_seconds > gpu_limit or peak_vram_gib > 7.2:
        raise RuntimeError("full resource budget exceeded")
    delta_values = np.asarray(list(deltas.values()), dtype=np.float64)
    aggregate = {
        "schema_version": "1.0",
        "record_type": "full-aggregate",
        "status": "full-trained-test-evaluated-awaiting-gate4",
        "code_hash": sha256_file(Path(__file__)),
        "config_hash": expected_config_hash,
        "full_split_hash": expected_full_split_hash,
        "data_hash": config["dataset"]["data_sha256"],
        "results": results,
        "delta_macro_f1_random_minus_holdout": deltas,
        "delta_summary": {
            "mean": float(delta_values.mean()),
            "sample_std": float(delta_values.std(ddof=1)),
        },
        "runtime": {
            "gpu_seconds": gpu_seconds,
            "wall_seconds": wall_seconds,
            "peak_vram_gib": peak_vram_gib,
        },
        "claim_status": "awaiting-gate4-no-public-conclusion",
    }
    result_path = run_root / "source" / "full-aggregate.json"
    result_path.write_text(json.dumps(aggregate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"status": aggregate["status"], "result_sha256": sha256_file(result_path)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("prepare", "train", "prepare-full", "full"))
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--expected-config-sha256")
    parser.add_argument("--expected-split-sha256")
    args = parser.parse_args()
    if args.command == "prepare":
        manifest = prepare(args.config)
        output = {"status": "prepared", "partition_hashes": manifest["partition_hashes"]}
    elif args.command == "prepare-full":
        output = prepare_full(args.config)
    elif args.command == "train":
        if not args.expected_config_sha256 or not args.expected_split_sha256:
            parser.error("train requires both expected SHA-256 values")
        output = train_pilot(
            args.config, args.expected_config_sha256, args.expected_split_sha256
        )
    else:
        if not args.expected_config_sha256 or not args.expected_split_sha256:
            parser.error("full requires both expected SHA-256 values")
        output = train_full(
            args.config, args.expected_config_sha256, args.expected_split_sha256
        )
    print(json.dumps(output, sort_keys=True))


if __name__ == "__main__":
    main()
