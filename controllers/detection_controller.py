from fastapi import UploadFile, Form, HTTPException
import cloudinary
import cloudinary.uploader
import io
from ultralytics import YOLO
import tempfile
import cv2
import os
import numpy as np


cloudinary.config(
    cloud_name="dfsozazph",
    api_key="957981467851439",
    api_secret="2m2EanObqtrcCkvxxmprwpl9Fis",
    secure=True
)


model = YOLO("lib/model-yolo/best.pt")


class DetectionController:

    @staticmethod
    async def detection_image(
        image: UploadFile,
        latitude: float = Form(...),
        longitude: float = Form(...),
    ):
        try:
            # --- Baca file UploadFile jadi array ---
            contents = await image.read()
            file_bytes = np.frombuffer(contents, np.uint8)
            img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

            # --- Jalankan deteksi ---
            results = model(img)

            # Ambil gambar hasil dengan bounding box
            annotated = results[0].plot()
            text = f"Lat: {latitude:.4f}, Long: {longitude:.4f}"

            # Tentukan posisi dan properti teks
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.8
            color = (0, 0, 255)  # Merah (Red)
            thickness = 2

            # Dapatkan ukuran teks untuk penempatan yang tepat
            (text_width, text_height), _ = cv2.getTextSize(
                text, font, font_scale, thickness)

            # Tempatkan teks di pojok kiri bawah gambar
            org = (10, annotated.shape[0] - 10)  # 10 pixels dari kiri & bawah

            # Gambar teks di atas gambar hasil deteksi
            cv2.putText(annotated, text, org, font, font_scale,
                        color, thickness, cv2.LINE_AA)

            # Simpan sementara ke file
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmpfile:
                cv2.imwrite(tmpfile.name, annotated)
                temp_path = tmpfile.name

            # Upload hasil ke Cloudinary
            upload_result = cloudinary.uploader.upload(
                temp_path,
                folder="detection-images",
                context={"latitude": latitude, "longitude": longitude}
            )

            # Hapus file lokal
            os.remove(temp_path)

            return {
                "success": True,
                "url": upload_result.get("secure_url"),
                "public_id": upload_result.get("public_id"),
                "latitude": latitude,
                "longitude": longitude
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
