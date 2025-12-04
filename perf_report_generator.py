from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

@dataclass
class BenchTable:
    name: str
    results: list[BenchmarkResult]


@dataclass
class BenchmarkResult:
    name: str
    profile: str
    scenario: str
    backend: str
    target: str
    change: float
    sig_threshold: float
    sig_factor: float

    @staticmethod
    def parse_from_row(raw_row: list[str]) -> BenchmarkResult:
        return BenchmarkResult(
            name=raw_row[1],
            profile=raw_row[2],
            scenario=raw_row[3],
            backend=raw_row[4],
            target=raw_row[5],
            change=BenchmarkResult.parse_number(raw_row[6]),
            sig_threshold=BenchmarkResult.parse_number(raw_row[7]),
            sig_factor=BenchmarkResult.parse_number(raw_row[8]),
        )

    @staticmethod
    def parse_number(s: str) -> float:
        return float(s[:-1])


def download_benchmarks_data(first_sha: str, second_sha: str, stat: str, tab: str) -> list[BenchTable]:
    url = construct_query_url(first_sha, second_sha, stat, tab)
    browser = dowload_url(url)

    return parse_benchmark_tables(browser)


def construct_query_url(first_sha: str, second_sha: str, stat: str, tab: str):
    base_url = 'https://perf.rust-lang.org/compare.html?'

    def add_query_param(base_url: str, key: str, value: str) -> str:
        return base_url + f'{key}={value}&'

    base_url = add_query_param(base_url, 'start', first_sha)
    base_url = add_query_param(base_url, 'end', second_sha)
    base_url = add_query_param(base_url, 'stat', stat)
    base_url = add_query_param(base_url, 'tab', tab)

    return base_url


def dowload_url(url: str) -> WebDriver:
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    browser = webdriver.Chrome(options=chrome_options)
    browser.get(url)

    import time
    time.sleep(5)

    return browser


def parse_benchmark_tables(browser: WebDriver) -> list[BenchTable]:
    elem = browser.find_element(value = "app")
    tables = elem.find_elements(By.CLASS_NAME, "bench-table")

    bench_tables = []
    for table in tables:
        table_id = table.get_attribute('id')
        try:
            table_body = table.find_element(By.TAG_NAME, 'tbody')
            rows = table_body.find_elements(By.TAG_NAME, 'tr')

            bench_results = []

            for row in rows:
                cols = row.find_elements(By.TAG_NAME, 'td')
                raw_row = list(map(lambda c: c.text, cols))
                bench_results.append(BenchmarkResult.parse_from_row(raw_row))

            bench_tables.append(BenchTable(
                name=table_id,
                results=bench_results
            ))
        except Exception as ex:
            print(ex)
            print(f'Table {table_id} does not contain results')
        
    return bench_tables


print(download_benchmarks_data(
    '0f6dae4afc8959262e7245fddfbdfc7a1de6f34a',
    '80d8f292d82d735f83417221dd63b0dd2bbb8dd2',
    'instructions:u',
    'compile'
))
