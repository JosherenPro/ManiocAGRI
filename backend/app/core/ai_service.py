import google.generativeai as genai
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from core.config import settings

# Configure Gemini
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)

async def chat_with_gemini(prompt: str, history: list = None):
    if not settings.GEMINI_API_KEY:
        return "L'IA est actuellement désactivée (Clé API manquante)."
    
    try:
        # gemini-2.0-flash is the current free-tier model
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # System Instruction Context
        context = "Tu es l'assistant intelligent de ManiocAgri, une plateforme agricole au Togo. Tu aides les utilisateurs (producteurs, clients, admins) sur des sujets comme le prix du manioc, les livraisons, et l'utilisation de la plateforme. Réponds de manière concise et professionnelle en français."
        
        full_prompt = f"{context}\n\nUtilisateur: {prompt}"
        
        response = model.generate_content(full_prompt)
        
        if response.candidates:
            return response.text
        else:
            return "Désolé, je n'ai pas pu générer de réponse. Le contenu a peut-être été filtré."
            
    except Exception as e:
        error_msg = str(e).lower()
        print(f"Gemini API Error: {str(e)}")
        
        # Handle common errors with user-friendly messages
        if "429" in str(e) or "quota" in error_msg or "rate" in error_msg:
            return "🔄 L'assistant est temporairement indisponible en raison d'un trop grand nombre de requêtes. Veuillez réessayer dans quelques instants."
        elif "401" in str(e) or "403" in str(e) or "api key" in error_msg or "invalid" in error_msg:
            return "🔑 Configuration de l'assistant en cours. Veuillez contacter l'administrateur."
        elif "404" in str(e) or "not found" in error_msg:
            return "⚙️ L'assistant est en maintenance. Veuillez réessayer plus tard."
        elif "timeout" in error_msg or "connection" in error_msg:
            return "📡 Problème de connexion avec l'assistant. Vérifiez votre connexion internet et réessayez."
        elif "blocked" in error_msg or "safety" in error_msg or "filtered" in error_msg:
            return "⚠️ Je ne peux pas répondre à cette question. Veuillez reformuler votre demande."
        else:
            return "😔 Désolé, une erreur s'est produite. Veuillez réessayer dans quelques instants."

class DemandPredictor:
    @staticmethod
    def predict(order_data: list):
        """
        Prédiction de la demande basée sur l'historique des commandes.
        order_data: liste d'objets avec {created_at, total_price}
        """
        if len(order_data) < 5:
            return {"forecast": [], "msg": "Pas assez de données pour une prédiction fiable."}
            
        df = pd.DataFrame(order_data)
        df['created_at'] = pd.to_datetime(df['created_at'])
        # Normaliser à minuit pour aggréger par jour
        df['date'] = df['created_at'].dt.normalize()
        
        # Aggrégation par jour
        daily_sales = df.groupby('date').size().reset_index(name='count')
        
        if len(daily_sales) < 2:
            return {"forecast": [], "msg": "Données historiques sur une seule journée. Prédiction impossible."}

        # Conversion des dates en nombres de jours depuis le début
        start_date = daily_sales['date'].min()
        daily_sales['day_num'] = (daily_sales['date'] - start_date).dt.days
        
        # Modèle de régression linéaire simple pour la tendance
        X = daily_sales[['day_num']].values
        y = daily_sales['count'].values
        
        reg_model = LinearRegression()
        reg_model.fit(X, y)
        
        # Prédiction pour les 7 prochains jours
        last_day = daily_sales['day_num'].max()
        future_days = np.array([[last_day + i] for i in range(1, 8)])
        predictions = reg_model.predict(future_days)
        
        forecast = []
        for i, pred in enumerate(predictions):
            future_date = start_date + timedelta(days=int(last_day + i + 1))
            forecast.append({
                "date": future_date.strftime("%Y-%m-%d"),
                "predicted_orders": max(0, int(round(pred)))
            })
            
        return forecast
