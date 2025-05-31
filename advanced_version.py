import requests
from PIL import Image
from io import BytesIO
import time
import os

# Your Hugging Face API key


# Stable Diffusion API endpoint
API_URL = os.getenv("API_URL")


headers = {"Authorization": f"Bearer {os.getenv('API_KEY')}"}

def generate_notification_card(title, body, style="modern"):
    """
    Generate high-quality notification cards with crystal clear text
    Focus on the 3 best-performing styles: modern, festive, premium
    """
    
    # Enhanced prompts with explicit text clarity instructions
    prompts = {
        "modern": f"""
            Ultra-high quality mobile notification card design, professional UI interface,
            clean white background with subtle shadow, rounded corners,
            left side: bright blue circular app icon (#2196F3),
            right side text layout with perfect typography:
            TITLE (bold, 18px, black): "{title}"
            BODY (regular, 14px, dark gray): "{body}"
            
            Design requirements: iOS/Android notification style, crystal clear text rendering,
            sharp typography, perfect font smoothing, no text blur, high resolution,
            minimal clean design, proper text contrast, readable fonts,
            professional mobile interface, pristine text quality
        """,
        
        "festive": f"""
            Premium festive notification card design, holiday celebration theme,
            warm gradient background (gold to cream), elegant rounded card,
            left: colorful festive app icon with holiday symbols,
            typography with crystal clear text rendering:
            TITLE (bold, holiday green): "{title}"
            BODY (warm gold color): "{body}"
            
            Visual elements: subtle holiday sparkles, warm lighting, premium design,
            ultra-sharp text, no blurry text, perfect font rendering,
            celebration aesthetic, high-quality typography, readable fonts,
            festive but professional, crystal clear lettering
        """,
        
        "premium": f"""
            Luxury premium notification design, high-end mobile interface,
            elegant gradient background (deep blue to navy), sophisticated styling,
            left: premium app icon with metallic finish,
            flawless typography layout:
            TITLE (bold, white/silver): "{title}"
            BODY (light gray, premium font): "{body}"
            
            Design style: luxury mobile app interface, crystal clear text,
            perfect font antialiasing, ultra-sharp typography, no text blur,
            premium materials design, high contrast text, readable fonts,
            sophisticated color palette, executive level quality
        """
    }
    
    prompt = prompts.get(style, prompts["modern"])
    
    # Optimized parameters for text clarity
    payload = {
        "inputs": prompt,
        "parameters": {
            "width": 1072,
            "height": 528,
            "num_inference_steps": 35,    # Increased for better quality
            "guidance_scale": 8.5,        # Higher guidance for prompt adherence
            "negative_prompt": "blurry text, pixelated text, unreadable text, distorted typography, low resolution, bad font rendering, text artifacts, fuzzy letters, poor text quality, illegible text, smudged text, unclear text, text noise"
        }
    }
    
    print(f"🎨 Generating {style.upper()} notification with crystal clear text...")
    print(f"   📝 Title: {title}")
    print(f"   💬 Body: {body[:50]}...")
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        
        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))
            
            # Create descriptive filename
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '_')).strip()
            timestamp = str(int(time.time()))[-4:]  # Last 4 digits of timestamp
            filename = f"notification_{style}_{safe_title[:15].replace(' ', '_')}_{timestamp}.png"
            
            # Save high-quality image
            image.save(filename, "PNG", optimize=False, quality=100)
            print(f"   ✅ SUCCESS: {filename}")
            print(f"   📐 Size: {image.size[0]}x{image.size[1]} pixels")
            
            return image, filename
            
        elif response.status_code == 503:
            print("   ⏳ Model loading... waiting 25 seconds")
            time.sleep(25)
            return generate_notification_card(title, body, style)
            
        else:
            print(f"   ❌ Error {response.status_code}: {response.text}")
            return None, None
            
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        return None, None

def generate_all_best_styles():
    """Generate notifications using the 3 best-performing styles"""
    
    # Premium notification examples - optimized for text clarity
    notifications = [
        {
            "title": "💳 Card Status Alert",
            "body": "Your EMI card is temporarily blocked. Tap to unblock instantly!"
        },
        {
            "title": "🎉 Festive Cashback!",
            "body": "₹5,000 bonus credited to your account. Happy festivities!"
        },
        {
            "title": "⚡ Payment Confirmed",
            "body": "₹2,500 payment successful. Transaction ID: PAY2024156789"
        },
        {
            "title": "🎊 Special Offer Live",
            "body": "20% extra cashback on all purchases this weekend only!"
        },
        {
            "title": "🔔 Security Update",
            "body": "New device login from Mumbai. Please verify if this was you."
        }
    ]
    
    # Only the 3 best styles
    styles = ["modern", "festive", "premium"]
    
    print("🚀 PREMIUM NOTIFICATION GENERATOR")
    print("=" * 50)
    print("Generating with 3 best-performing styles for maximum text clarity")
    print()
    
    total_generated = 0
    results = {}
    
    for i, notif in enumerate(notifications, 1):
        print(f"📱 NOTIFICATION {i}/{len(notifications)}")
        print(f"Title: {notif['title']}")
        print(f"Body: {notif['body']}")
        print("-" * 40)
        
        notification_results = {}
        
        for style in styles:
            print(f"\n🎨 Generating {style.upper()} style...")
            
            image, filename = generate_notification_card(
                notif['title'], 
                notif['body'], 
                style
            )
            
            if image and filename:
                notification_results[style] = {
                    "image": image,
                    "filename": filename,
                    "status": "success"
                }
                total_generated += 1
                print(f"   🎯 {style} style: SUCCESS")
            else:
                notification_results[style] = {
                    "status": "failed"
                }
                print(f"   ❌ {style} style: FAILED")
            
            # Delay between requests to avoid rate limiting
            time.sleep(6)
        
        results[f"notification_{i}"] = notification_results
        print(f"\n✅ Notification {i} complete")
        print("=" * 50)
    
    # Summary report
    print(f"\n🎯 GENERATION SUMMARY")
    print(f"Total images generated: {total_generated}/{len(notifications) * len(styles)}")
    print(f"Success rate: {(total_generated/(len(notifications) * len(styles)))*100:.1f}%")
    
    # List all generated files
    png_files = [f for f in os.listdir('.') if f.startswith('notification_') and f.endswith('.png')]
    recent_files = sorted([f for f in png_files if 'modern' in f or 'festive' in f or 'premium' in f], 
                         key=lambda x: os.path.getctime(x), reverse=True)[:10]
    
    if recent_files:
        print(f"\n📁 Latest Generated Files:")
        for f in recent_files:
            print(f"   • {f}")
    
    return results

def generate_custom_notification():
    """Create a single custom notification in all 3 best styles"""
    
    print("\n🎨 CUSTOM NOTIFICATION CREATOR")
    print("=" * 35)
    
    try:
        title = input("📝 Enter notification title: ").strip()
        if not title:
            title = "📱 Default Notification"
        
        body = input("💬 Enter notification body: ").strip()
        if not body:
            body = "This is a sample notification message for testing."
        
        print(f"\n🎯 Creating custom notification with crystal clear text...")
        print(f"Title: {title}")
        print(f"Body: {body}")
        print()
        
        styles = ["modern", "festive", "premium"]
        custom_results = {}
        
        for style in styles:
            print(f"🎨 Generating {style.upper()} version...")
            
            image, filename = generate_notification_card(title, body, style)
            
            if image and filename:
                custom_results[style] = filename
                print(f"   ✅ {style}: {filename}")
            else:
                print(f"   ❌ {style}: Failed to generate")
            
            time.sleep(6)
        
        print(f"\n🎉 Custom notification complete!")
        print(f"Generated {len(custom_results)}/3 styles successfully")
        
        return custom_results
        
    except KeyboardInterrupt:
        print("\n👋 Custom notification cancelled")
        return {}
    except Exception as e:
        print(f"❌ Error in custom creation: {e}")
        return {}

def main():
    print("🌟 PREMIUM NOTIFICATION GENERATOR")
    print("=" * 50)
    print("✨ Featuring the 3 best styles with crystal clear text")
    print("🎨 Styles: Modern | Festive | Premium")
    print("🎯 Optimized for maximum text clarity and readability")
    print()
    
    print("Choose generation mode:")
    print("3. Generate custom notification (all 3 styles)")
    print("4. Generate complete notification suite (5 notifications × 3 styles)")
    
    try:
        choice = input("\nEnter choice (3 or 4): ").strip()
    except:
        choice = "4"
    
    if choice == "3":
        generate_custom_notification()
    else:
        # Default: generate complete suite
        generate_all_best_styles()
    
    print("\n🎉 GENERATION COMPLETE!")
    print("💡 Tips for best results:")
    print("   • Keep titles under 50 characters")
    print("   • Use clear, concise body text")
    print("   • Include relevant emojis for visual appeal")
    print("   • Check generated images for text clarity")

if __name__ == "__main__":
    main()