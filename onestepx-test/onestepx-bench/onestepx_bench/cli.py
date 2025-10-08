import click
from . import benchmarks

@click.group()
def main():
    pass

@main.command()
@click.option('--driver', required=True)
@click.option('--n', default=1000, type=int)
def latency(driver, n):
    benchmarks.run_latency_benchmark(driver, n)

@main.command()
@click.option('--driver', required=True)
@click.option('--duration', default=5, type=int)
def qps(driver, duration):
    benchmarks.run_qps_benchmark(driver, duration)

@main.command()
@click.option('--driver', required=True)
@click.option('--warm-eps', default=3000, type=int)
@click.option('--warm-s', default=5, type=int)
@click.option('--burst-eps', default=50000, type=int)
@click.option('--burst-s', default=10, type=int)
@click.option('--readers', default=12, type=int)
def burst(driver, warm_eps, warm_s, burst_eps, burst_s, readers):
    benchmarks.run_burst_benchmark(driver, warm_eps, warm_s, burst_eps, burst_s, readers)

@main.command()
@click.option('--driver', required=True)
@click.option('--duration', default=600, type=int)
@click.option('--eps', default=3000, type=int)
@click.option('--readers', default=12, type=int)
@click.option('--sample-every', default=5, type=int)
def long(driver, duration, eps, readers, sample_every):
    benchmarks.run_long_benchmark(driver, duration, eps, readers, sample_every)

if __name__ == "__main__":
    main()
