# unpack

**Category:** Web | **Points:** 500

## Description

A web application that lets you upload ZIP archives and download the extracted files. What could go wrong?

## Setup

```bash
docker compose up --build
```

Service available at `http://localhost:5000`.

## Challenge Structure

Flask web application with ZIP archive processing. Exposes an upload endpoint (`/upload`, POST) that extracts submitted archives into a per-upload temporary directory, and a download endpoint (`/download/<token>/<path>`, GET) to retrieve individual extracted files. Includes a simple HTML upload interface.
