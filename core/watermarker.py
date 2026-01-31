import cv2
import numpy as np
import pywt

class Watermarker:
    def __init__(self):
        self.wavelet = 'haar'
        self.scale = 0.1  # Embedding strength

    def _embed_block(self, block, bit):
        # Apply DCT to the block
        dct_block = cv2.dct(block.astype(np.float32))
        
        # Embed in mid-frequency (e.g., pos 3,3 in 4x4 or 8x8)
        # We'll use a simple strategy: Modify (3,3) > (4,4) for 1, else 0
        # Robustness comes from differential encoding
        v1 = dct_block[3, 3]
        v2 = dct_block[4, 4]
        
        if bit == 1:
            if v1 <= v2:
                diff = v2 - v1 + self.scale
                dct_block[3, 3] = v1 + diff/2
                dct_block[4, 4] = v2 - diff/2
        else:
            if v1 >= v2:
                diff = v1 - v2 + self.scale
                dct_block[3, 3] = v1 - diff/2
                dct_block[4, 4] = v2 + diff/2
                
        return cv2.idct(dct_block)

    def embed(self, image_bytes, text_payload):
        # 1. Payload
        # Max 4 chars -> 32 bits. 
        if len(text_payload) > 4: text_payload = text_payload[:4]
        text_payload = text_payload.ljust(4)
        
        bits = []
        for char in text_payload:
            # Convert char to 8 bits
            b = bin(ord(char))[2:].zfill(8)
            bits.extend([int(x) for x in b])
        
        # 2. Load Image
        nparr = np.frombuffer(image_bytes, np.uint8)
        bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        h, w = bgr.shape[:2]
        
        # Work on Blue channel YCrCb conversion is better but Blue is fine for demo
        # Let's use Y channel from YCrCb for invisibility
        ycrcb = cv2.cvtColor(bgr, cv2.COLOR_BGR2YCrCb)
        y, cr, cb = cv2.split(ycrcb)
        
        y_float = y.astype(np.float32) / 255.0
        
        # DWT
        coeffs = pywt.dwt2(y_float, self.wavelet)
        LL, (LH, HL, HH) = coeffs
        
        # Embed in LL? No, LL is visible. Embed in HH (high freq) -> invisible
        # But HH is fragile. LH/HL is better balance. Let's use LH.
        # We need 32 bits. We can scatter them.
        # Simple grid embedding in LH
        
        lh_h, lh_w = LH.shape
        # We need 32 slots. 
        # Divide LH into 8x8 blocks?
        
        # Simplified: Just add a pseudo-random sequence scaled by bits directly into LH
        # This is "spread spectrum".
        # Let's stick to the block DCT idea but on the DWT coeffs? 
        # Actually, simpler: Just add small +delta to specific pixels in LH based on bit
        
        np.random.seed(42) # Fixed seed for synthid-like consistency
        
        # Flatten LH to embed bits distributedly
        flat_indices = np.arange(LH.size)
        np.random.shuffle(flat_indices)
        
        # Use 1000 pixels per bit for robustness (Spread Spectrum)
        pixels_per_bit = min(LH.size // 32, 1000)
        
        LH_mod = LH.copy()
        
        for i, bit in enumerate(bits):
            idx_start = i * pixels_per_bit
            idx_end = (i + 1) * pixels_per_bit
            indices = flat_indices[idx_start:idx_end]
            
            # Simple additive watermark
            rows = indices // lh_w
            cols = indices % lh_w
            
            sign = 1 if bit == 1 else -1
            LH_mod[rows, cols] += sign * self.scale
            
        # IDWT
        coeffs_mod = (LL, (LH_mod, HL, HH))
        y_mod = pywt.idwt2(coeffs_mod, self.wavelet)
        
        # Crop to original size (IDWT might expand slightly)
        y_mod = y_mod[:h, :w]
        
        y_mod_uint8 = np.clip(y_mod * 255.0, 0, 255).astype(np.uint8)
        
        ycrcb_mod = cv2.merge([y_mod_uint8, cr, cb])
        bgr_mod = cv2.cvtColor(ycrcb_mod, cv2.COLOR_YCrCb2BGR)
        
        return bgr_mod

    def decode(self, image_bytes):
        nparr = np.frombuffer(image_bytes, np.uint8)
        bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        ycrcb = cv2.cvtColor(bgr, cv2.COLOR_BGR2YCrCb)
        y, _, _ = cv2.split(ycrcb)
        y_float = y.astype(np.float32) / 255.0
        
        coeffs = pywt.dwt2(y_float, self.wavelet)
        _, (LH, _, _) = coeffs
        
        lh_h, lh_w = LH.shape
        np.random.seed(42)
        flat_indices = np.arange(LH.size)
        np.random.shuffle(flat_indices)
        pixels_per_bit = min(LH.size // 32, 1000)
        
        detected_bits = []
        for i in range(32):
            idx_start = i * pixels_per_bit
            idx_end = (i + 1) * pixels_per_bit
            indices = flat_indices[idx_start:idx_end]
            
            rows = indices // lh_w
            cols = indices % lh_w
            
            # Correlation
            val = np.sum(LH[rows, cols])
            detected_bits.append(1 if val > 0 else 0)
            
        # Bits to chars
        chars = []
        for i in range(0, 32, 8):
            byte_bits = detected_bits[i:i+8]
            byte_str = "".join(str(b) for b in byte_bits)
            chars.append(chr(int(byte_str, 2)))
            
        return "".join(chars).strip()
