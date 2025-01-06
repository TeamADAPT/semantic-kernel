# Semantic Kernel Model Configuration Guide

## Validated Models

### Chat Models

```yaml
chat_models:
  pixtral_large:
    name: "pixtral-large-latest"
    capabilities: ["vision"]
    latency_target: 0.39s
    priority: high

  pixtral_12b:
    name: "pixtral-12b-latest"
    capabilities: ["vision"]
    latency_target: 0.39s
    priority: medium

  open_mixtral:
    name: "open-mixtral-8x22b"
    capabilities: ["text"]
    latency_target: 0.27s
    priority: high
    notes: "Best Performance"
```

### Embedding Models

```yaml
embedding_models:
  mistral_embed:
    name: "mistral-embed"
    latency_target: 0.19s
    priority: high
    notes: "Fastest embedding model"

  cohere_english:
    name: "Cohere-embed-v3-english"
    latency_target: 0.25s
    priority: medium

  cohere_multilingual:
    name: "Cohere-embed-v3-multilingual"
    latency_target: 0.30s
    priority: medium
```

## Model Integration

```python
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

class ModelCapability(Enum):
    TEXT = "text"
    VISION = "vision"
    EMBEDDING = "embedding"

@dataclass
class ModelConfig:
    name: str
    capabilities: List[ModelCapability]
    latency_target: float
    priority: str
    notes: Optional[str] = None

class ModelManager:
    def __init__(self):
        self.models = {
            'chat': {
                'pixtral-large-latest': ModelConfig(
                    name="pixtral-large-latest",
                    capabilities=[ModelCapability.VISION, ModelCapability.TEXT],
                    latency_target=0.39,
                    priority="high"
                ),
                'open-mixtral-8x22b': ModelConfig(
                    name="open-mixtral-8x22b",
                    capabilities=[ModelCapability.TEXT],
                    latency_target=0.27,
                    priority="high",
                    notes="Best Performance"
                )
            },
            'embedding': {
                'mistral-embed': ModelConfig(
                    name="mistral-embed",
                    capabilities=[ModelCapability.EMBEDDING],
                    latency_target=0.19,
                    priority="high",
                    notes="Fastest embedding model"
                )
            }
        }

    def get_model(self, model_type: str, model_name: str) -> Optional[ModelConfig]:
        return self.models.get(model_type, {}).get(model_name)

    def get_fastest_model(self, capability: ModelCapability) -> Optional[ModelConfig]:
        fastest = None
        fastest_latency = float('inf')

        for category in self.models.values():
            for model in category.values():
                if capability in model.capabilities:
                    if model.latency_target < fastest_latency:
                        fastest = model
                        fastest_latency = model.latency_target

        return fastest
```

## Performance Monitoring

```python
from prometheus_client import Histogram, Counter
from typing import Dict, Any

class ModelMetrics:
    def __init__(self):
        self.latency = Histogram(
            'sk_model_latency_seconds',
            'Model inference latency in seconds',
            ['model_name', 'capability'],
            buckets=[0.1, 0.19, 0.27, 0.33, 0.39, 0.5]
        )

        self.requests = Counter(
            'sk_model_requests_total',
            'Total number of model requests',
            ['model_name', 'capability']
        )

        self.errors = Counter(
            'sk_model_errors_total',
            'Total number of model errors',
            ['model_name', 'capability', 'error_type']
        )

class ModelMonitor:
    def __init__(self):
        self.metrics = ModelMetrics()
        self.model_manager = ModelManager()

    async def monitor_inference(self, model_name: str, capability: str):
        model = self.model_manager.get_model('chat', model_name)
        if not model:
            model = self.model_manager.get_model('embedding', model_name)

        if not model:
            raise ValueError(f"Unknown model: {model_name}")

        async with self.measure_latency(model_name, capability):
            self.metrics.requests.labels(
                model_name=model_name,
                capability=capability
            ).inc()

            # Your inference code here
            pass

    async def measure_latency(self, model_name: str, capability: str):
        import time
        start = time.time()
        try:
            yield
        finally:
            duration = time.time() - start
            self.metrics.latency.labels(
                model_name=model_name,
                capability=capability
            ).observe(duration)
```

## Health Checks

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List

@dataclass
class ModelHealth:
    status: str
    latency: float
    error_rate: float
    last_check: datetime

class HealthChecker:
    def __init__(self):
        self.model_manager = ModelManager()
        self.check_interval = 300  # 5 minutes

    async def check_model_health(self, model_name: str) -> ModelHealth:
        try:
            # Perform health check
            latency = await self.measure_latency(model_name)
            error_rate = await self.get_error_rate(model_name)

            status = "healthy" if self._is_healthy(latency, error_rate) else "unhealthy"

            return ModelHealth(
                status=status,
                latency=latency,
                error_rate=error_rate,
                last_check=datetime.utcnow()
            )
        except Exception as e:
            return ModelHealth(
                status="error",
                latency=float('inf'),
                error_rate=1.0,
                last_check=datetime.utcnow()
            )

    def _is_healthy(self, latency: float, error_rate: float) -> bool:
        return latency <= 0.5 and error_rate <= 0.01
```

## Alert Configuration

```yaml
groups:
  - name: model_alerts
    rules:
      - alert: ModelHighLatency
        expr: sk_model_latency_seconds > 0.39
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: High model latency detected
          description: Model {{ $labels.model_name }} latency above threshold

      - alert: ModelErrorSpike
        expr: rate(sk_model_errors_total[5m]) > 0.01
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: High model error rate detected
          description: Model {{ $labels.model_name }} error rate above threshold
```

## Usage Example

```python
async def process_inference(model_name: str, input_data: Dict[str, Any]):
    monitor = ModelMonitor()
    health_checker = HealthChecker()

    # Check model health
    health = await health_checker.check_model_health(model_name)
    if health.status != "healthy":
        raise RuntimeError(f"Model {model_name} is unhealthy")

    # Process inference with monitoring
    async with monitor.monitor_inference(model_name, "text"):
        # Your inference code here
        pass
```

## Support Channels

- API Issues: llm-oncall@company.com
- Performance: llm-ops@company.com
- General: llm-support@company.com

## Monitoring Channels

- Daily Status: #llm-status
- Weekly Performance: #llm-metrics
- Monthly Infrastructure: #llm-infra

---

Last Updated: 2024-12-15
Version: 1.0.0
Classification: INTERNAL USE ONLY
