import pandas as pd
import os
import s3fs
import pyarrow.parquet as pq
import pyarrow as pa


df = pd.read_parquet('logs_2023-10-19.parquet', engine='pyarrow')
df["date"] = df.timestamp.dt.date
table = pa.Table.from_pandas(df)


def write_parquet_as_partitioned_dataset(table, bucket_name, path, basename_template: str = "daily_logs_{i}.parquet", partition_cols=None, compression="SNAPPY"):
    url = f"https://{os.getenv('AWS_S3_ENDPOINT')}"
    fs = s3fs.S3FileSystem(client_kwargs={'endpoint_url': url})
    file_uri = f"{bucket_name}/{path}"
    pq.write_to_dataset(table, root_path=file_uri, partition_cols=partition_cols, filesystem=fs, basename_template=basename_template, compression=compression)


write_parquet_as_partitioned_dataset(table, bucket_name="projet-ape", path="log_files/dashboard", partition_cols=["date"])
