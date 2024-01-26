import os
import re
import sys
import yaml
import json
import exrex
import httpx
import asyncio
import argparse
import tempfile
import http.client
from tqdm import tqdm
from datetime import datetime
import concurrent.futures
import aiofiles
import aiohttp

class Interface:
    @staticmethod
    def get_tempdir():
        timestamp = datetime.now().timestamp()
        temp_dir = tempfile.mkdtemp()
        return timestamp, temp_dir

    @staticmethod
    async def write_yaml(data, path=None, encoding='utf-8'):
        async with aiofiles.open(path, 'w', encoding=encoding) as f:
            await f.write(yaml.dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True))

    @staticmethod
    async def update_yaml(new_data, path=None, encoding='utf-8'):
        existing_data = {}
        try:
            if path:
                async with aiofiles.open(path, 'r', encoding=encoding) as f:
                    existing_data = yaml.safe_load(await f.read())
        except FileNotFoundError:
            pass

        existing_data.update(new_data)

        if path:
            async with aiofiles.open(path, 'w', encoding=encoding) as f:
                await f.write(yaml.dump(existing_data, default_flow_style=False, sort_keys=True, allow_unicode=True))
        else:
            return existing_data

async def generate_ord(p, limit):
    print(f'Count: {exrex.count(p, limit=limit)}')
    print(f'Range limit: {limit}')
    return '\n'.join(exrex.generate(p, limit=limit))

async def generate_rand(p, limit):
    return exrex.getone(p, limit=limit)

async def generate_urls(p, tmpf, count, limit, sort, interval):
    try:
        async with aiofiles.open(tmpf, "w") as file:
            if sort == ['natural']:
                url = await generate_ord(p, limit)
                await file.write(url + "\n")
            else:
                for _ in tqdm(range(count), desc="Generating"):
                    try:
                        url = await generate_rand(p, limit)
                        await file.write(url + "\n")
                    except Exception as e:
                        print(f"Error generating URL: {e}")
                    await asyncio.sleep(interval)
    except KeyboardInterrupt:
        print("\nGeneration interrupted. Partial results saved.")
    except Exception as e:
        print(f"Error during generation: {e}")

async def check_valid_url(url, log_dict, interval, timeout, content_subdir, download, i, pbar):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.head(url, timeout=timeout, follow_redirects=True)
            print(f"[{response.status_code}]: {url}", end="\r")

            log_entry = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "url": url
            }

            if 300 <= response.status_code < 400 and 'location' in response.headers:
                # Handle redirects
                redirect_url = response.headers['location']
                log_entry['redirect_url'] = redirect_url
                log_dict[i] = log_entry
                await download_contents(redirect_url, content_subdir)
            else:
                # Handle non-redirect cases
                log_dict[i] = log_entry
                if download and response.status_code == 200:
                    await download_contents(url, content_subdir)

    except httpx.RequestError as e:
        print(f"Error while checking {url}: {e}", end="\r")
        log_entry = {
            "error": f"Error while checking {url}: {e}",
            "url": url
        }
        log_dict[i] = log_entry
    except Exception as e:
        print(f"Unknown error while checking {url}: {e}", end="\r")
        log_entry = {
            "error": f"Unknown error while checking {url}: {e}",
            "url": url
        }
        log_dict[i] = log_entry
    finally:
        pbar.update(1)

async def check_valid_urls_parallel(urls, log_file_path, interval, timeout, content_subdir, download):
    log_dict = {}
    pbar = tqdm(total=len(urls), desc="Checking Validity", leave=False)
    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        tasks = [
            loop.run_in_executor(
                executor,
                lambda: asyncio.run(
                    check_valid_url(url, log_dict, interval, timeout, content_subdir, download, i, pbar)
                )
            )
            for i, url in enumerate(urls, start=1)
        ]

        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            print(f"An error occurred in check_valid_urls_parallel: {e}")
        finally:
            pbar.close()
            await Interface.write_yaml(log_dict, log_file_path)
            print(f'Saved log at: {log_file_path}')
            print(f'Saved contents at: {content_subdir}')

def main():
    parser = argparse.ArgumentParser(description="Generate URLs with specified regex pattern and check their validity.")
    parser.usage = f"{sys.argv[0]} " + "[{gen,check,match}]  [-h] [-o OUTPUT_PATH] [-p PATTERN] [-c COUNT] [-l LIMIT] [-t TIMEOUT] [-I INTERVAL] [-s {natural,asc,desc,random}] [-d] [input_path [input_path ...]]"
    parser.add_argument('input_path', nargs='*', help='Input path for URLs. If not provided, read from stdin.')
    parser.add_argument("mode", nargs=1, choices=["gen", "check", "match"], default=["gen"], help="Mode: gen, check, or match (default: gen)")
    parser.add_argument("-o", "--output_path", default=None, help="Output path")
    parser.add_argument("-p", "--pattern", default="https://www\.example\.com/\d{7}", help="Regular expression pattern for generating random strings")
    parser.add_argument("-c", "--count", type=int, default=10, help="Max number of urls (default: 10) [WIP: only works in random]")
    parser.add_argument("-l", "--limit", type=int, default=1, help="Max string length range limit (default: 1)")
    parser.add_argument("-t", "--timeout", type=int, default=5, help="Timeout for HTTP requests (default: 5 seconds)")
    parser.add_argument("-I", "--interval", type=int, default=1, help="Interval between requests (default: 1 second)")
    parser.add_argument("-s", "--sort", nargs="+", choices=["natural", "asc", "desc","random"], default=["random"], help="Sort: generate, asc, or desc (default: random)")
    parser.add_argument("-d", "--download", action="store_true", help="Enable downloading contents for valid URLs (default: False)")

    args = parser.parse_args()
    ts, temp_dir = Interface.get_tempdir()
    temp_file = f'{temp_dir}/{ts}'

    if "gen" in args.mode:
        asyncio.run(generate_urls(args.pattern, temp_file, args.count, args.limit, args.sort, args.interval))
        print(f"Generated URLs are saved to: {temp_file}")

    if "check" in args.mode:
        log_dir = 'log'
        content_dir = "contents"
        os.makedirs(log_dir, exist_ok=True)
        os.makedirs(content_dir, exist_ok=True)
        log_file = f"{log_dir}/{ts}.yaml"
        content_subdir = f"{content_dir}/{ts}"
        if args.input_path:

            urls = args.input_path
        else:
            urls = sys.stdin.read().splitlines()
        asyncio.run(check_valid_urls_parallel(urls, log_file, args.interval, args.timeout, content_subdir, args.download))

    if "match" in args.mode:
        match_urls(args.input_path, args.pattern)

if __name__ == "__main__":
    main()
