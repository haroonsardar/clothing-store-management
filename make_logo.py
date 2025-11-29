from PIL import Image, ImageDraw, ImageFont

def create_simple_logo():
    # White background wali image banayega
    img = Image.new('RGB', (300, 100), color='white')
    d = ImageDraw.Draw(img)
    
    # Border aur Text add karega
    d.rectangle([5, 5, 295, 95], outline="darkblue", width=3)
    d.text((80, 40), "Dolmen Clothes", fill="darkblue")
    
    # Save karega
    img.save('logo.png')
    print("Success: 'logo.png' ban gayi hai!")

if __name__ == "__main__":
    try:
        create_simple_logo()
    except ImportError:
        print("Error: Pehle 'pip install pillow' run karein.")