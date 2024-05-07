from prometheus_client import start_http_server, Gauge
import psutil
import uuid, time

# Create Gauge metrics to track system resources
system_uuid_metric = Gauge('system_uuid', 'UUID of the system', ['uuid'])

total_ram = Gauge('system_total_ram', 'Total RAM in megabytes')
available_ram = Gauge('system_available_ram', 'Available RAM in megabytes')

total_cpu = Gauge('system_total_cpu', 'Total CPU usage')
available_cpu = Gauge('system_available_cpu', 'Available CPU usage')

total_hdd = Gauge('system_total_hdd', 'Total HDD space in gigabytes')
available_hdd = Gauge('system_available_hdd', 'Available HDD space in gigabytes')

def fetch_system_metrics():
    """Fetch system metrics and update the Prometheus metrics."""

    # ID metrics
    if not system_uuid_metric.collect()[0].samples:  # Check if the metric is not already set
        system_uuid = str(uuid.uuid4())
        system_uuid_metric.labels(uuid=system_uuid).set(1)  # Set the metric to 1 for the given UUID

    # RAM metrics
    mem = psutil.virtual_memory()
    total_ram.set(mem.total / 1024 / 1024)  # Convert from bytes to megabytes
    available_ram.set(mem.available / 1024 / 1024)

    # CPU metrics
    cpu_count = psutil.cpu_count()
    total_cpu.set(cpu_count)
    cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
    available_cpu.set(cpu_count - sum(cpu_percent) / 100)

    # Disk metrics
    disk_usage = psutil.disk_usage('/')
    total_hdd.set(disk_usage.total / (1024 * 1024 * 1024))  # Convert from bytes to gigabytes
    available_hdd.set((disk_usage.total - disk_usage.used) / (1024 * 1024 * 1024))

def main():
    """Start up the server to expose the metrics."""
    start_http_server(8000)  # Port where metrics are exposed
    print("Metrics server running on http://localhost:8000")

    # Update the metric every 5 seconds
    while True:
        fetch_system_metrics()
        time.sleep(5)

if __name__ == '__main__':
    main()