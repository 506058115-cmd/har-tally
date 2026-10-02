# har-tally

Summarize a browser-exported HAR file without printing URLs, headers, cookies, or request/response bodies. It reports only aggregate counts for common methods, HTTP status classes, and media type families.

Requires Python 3.8+ and uses only the standard library. Input is limited to 32 MiB.

~~~sh
python har_tally.py browser.har
~~~

The summary contains the number of entries, incomplete entries, method buckets, status classes, and media type families. Unknown methods and media types are grouped as `OTHER`/`other`. A HAR entry with missing or invalid request or response fields is counted as incomplete; valid entries are still summarized.

HAR files can contain private browsing data. This tool processes the selected file locally and does not display its URLs, headers, cookies, or bodies. The output is an aggregate summary, not a complete HAR validation. See the [HAR 1.2 overview](https://w3c.github.io/web-performance/specs/HAR/Overview.html) for the format structure.

Exit status: `0` when entries are complete, `1` when at least one entry is incomplete, `2` when the file cannot be read or is not valid HAR-shaped JSON.

## Linux x86_64 downloads

- [Single-file build](https://github.com/506058115-cmd/har-tally/releases/download/v1.0.0/har-tally-linux-x86_64-onefile.tar.gz)
- [Directory build](https://github.com/506058115-cmd/har-tally/releases/download/v1.0.0/har-tally-linux-x86_64-onedir.tar.gz)
- [v1.0.0 release](https://github.com/506058115-cmd/har-tally/releases/tag/v1.0.0)

Archives include build information and dependency licenses; the Release includes SHA-256 checksums. Built in WSL Ubuntu 24.04 (Python 3.12.3, PyInstaller 6.22.2) for GNU/Linux x86_64. Older Linux distributions may require a compatible glibc. The packaged executable has not been run for functional validation.

## License

MIT. See [LICENSE](LICENSE).
