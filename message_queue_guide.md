# Semantic Kernel Message Queue Configuration Guide

## Core Architecture

```ascii
┌─────────────────┐
│   Meta Router   │
│    (Central)    │
└───────┬─────────┘
        │
┌───────┴────────┐
│    RabbitMQ    │
│  Message Broker │
└────────────────┘
```

## Exchange Configuration

```python
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class ExchangeConfig:
    name: str
    type: str
    routing_pattern: str
    durable: bool = True
    auto_delete: bool = False

class ExchangeManager:
    def __init__(self):
        self.exchanges = {
            'pattern_events': ExchangeConfig(
                name='nova.pattern.events',
                type='topic',
                routing_pattern='pattern.#'
            ),
            'field_status': ExchangeConfig(
                name='nova.field.status',
                type='topic',
                routing_pattern='field.#'
            ),
            'system_health': ExchangeConfig(
                name='meta-router.health',
                type='topic',
                routing_pattern='#'
            )
        }

    def get_exchange_config(self, name: str) -> ExchangeConfig:
        return self.exchanges.get(name)
```

## Queue Configuration

```python
@dataclass
class QueueConfig:
    name: str
    binding_pattern: str
    durable: bool = True
    arguments: Dict = None

class QueueManager:
    def __init__(self):
        self.queues = {
            'pattern_queue': QueueConfig(
                name='nova.pattern.queue',
                binding_pattern='pattern.#',
                arguments={
                    'x-message-ttl': 30000,
                    'x-dead-letter-exchange': 'dlx'
                }
            ),
            'field_queue': QueueConfig(
                name='nova.field.queue',
                binding_pattern='field.#',
                arguments={
                    'x-message-ttl': 30000,
                    'x-dead-letter-exchange': 'dlx'
                }
            ),
            'monitoring': QueueConfig(
                name='nova.monitoring',
                binding_pattern='#',
                arguments={
                    'x-message-ttl': 30000
                }
            )
        }

    def get_queue_config(self, name: str) -> QueueConfig:
        return self.queues.get(name)
```

## Connection Management

```python
import pika
from typing import Optional

class RabbitMQConnection:
    def __init__(self):
        self.host = 'localhost'
        self.port = 5672
        self.connection = None
        self.channel = None

    def connect(self) -> bool:
        try:
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=self.host,
                    port=self.port
                )
            )
            self.channel = self.connection.channel()
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False

    def close(self):
        if self.channel:
            self.channel.close()
        if self.connection:
            self.connection.close()
```

## Health Monitoring

```python
import subprocess
from typing import Dict

class MessageQueueHealth:
    def __init__(self):
        self.services = ['rabbitmq-server', 'meta-router']

    def check_service_status(self) -> Dict[str, str]:
        status = {}
        for service in self.services:
            try:
                result = subprocess.run(
                    ['systemctl', 'is-active', service],
                    capture_output=True,
                    text=True
                )
                status[service] = result.stdout.strip()
            except Exception as e:
                status[service] = f"error: {str(e)}"
        return status

    def verify_connections(self) -> Dict[str, bool]:
        try:
            result = subprocess.run(
                ['rabbitmqctl', 'list_connections'],
                capture_output=True,
                text=True
            )
            return {
                'status': True,
                'connections': result.stdout.strip()
            }
        except Exception as e:
            return {
                'status': False,
                'error': str(e)
            }
```

## Usage Example

```python
# Initialize managers
exchange_manager = ExchangeManager()
queue_manager = QueueManager()
connection = RabbitMQConnection()
health_monitor = MessageQueueHealth()

# Connect to RabbitMQ
if connection.connect():
    # Setup exchanges
    for exchange in exchange_manager.exchanges.values():
        connection.channel.exchange_declare(
            exchange=exchange.name,
            exchange_type=exchange.type,
            durable=exchange.durable
        )

    # Setup queues
    for queue in queue_manager.queues.values():
        connection.channel.queue_declare(
            queue=queue.name,
            durable=queue.durable,
            arguments=queue.arguments
        )

    # Create bindings
    for queue in queue_manager.queues.values():
        connection.channel.queue_bind(
            exchange=exchange_manager.exchanges['pattern_events'].name,
            queue=queue.name,
            routing_key=queue.binding_pattern
        )
```

## Quick Commands

```bash
# Service Management
sudo systemctl start rabbitmq-server
sudo systemctl start meta-router

# Status Verification
sudo systemctl status rabbitmq-server
sudo systemctl status meta-router

# Queue Management
sudo rabbitmqctl list_exchanges
sudo rabbitmqctl list_queues
sudo rabbitmqctl list_bindings
```

## System Configuration

### Port Configuration

- RabbitMQ: 5672
- Management Interface: 15672
- Management URL: http://localhost:15672

### File Paths

- Config: `/data/ax/CommOps/rabbitmq/config/`
- Logs: `/data/ax/CommOps/rabbitmq/logs/`
- Scripts: `/data/ax/CommOps/rabbitmq/scripts/`

## Support Channels

### Primary Support

- Slack: #nova-rmq-support
- Email: rmq-support@acumen.local
- Documentation: http://docs.commops.local/rmq

### Emergency Contacts

- On-call: oncall@acumen.local
- Emergency: emergency@acumen.local
- Phone: 555-0123

## Troubleshooting

### Common Issues

1. Service Won't Start

```bash
sudo systemctl restart rabbitmq-server
```

2. Connection Failed

```bash
sudo rabbitmqctl status
```

3. Queue Issues

```bash
sudo rabbitmqctl list_queues
```

## Health Check Script

```python
def verify_rmq_health():
    health_monitor = MessageQueueHealth()

    # Check service status
    service_status = health_monitor.check_service_status()
    if not all(status == 'active' for status in service_status.values()):
        return False, "Service not active"

    # Check connections
    connection_status = health_monitor.verify_connections()
    if not connection_status['status']:
        return False, connection_status['error']

    return True, "All systems operational"
```

---

Last Updated: 2024-12-15
Version: 1.0.0
Classification: INTERNAL USE ONLY
