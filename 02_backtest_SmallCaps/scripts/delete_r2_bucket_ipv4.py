from __future__ import annotations

import os
import socket
import sys
import time
from pathlib import Path

import boto3
from botocore.config import Config
from botocore.session import Session

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.core.settings import settings


def _force_ipv4() -> None:
    real_getaddrinfo = socket.getaddrinfo

    def force_ipv4(host, port, family=0, type=0, proto=0, flags=0):
        return real_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)

    socket.getaddrinfo = force_ipv4


def _clear_proxy_env() -> None:
    for key in (
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "ALL_PROXY",
        "http_proxy",
        "https_proxy",
        "all_proxy",
    ):
        os.environ.pop(key, None)
    os.environ["NO_PROXY"] = "*"
    os.environ.pop("AWS_PROFILE", None)
    os.environ.pop("AWS_DEFAULT_PROFILE", None)


def get_client():
    _clear_proxy_env()
    _force_ipv4()
    session = Session()
    cfg = Config(
        signature_version="s3v4",
        retries={"max_attempts": 2, "mode": "standard"},
        connect_timeout=10,
        read_timeout=30,
        s3={"addressing_style": "path"},
    )
    return boto3.Session(botocore_session=session).client(
        "s3",
        endpoint_url=settings.R2_ENDPOINT,
        aws_access_key_id=settings.R2_ACCESS_KEY_ID,
        aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
        region_name=settings.R2_REGION,
        config=cfg,
    )


def main() -> int:
    s3 = get_client()
    bucket = settings.R2_BUCKET
    deleted = 0
    batches = 0
    start = time.time()

    print(f"bucket={bucket}", flush=True)
    print(f"endpoint={settings.R2_ENDPOINT}", flush=True)

    while True:
        resp = s3.list_objects_v2(Bucket=bucket, MaxKeys=1000)
        objs = [{"Key": o["Key"]} for o in resp.get("Contents", [])]
        if not objs:
            print("No quedan objetos.", flush=True)
            break

        batches += 1
        out = s3.delete_objects(Bucket=bucket, Delete={"Objects": objs, "Quiet": True})
        batch_deleted = len(out.get("Deleted", []))
        batch_errors = len(out.get("Errors", []))
        deleted += batch_deleted

        print(
            f"batches={batches} borrados_total={deleted} "
            f"borrados_lote={batch_deleted} errores_lote={batch_errors} "
            f"elapsed_sec={time.time() - start:.0f}",
            flush=True,
        )

        if batch_deleted == 0 and batch_errors == 0:
            print("Sin progreso en el lote; se detiene para evitar bucle infinito.", flush=True)
            break

    check = s3.list_objects_v2(Bucket=bucket, MaxKeys=10)
    print(f"remaining={check.get('KeyCount', 0)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
