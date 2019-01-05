import glob
import os
import time
from concurrent.futures import ProcessPoolExecutor

import pandas as pd

SAFECAST_DATA_PATH = r"F:\safecast\measurements-out.csv"
CHUNKS_DIR = r"F:\safecast\chunks"
MERGED_CSV_FILENAME = r"F:\safecast\merged.csv"
ROWS_IN_CHUNK = 1000000
FIRST_CHUNK_NUMBER = 0
LAST_CHUNK_NUMBER = 108
MULTIPROCESSING_WORKERS = 4

COLUMNS_TO_DROP = ["location name", "device id", "md5sum", "height", "surface", "radiation", "uploaded time",
                   "loader id", "unit"]


def parse_chunk(chunk_number: int) -> int:
    start_time = time.time()
    rows_to_skip = list(range(1, chunk_number * ROWS_IN_CHUNK + 1))
    df = pd.read_csv(SAFECAST_DATA_PATH, skiprows=rows_to_skip, nrows=ROWS_IN_CHUNK)
    df = clean_up_df(df)
    df.to_csv(os.path.join(CHUNKS_DIR, f"{chunk_number}.csv"), index=False, header=chunk_number == 0)
    size = len(df.index)
    print(f'Chunk #{chunk_number} size: {size}, time: {time.time() - start_time} s')
    del df
    return size


def clean_up_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(str.lower, axis="columns")
    df["captured time"] = pd.to_datetime(df["captured time"], errors="coerce")
    df = df[df["captured time"].notna()]
    df = df[df["captured time"] <= pd.datetime.now()]
    df = df[df["unit"] == "cpm"]
    return df.drop(columns=COLUMNS_TO_DROP)


def merge_chunks() -> None:
    with open(MERGED_CSV_FILENAME, "w") as result_file:
        for filename in glob.glob(os.path.join(CHUNKS_DIR, "*.csv")):
            with open(filename) as chunk_file:
                result_file.write(chunk_file.read())


if __name__ == '__main__':
    if not os.path.exists(CHUNKS_DIR):
        os.makedirs(CHUNKS_DIR)
    with ProcessPoolExecutor(max_workers=MULTIPROCESSING_WORKERS) as pool:
        total_size = sum(pool.map(parse_chunk, range(FIRST_CHUNK_NUMBER, LAST_CHUNK_NUMBER)))
    print('total size', total_size)
    merge_chunks()
