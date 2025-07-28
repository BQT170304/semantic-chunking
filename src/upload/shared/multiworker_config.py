"""
Configuration utilities for multi-worker document processing.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class MultiWorkerConfig:
    """Configuration for multi-worker document processing."""

    max_workers: Optional[int] = None
    enable_multiprocessing: bool = False  # Use ProcessPoolExecutor instead of ThreadPoolExecutor
    memory_limit_per_worker_mb: int = 512  # Memory limit per worker in MB
    timeout_per_file_seconds: int = 300  # Timeout per file processing in seconds

    @classmethod
    def from_environment(cls) -> MultiWorkerConfig:
        """Create configuration from environment variables."""
        return cls(
            max_workers=int(os.getenv('UPLOAD_MAX_WORKERS', '0')) or None,
            enable_multiprocessing=os.getenv('UPLOAD_USE_MULTIPROCESSING', 'false').lower() == 'true',
            memory_limit_per_worker_mb=int(os.getenv('UPLOAD_MEMORY_LIMIT_MB', '512')),
            timeout_per_file_seconds=int(os.getenv('UPLOAD_TIMEOUT_SECONDS', '300')),
        )

    @classmethod
    def auto_configure(cls, file_count: int) -> MultiWorkerConfig:
        """Auto-configure based on system resources and file count."""
        cpu_count = os.cpu_count() or 1

        # Calculate optimal worker count
        if file_count <= 1:
            max_workers = 1
        elif file_count <= 4:
            max_workers = min(file_count, cpu_count)
        else:
            # For I/O bound operations, can use more workers than CPU cores
            max_workers = min(file_count, cpu_count * 2, 8)

        return cls(
            max_workers=max_workers,
            enable_multiprocessing=file_count > 10,  # Use multiprocessing for large batches
            memory_limit_per_worker_mb=max(256, 1024 // max_workers),  # Adjust memory per worker
            timeout_per_file_seconds=300,
        )

    def validate(self) -> None:
        """Validate configuration parameters."""
        if self.max_workers is not None and self.max_workers < 1:
            raise ValueError('max_workers must be >= 1')

        if self.memory_limit_per_worker_mb < 128:
            raise ValueError('memory_limit_per_worker_mb must be >= 128')

        if self.timeout_per_file_seconds < 10:
            raise ValueError('timeout_per_file_seconds must be >= 10')


def get_optimal_worker_count(file_count: int, max_workers: Optional[int] = None) -> int:
    """Calculate optimal worker count based on file count and system resources."""
    if file_count <= 1:
        return 1

    cpu_count = os.cpu_count() or 1

    # Default calculation
    optimal = min(
        file_count,        # Don't exceed number of files
        cpu_count * 2,     # 2x CPU cores for I/O bound operations
        8,                  # Reasonable upper limit
    )

    # Apply user override if provided
    if max_workers is not None:
        optimal = min(optimal, max_workers)

    return max(1, optimal)


def estimate_memory_usage(file_count: int, avg_file_size_mb: float, max_workers: int) -> float:
    """Estimate memory usage for multi-worker processing."""
    # Each worker processes one file at a time
    # PDF/image processing can use 2-3x the file size in memory
    memory_multiplier = 2.5
    concurrent_files = min(file_count, max_workers)

    return concurrent_files * avg_file_size_mb * memory_multiplier


def check_system_resources(config: MultiWorkerConfig, file_count: int, avg_file_size_mb: float = 10) -> dict:
    """Check if system has adequate resources for the given configuration."""
    import psutil

    max_workers = config.max_workers or get_optimal_worker_count(file_count)
    estimated_memory_mb = estimate_memory_usage(file_count, avg_file_size_mb, max_workers)

    # Get system resources
    available_memory_mb = psutil.virtual_memory().available / (1024 * 1024)
    cpu_count = os.cpu_count() or 1

    warnings = []
    recommendations = []

    # Memory check
    memory_usage_percent = (estimated_memory_mb / available_memory_mb) * 100
    if memory_usage_percent > 80:
        warnings.append(f"High memory usage expected: {memory_usage_percent:.1f}%")
        recommendations.append(f"Consider reducing max_workers to {max_workers // 2}")

    # CPU check
    if max_workers > cpu_count * 2:
        warnings.append(f"Worker count ({max_workers}) much higher than CPU cores ({cpu_count})")
        recommendations.append(f"Consider reducing max_workers to {cpu_count * 2}")

    return {
        'max_workers': max_workers,
        'estimated_memory_mb': estimated_memory_mb,
        'available_memory_mb': available_memory_mb,
        'memory_usage_percent': memory_usage_percent,
        'cpu_count': cpu_count,
        'warnings': warnings,
        'recommendations': recommendations,
        'is_safe': len(warnings) == 0,
    }


# Example usage:
if __name__ == '__main__':
    # Auto-configure for 5 files
    config = MultiWorkerConfig.auto_configure(5)
    print(f"Auto config: {config}")

    # Check system resources
    resources = check_system_resources(config, 5, avg_file_size_mb=15)
    print(f"Resource check: {resources}")

    # Environment-based config
    env_config = MultiWorkerConfig.from_environment()
    print(f"Environment config: {env_config}")
