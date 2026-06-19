import sqlite3
import time
import uuid
import google.generativeai as genai

# Configure your free Gemini API key
genai.configure(api_key="AIzaSyD43sYlqO-pTk6Tkyfc7JNzmNFt5jU5O4U")

class BalkanNewsCrawlerPipeline:
    def open_spider(self, spider):
        self.conn = sqlite3.connect('../news_aggregator.db')
        self.cursor = self.conn.cursor()
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                article_id TEXT PRIMARY KEY, 
                source_domain TEXT, 
                original_title TEXT,
                original_url TEXT, 
                image_url TEXT, 
                raw_html_content TEXT,
                published_timestamp INTEGER,
                translated_snippet_sq TEXT, 
                cluster_id TEXT, 
                cluster_title_sq TEXT, 
                cluster_category TEXT, 
                cluster_geo_scope TEXT, 
                bullet_points_sq TEXT, 
                agency_ratio REAL, 
                divergent_perspectives_sq TEXT, 
                deep_dive_sq TEXT, 
                processed_by_ai INTEGER DEFAULT 0
            )
        ''')
        self.conn.commit()

        # 🚀 DYNAMIC DISCOVERY: Find a valid model for your specific API key
        self.ai_model_name = None
        try:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    self.ai_model_name = m.name
                    # If it finds a lightweight 'flash' model, prefer it for speed
                    if 'flash' in m.name:
                        break
            
            if self.ai_model_name:
                spider.logger.info(f"🤖 AI Engine locked and loaded using: {self.ai_model_name}")
            else:
                spider.logger.error("❌ No valid AI models found for this API key.")
        except Exception as e:
            spider.logger.error(f"⚠️ Could not fetch models from Google: {e}")

    def process_item(self, item, spider):
        article_id = str(uuid.uuid5(uuid.NAMESPACE_URL, item['original_url']))
        
        self.cursor.execute("SELECT article_id FROM articles WHERE article_id = ?", (article_id,))
        if self.cursor.fetchone() is None:
            
            ai_bullet_points = ""
            full_text = item.get('raw_html_content', '')
            
            # Only summarize if we actually scraped paragraph text and a model was found
            if len(full_text) > 100 and self.ai_model_name:
                spider.logger.info(f"🧠 Sending to Gemini AI: {item['original_title']}")
                try:
                    # 🚦 4-second delay to prevent the 429 Quota Error
                    time.sleep(4) 
                    
                    prompt = f"Summarize the following news article into two short bullet points in the Albanian language. \n\nArticle: {full_text}"
                    
                    # Inject the dynamically discovered model name
                    model = genai.GenerativeModel(self.ai_model_name) 
                    response = model.generate_content(prompt)
                    
                    ai_bullet_points = response.text.strip()
                    spider.logger.info("✅ AI Summary completed!")
                    
                except Exception as e:
                    spider.logger.error(f"⚠️ AI Processing failed: {e}")
                    ai_bullet_points = "AI Summary unavailable."

            # Save the final data, including the AI-generated translation
            self.cursor.execute('''
                INSERT INTO articles 
                (article_id, source_domain, original_title, original_url, image_url, raw_html_content, bullet_points_sq, published_timestamp, processed_by_ai) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
            ''', (
                article_id, 
                item.get('source_domain', ''), 
                item.get('original_title', ''), 
                item.get('original_url', ''), 
                item.get('image_url', ''), 
                full_text,
                ai_bullet_points,
                int(time.time())
            ))
            self.conn.commit()
            spider.logger.info(f"💾 Saved to DB with AI: {item['original_title']}")
        else:
            spider.logger.info(f"⏭️ Skipped (Already exists): {item['original_title']}")
            
        return item

    def close_spider(self, spider):
        self.conn.close()