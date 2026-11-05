import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from lxml import etree

# Folder and XPath settings
FOLDER = Path(r"C:\Users\ZaricJ\Downloads\Lobster Profile Export\ProfileExportEcht")
XPATH_EXPRESSION = "/datawizardprofile/responsesettings/responseunits/unit_file/description/text()"  # example: change to what you search
PARSER = etree.XMLParser(recover=True, huge_tree=True)

def process_file(file: Path):
    """Parse and count XPath matches."""
    try:
        tree = etree.parse(str(file), parser=PARSER)
        return len(tree.xpath(XPATH_EXPRESSION))
    except Exception as e:
        print(f"Error in {file.name}: {e}")
        return 0


# --- Benchmark runners ---
def sequential(files):
    total = 0
    for f in files:
        total += process_file(f)
    return total

def threaded(files):
    with ThreadPoolExecutor() as pool:
        return sum(pool.map(process_file, files))

def processed(files):
    with ProcessPoolExecutor() as pool:
        return sum(pool.map(process_file, files))

def benchmark(func, files):
    start = time.perf_counter()
    result = func(files)
    end = time.perf_counter()
    print(f"{func.__name__:>12} → {end - start:6.2f} s, found {result} matches")


# --- Main benchmark ---
if __name__ == "__main__":
    files = list(FOLDER.glob("*.xml"))
    print(f"Benchmarking {len(files)} XML files...\n")

    benchmark(sequential, files)
    benchmark(threaded, files)
    benchmark(processed, files)
    print("\nBenchmark complete.")