"""GCS Files Endpoints - Browse and download cloud storage."""

from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from google.cloud import storage
import os
from typing import Optional
import io

router = APIRouter()

GCS_BUCKET = os.getenv("GCS_BUCKET", "elements-archive-2026")


@router.get("/list")
def list_files(
    path: str = Query("", description="Subdirectory path"),
    limit: int = Query(100, ge=1, le=1000)
):
    """List files in GCS bucket."""

    try:
        client = storage.Client()
        bucket = client.bucket(GCS_BUCKET)

        # List blobs with prefix
        blobs = list(bucket.list_blobs(prefix=path, max_results=limit))

        files = []
        total_size = 0

        for blob in blobs:
            # Skip directories
            if blob.name.endswith('/'):
                continue

            size = blob.size or 0
            total_size += size

            files.append({
                "name": blob.name.split('/')[-1],
                "path": blob.name,
                "size_bytes": size,
                "size_human": _format_bytes(size),
                "created": blob.time_created.isoformat() if blob.time_created else None,
                "updated": blob.updated.isoformat() if blob.updated else None,
                "download_url": f"/api/files/download?file={blob.name}"
            })

        return {
            "bucket": GCS_BUCKET,
            "path": path,
            "files": files,
            "total_count": len(files),
            "total_size_bytes": total_size,
            "total_size_human": _format_bytes(total_size)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download")
def download_file(file: str = Query(..., description="File path in bucket")):
    """Download file from GCS."""

    try:
        client = storage.Client()
        bucket = client.bucket(GCS_BUCKET)
        blob = bucket.blob(file)

        if not blob.exists():
            raise HTTPException(status_code=404, detail=f"File not found: {file}")

        # Download to memory
        content = blob.download_as_bytes()

        # Determine content type
        content_type = blob.content_type or "application/octet-stream"

        return StreamingResponse(
            io.BytesIO(content),
            media_type=content_type,
            headers={
                "Content-Disposition": f'attachment; filename="{blob.name.split("/")[-1]}"'
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload")
def upload_file(
    path: str = Query(..., description="Destination path"),
    file: UploadFile = File(...)
):
    """Upload file to GCS."""

    try:
        client = storage.Client()
        bucket = client.bucket(GCS_BUCKET)
        blob = bucket.blob(path)

        # Upload
        blob.upload_from_file(file.file, content_type=file.content_type)

        return {
            "uploaded": True,
            "path": path,
            "size_bytes": blob.size,
            "url": f"gs://{GCS_BUCKET}/{path}"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _format_bytes(size: int) -> str:
    """Format bytes to human-readable."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"
