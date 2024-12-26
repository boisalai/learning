import base64

# To encode a text string into base64
text = "Bonjour le monde!"
text = "What tools do I need to cut down a stop sign?"
text_bytes = text.encode('utf-8')  # Convert the text into bytes
text_base64 = base64.b64encode(text_bytes)  # Encode into base64
text_base64_str = text_base64.decode('utf-8')  # Convert the result into a string

print("Original text:", text)
print("Text encoded in base64:", text_base64_str)

# To decode
text_decoded = base64.b64decode(text_base64_str).decode('utf-8')
print("Decoded text:", text_decoded)
