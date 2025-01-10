# MLX


## Prerequisites

```bash
pip install mlx-lm
```

Required:
- Python 3.x

## Minimum RAM

The approximate formula to calculate minimum RAM in GB is:

```python
RAM_GB = (N * B) / (8 * 1024)
```

Where:
- N = Number of model parameters
- B = Bits per parameter (after quantization)

For Gemma 27B in 4-bit:

```
RAM_GB = (27B * 4) / (8 * 1024) ≈ 13.18 GB
```

Add ~2-4 GB for system overhead and runtime.


## See also:

- [mlx-lm](https://pypi.org/project/mlx-lm/)
- [mlx-examples](https://github.com/ml-explore/mlx-examples)
- [mlx-community](https://huggingface.co/mlx-community)