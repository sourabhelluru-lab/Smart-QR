package com.example.demo;

import com.example.demo.models.TabletInfo;
import com.google.zxing.BarcodeFormat;
import com.google.zxing.WriterException;
import com.google.zxing.client.j2se.MatrixToImageWriter;
import com.google.zxing.common.BitMatrix;
import com.google.zxing.qrcode.QRCodeWriter;

import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;

import java.io.ByteArrayOutputStream;
import java.io.IOException;

@RestController
@CrossOrigin(origins = "*")
public class QrController {

    @PostMapping(value = "/generateQR", produces = MediaType.IMAGE_PNG_VALUE)
    public @ResponseBody byte[] generateQR(@RequestBody TabletInfo info)
            throws WriterException, IOException {

        String qrText =
                "Name: " + info.getName() +
                "\nDosage: " + info.getDosage() +
                "\nTiming: " + info.getTiming();

        QRCodeWriter qrCodeWriter = new QRCodeWriter();
        BitMatrix bitMatrix =
                qrCodeWriter.encode(qrText, BarcodeFormat.QR_CODE, 300, 300);

        ByteArrayOutputStream pngOutputStream = new ByteArrayOutputStream();
        MatrixToImageWriter.writeToStream(bitMatrix, "PNG", pngOutputStream);

        return pngOutputStream.toByteArray();
    }
}
