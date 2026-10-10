# agentish-challenges

This repo contains the agentish-based CTF challenges designed for the 2026 iCTF.

### Standard structure

- Each challenge lives under `challenges/<challenge-id>/`.
- Check `challenges/FORMAT.md` for the expected format.

### Shared stub services (for local/dev)

This repo includes reusable **stub containers** for shared infrastructure that is typically provided externally in production:

- **`stubs/langfuse_stub`**: minimal HTTP stub
- **`stubs/sandbox_stub`**: minimal “sandbox runner” that executes a mounted Python file

For LiteLLM in local/dev, challenges can use `stubs/litellm_stub` (a lightweight OpenAI-compatible stub backed by the LiteLLM SDK).

Challenges can reference these stubs from their `docker-compose.yml` so future challenges reuse the same images. See `stubs/README.md`.

### Reference challenge

See `challenges/where-is-waldo/`.

### Large files (S3)

Challenge files over ~50 MB (binaries, datasets, disk images) should not be committed to git. Upload them to S3 instead:

```bash
pip install boto3
python upload_challenge_data.py <challenge-name> <file-or-directory>
```

Files are publicly accessible at `https://ictf-challenge-data.s3.us-west-2.amazonaws.com/<challenge-name>/<filename>`.

In Dockerfiles, pull them at build time:
```dockerfile
ADD https://ictf-challenge-data.s3.us-west-2.amazonaws.com/my-challenge/data.bin /data/
```

