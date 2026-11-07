import os
import time
import schedule
from supabase import create_client, Client
import google.generativeai as genai

# جلب المفاتيح السرية من إعدادات السيرفر (Render)
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

def update_prices():
    print("Agent is asking Gemini for prices...")
    prompt = "أنت خبير اقتصادي بالسوق السورية. أعطني السعر العادل بالدولار لمنتج 'سلة غذائية' كرقم فقط (مثال: 45.50) بدون أي كلمات أخرى."
    
    try:
        response = model.generate_content(prompt)
        new_price = float(response.text.strip())
        print(f"New Price is: ${new_price}")
        
        # تحديث السعر في قاعدة البيانات
        supabase.table('products').update({'price': new_price}).ilike('title', '%سلة%').execute()
        print("Database Updated Successfully!")
    except Exception as e:
        print(f"Error: {e}")

# جدولتها لتعمل كل 12 ساعة
schedule.every(12).hours.do(update_prices)

if __name__ == "__main__":
    print("Sanad Agent Started on Render 24/7...")
    update_prices() # تشغيل فوري أول مرة
    
    while True:
        schedule.run_pending()
        time.sleep(60)
