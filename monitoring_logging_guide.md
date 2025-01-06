# Semantic Kernel Monitoring and Logging Guide

## Centralized Logging Configuration

```python
import logging
import logging.config
from pathlib import Path
from typing import Dict, Any

class LoggingManager:
    def __init__(self):
        self.config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'json': {
                    'class': 'pythonjsonlogger.jsonlogger.JsonFormatter',
                    'format': '%(asctime)s %(levelname)s %(name)s %(message)s'
                },
                'standard': {
                    'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
                }
            },
            'handlers': {
                'file': {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'filename': '/logs/semantic-kernel/service.log',
                    'maxBytes': 10485760,
                    'backupCount': 5,
                    'formatter': 'json',
                    'level': 'INFO'
                },
                'error_file': {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'filename': '/logs/semantic-kernel/error.log',
                    'maxBytes': 10485760,
                    'backupCount': 5,
                    'formatter': 'json',
                    'level': 'ERROR'
                },
                'console': {
                    'class': 'logging.StreamHandler',
                    'formatter': 'standard',
                    'level': 'INFO'
                }
            },
            'loggers': {
                '': {
                    'handlers': ['console', 'file', 'error_file'],
                    'level': 'INFO',
                    'propagate': True
                }
            }
        }

    def setup(self):
        log_dir = Path('/logs/semantic-kernel')
        log_dir.mkdir(parents=True, exist_ok=True)
        logging.config.dictConfig(self.config)
```

## Prometheus Metrics Configuration

```python
from prometheus_client import Counter, Histogram, Gauge, start_http_server
from typing import Dict

class MetricsManager:
    def __init__(self, port: int = 9090):
        self.port = port

        # Request metrics
        self.request_counter = Counter(
            'sk_requests_total',
            'Total requests processed',
            ['method', 'endpoint']
        )

        self.request_latency = Histogram(
            'sk_request_duration_seconds',
            'Request duration in seconds',
            ['method', 'endpoint'],
            buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
        )

        # Error metrics
        self.error_counter = Counter(
            'sk_errors_total',
            'Total errors encountered',
            ['type', 'service']
        )

        # Resource metrics
        self.memory_gauge = Gauge(
            'sk_memory_usage_bytes',
            'Current memory usage in bytes'
        )

        self.cpu_gauge = Gauge(
            'sk_cpu_usage_percent',
            'Current CPU usage percentage'
        )

        # LLM specific metrics
        self.model_latency = Histogram(
            'sk_model_inference_seconds',
            'Model inference duration in seconds',
            ['model_name'],
            buckets=[0.1, 0.2, 0.33, 0.5, 1.0]
        )

    def start(self):
        start_http_server(self.port)
```

## Alert Manager Configuration

```yaml
alertmanager:
  config:
    global:
      resolve_timeout: 5m
      slack_api_url: "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"

    route:
      group_by: ["alertname", "service"]
      group_wait: 30s
      group_interval: 5m
      repeat_interval: 4h
      receiver: "slack-notifications"

    receivers:
      - name: "slack-notifications"
        slack_configs:
          - channel: "#nova-alerts"
            send_resolved: true
            title: '{{ template "slack.title" . }}'
            text: '{{ template "slack.text" . }}'

    templates:
      - "/etc/alertmanager/templates/*.tmpl"
```

## Alert Rules Configuration

```yaml
groups:
  - name: semantic_kernel_alerts
    rules:
      - alert: HighLatency
        expr: sk_request_duration_seconds > 0.33
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: High latency detected
          description: Request duration above threshold of 0.33s

      - alert: HighErrorRate
        expr: rate(sk_errors_total[5m]) > 0.01
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: High error rate detected
          description: Error rate above 1% threshold

      - alert: HighMemoryUsage
        expr: sk_memory_usage_bytes > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: High memory usage
          description: Memory usage above 85%

      - alert: HighCPUUsage
        expr: sk_cpu_usage_percent > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: High CPU usage
          description: CPU usage above 80%
```

## Monitoring Integration Example

```python
import time
from contextlib import contextmanager

class MonitoringIntegration:
    def __init__(self):
        self.logging_manager = LoggingManager()
        self.metrics_manager = MetricsManager()
        self.logger = logging.getLogger(__name__)

    def initialize(self):
        self.logging_manager.setup()
        self.metrics_manager.start()

    @contextmanager
    def monitor_request(self, method: str, endpoint: str):
        start_time = time.time()
        try:
            yield
            duration = time.time() - start_time
            self.metrics_manager.request_counter.labels(
                method=method,
                endpoint=endpoint
            ).inc()
            self.metrics_manager.request_latency.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)
        except Exception as e:
            self.metrics_manager.error_counter.labels(
                type=type(e).__name__,
                service='semantic-kernel'
            ).inc()
            self.logger.error(f"Request failed: {str(e)}", exc_info=True)
            raise

    def record_model_inference(self, model_name: str, duration: float):
        self.metrics_manager.model_latency.labels(
            model_name=model_name
        ).observe(duration)
```

## Usage Example

```python
# Initialize monitoring
monitoring = MonitoringIntegration()
monitoring.initialize()

# Monitor API requests
@app.route('/v1/semantic-kernel/infer', methods=['POST'])
def infer():
    with monitoring.monitor_request(method='POST', endpoint='/infer'):
        # Process request
        start_time = time.time()
        result = process_inference(request.json)
        duration = time.time() - start_time

        # Record model inference time
        monitoring.record_model_inference(
            model_name=request.json['model'],
            duration=duration
        )

        return jsonify(result)
```

## Monitoring Dashboard Layout

```ascii
┌──────────────────┐ ┌──────────────────┐
│   Request Rate   │ │   Error Rate     │
│                  │ │                  │
└──────────────────┘ └──────────────────┘
┌──────────────────┐ ┌──────────────────┐
│  Latency (p95)   │ │   Memory Usage   │
│                  │ │                  │
└──────────────────┘ └──────────────────┘
┌──────────────────┐ ┌──────────────────┐
│   CPU Usage      │ │  Model Latency   │
│                  │ │                  │
└──────────────────┘ └──────────────────┘
```

## Performance Thresholds

- Request Latency: < 0.33s (p95)
- Error Rate: < 0.1%
- Memory Usage: < 85%
- CPU Usage: < 80%
- Model Inference: < 0.33s
- Log Volume: < 10GB/day

---

Last Updated: 2024-12-15
Version: 1.0.0
Classification: INTERNAL USE ONLY
